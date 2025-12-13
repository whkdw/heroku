import logging
import logging.handlers
import os

import requests
import random
import re
import unicodedata

import time
import math
import sys

from typing import List, Dict, Tuple
from urllib.parse import quote

try:
    GYM_PASSWORD = os.environ["GYM_PASSWORD"]
    GYM_USERNAME = os.environ["GYM_USERNAME"]
except KeyError:
    GYM_PASSWORD = "bannerlrd"
    GYM_USERNAME = ""


# ------------------------------
# Configuration / Constants
# ------------------------------

max_weights = [ 106, 109, 112, 115, 118, 122, 126, 130, 135, 141, 147, 153, 160, 167, 175, 200, 1000 ]
build_str = [ "very light", "light", "a little light", "normal", "a little heavy", "heavy", "very heavy" ]
divis_str = [ "Straw", "Junior-Fly", "Fly", "Super-Fly", "Bantam", "Super-Bantam", "Feather", "Super-Feather", "Light", "Super-Light", "Welter", "Super-Welter", "Middle", "Super-Middle", "Light-Heavy", "Cruiser", "Heavy" ]
style_str = [ "inside", "clinch", "feint", "counter", "ring", "ropes", "outside", "allout" ]
cut_str = [ "low", "normal", "high" ]

stats_str = [ "strength", "knockout punch", "speed", "agility", "chin", "conditioning" ]
train_str = [ "weights+(STR)", "heavy+bag+(KP)", "speed+bag+(SPD)", "jump+rope+(AGL)", "sparring+(CHN)", "road+work+(CND)" ]

DIVISIONS = [
    "Straw", "Junior-Fly", "Fly", "Super-Fly", "Bantam", "Super-Bantam", "Feather", "Super-Feather",
    "Light", "Super-Light", "Welter", "Super-Welter", "Middle", "Super-Middle", "Light-Heavy", "Cruiser", "Heavy"
]

# day_fps parallels the PHP array (index 0 = Sunday)
DAY_FPS = [
    [DIVISIONS[3], DIVISIONS[4], DIVISIONS[5], DIVISIONS[6], DIVISIONS[7], DIVISIONS[8]],  # sun
    [DIVISIONS[6], DIVISIONS[7], DIVISIONS[8], DIVISIONS[9], DIVISIONS[10], DIVISIONS[11]],  # mon
    [DIVISIONS[9], DIVISIONS[10], DIVISIONS[11], DIVISIONS[12], DIVISIONS[13]],  # tues
    [DIVISIONS[12], DIVISIONS[13], DIVISIONS[14], DIVISIONS[15]],  # weds
    [DIVISIONS[14], DIVISIONS[15], DIVISIONS[16]],  # thurs
    [DIVISIONS[16], DIVISIONS[0], DIVISIONS[1], DIVISIONS[2]],  # fri
    [DIVISIONS[0], DIVISIONS[1], DIVISIONS[2], DIVISIONS[3], DIVISIONS[4], DIVISIONS[5]]  # sat
]


# ------------------------------
# Small helpers
# --------

def _parse_etc_params(etc: str) -> Dict[str, str]:
    """
    Convert a PHP-style query string like:
        "+team_id=123&foo=bar&+x=y"
    into a clean parameter dict.
    """
    params = {}
    if not etc:
        return params

    # Remove ONLY leading "+" from keys (like PHP logic)
    for part in etc.split("&"):
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        key = key.lstrip("+").strip()
        value = value.strip()

        if key:
            params[key] = value

    return params

def write_msg(
    command: str = "",
    etc: str = "",
    script: str = "query.fcgi",
    timeout: int = 10,
    retries: int = 2,
    backoff: float = 0.75,
    return_response_obj: bool = False,
) -> str:
    """
    Python equivalent of the PHP curl wrapper.
    
    Args:
        command: The CGI "command=" param.
        etc: A query-string fragment like "+team_id=12&foo=bar".
        script: CGI script name.
        timeout: Timeout for every request attempt.
        retries: Number of retry attempts on network failure.
        backoff: Added delay before each retry.
        return_response_obj: If True, return the Response object instead of just text.

    Returns:
        Response text (or Response object if return_response_obj=True).
    """
    url = f"https://webl.vivi.com/cgi-bin/{script}"

    # Parse PVC-style param syntax
    params = _parse_etc_params(etc)

    # Append standard params
    params.update({
        "username": GYM_PASSWORD,
        "password": GYM_PASSWORD,
        "block_ad": "1",
        "command": command,
    })

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        ),
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Perform retries with exponential backoff
    for attempt in range(retries + 1):
        delay = backoff * (attempt + 1)
        time.sleep(delay)
        try:
            resp = requests.post(url, data=params, headers=headers, timeout=timeout)
            resp.raise_for_status()

            return resp if return_response_obj else resp.text

        except Exception as e:
            if attempt >= retries:
                print(
                    f"[write_msg] FAILED after {retries+1} attempts — "
                    f"script={script}, command={command}, etc='{etc}'\n"
                    f"Error: {e}\n",
                    file=sys.stderr
                )
                return ""  # Final fail


def find_name():
    """
    Generates a fantasy-style name by combining a prefix with the first word
    from the title of a random Wikipedia page in 'Living people'.
    """
    
    # Configurable prefix pool
    PREFIXES = ["Byl", "Ell", "Fel", "Kel", "Kul"]

    url = "https://en.wikipedia.org/wiki/Special:RandomInCategory/Category:Living_people"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FantasyNameBot/1.0)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        # Fallback if Wikipedia request fails
        return random.choice(PREFIXES) + "'noname"

    html = response.text

    # Normalize to ASCII (like PHP iconv)
    ascii_html = (
        unicodedata.normalize("NFKD", html)
        .encode("ascii", "ignore")
        .decode("ascii", "ignore")
    )

    # Extract first word from <title>
    match = re.search(r"<title>\s*([\w]+)", ascii_html, flags=re.IGNORECASE)
    name_part = match.group(1).lower() if match else "unknown"

    return f"{random.choice(PREFIXES)}'{name_part}"

def convert_height(feet: int, inches: int) -> int:
    """
    The PHP did: return 12 * (intval("0" . $feet) - 5) + intval("0" . $inches);
    So convert similarly.
    """
    try:
        f = int(feet)
    except Exception:
        f = 0
    try:
        i = int(inches)
    except Exception:
        i = 0
    return 12 * (f - 5) + i

def compute_weight(hgtval: int, strval: int, aglval: int, cndval: int, bldval: int) -> Tuple[int, int]:
    """
    Ported from PHP compute_weight().
    Returns (fwgt, cutweight)
    """
    # replicate PHP floating logic carefully
    if isinstance(strval, (str,)) or isinstance(aglval, (str,)) or isinstance(cndval, (str,)):
        try:
            strval = float(strval)
            aglval = float(aglval)
            cndval = float(cndval)
        except Exception:
            strval = float(10)
            aglval = float(10)
            cndval = float(10)
    # compute the complicated formula:
    # sqrt branches: PHP used ($strval > 10 ? sqrt($strval - 10.0) : -sqrt(10.0 - $strval))
    def signed_sqrt_diff(x):
        if x > 10.0:
            return math.sqrt(x - 10.0)
        else:
            return -math.sqrt(10.0 - x)
    fwgt = round((hgtval + 60.0) * (hgtval + 60.0) * (hgtval + 60.0) / 2000.0 *
                 (1.0 + signed_sqrt_diff(strval) * 0.05) *
                 (1.0 - signed_sqrt_diff(aglval) * 0.05) *
                 (1.0 + bldval * 0.02) - 0.49999)
    cutweight = round((1.0 - 0.0025 * (cndval + 2.0)) * fwgt)
    return fwgt, cutweight

def fighter_types() -> List[Dict]:
    """
    Return same fighter types as PHP.
    STRENGTH = (1.0 - SPEED - AGILITY) implicitly in comments; we keep explicit values.
    """
    return [
        {"STRENGTH": 0.45, "SPEED": 0.33, "AGILITY": 0.22, "CHIN": 19, "COUNT": 3},
        {"STRENGTH": 0.55, "SPEED": 0.30, "AGILITY": 0.15, "CHIN": 22, "COUNT": 1},
        {"STRENGTH": 0.46, "SPEED": 0.25, "AGILITY": 0.29, "CHIN": 20, "COUNT": 2},
        {"STRENGTH": 0.38, "SPEED": 0.30, "AGILITY": 0.32, "CHIN": 19, "COUNT": 0},
    ]


# ------------------------------
# Parsing fighter profile HTML
# ------------------------------

def parse_fighter_html(html: str) -> Dict:
    """
    Convert the regex-heavy PHP parsing into Python matches.
    The PHP pattern set is large — we map the important ones.
    """
    data = {}

    # Name
    m = re.search(r"<P>(.*?) fights in the", html, re.DOTALL | re.IGNORECASE)
    data["NAME"] = m.group(1).strip() if m else ""

    # Numeric stats
    def find_int(pattern, default=0):
        mm = re.search(pattern, html, re.IGNORECASE)
        return int(mm.group(1)) if mm and mm.group(1).isdigit() else default

    data["STRENGTH"] = find_int(r"[Dd]>[Ss]trength[^0-9]+(\d+)")
    data["KP"] = find_int(r"[Dd]>[Kk]nockout[^0-9]+(\d+)")
    data["SPEED"] = find_int(r"[Dd]>[Ss]peed[^0-9]+(\d+)")
    data["AGILITY"] = find_int(r"[Dd]>[Aa]gility[^0-9]+(\d+)")
    data["CHIN"] = find_int(r"[Dd]>[Cc]hin[^0-9]+(\d+)")
    data["CONDITIONING"] = find_int(r"[Dd]>[Cc]onditioning[^0-9]+(\d+)")
    # CUT: map "Cut Resistance <...>ight>(word)"
    m = re.search(r"Cut Resistance <[^>]*>([a-zA-Z]+)", html)
    if m:
        try:
            cutval = m.group(1).strip().lower()
            data["CUT"] = next((k for k, v in CUTS_STR.items() if v == cutval), 0)
        except Exception:
            data["CUT"] = 0
    else:
        data["CUT"] = 0

    data["RATING"] = find_int(r"Rating[^0-9]+ight>(\d+)")
    data["STATUS"] = find_int(r"Status[^0-9]+ight>(\d+)")

    # Height: "Height<TD colspan=3>(\d+) feet ?([0-9]{0,2})"
    m = re.search(r"Height<TD colspan=3>(\d+)\s*feet\s*([0-9]{0,2})", html)
    if m:
        data["HEIGHT"] = convert_height(int(m.group(1)), int(m.group(2) or 0))
    else:
        data["HEIGHT"] = 0

    # Build
    m = re.search(r"Build<TD colspan=3>([a-zA-Z ]+)", html)
    if m:
        build_str = m.group(1).strip().lower()
        # reverse mapping: find key in BUILD_STR with matching string
        found = next((k for k, v in BUILD_STR.items() if v.lower() == build_str), 0)
        data["BUILD"] = found
    else:
        data["BUILD"] = 0

    # Weight computed
    data["WEIGHT"] = compute_weight(data["HEIGHT"], data["STRENGTH"], data["AGILITY"], data["CONDITIONING"], data["BUILD"])

    # IPS (Injury Points) and AP Loss stuff approximation; the PHP added AP Loss * 500 if present
    m = re.search(r"Injury Points<[^0-9]+ight>(\d+)", html)
    if m:
        ips = int(m.group(1))
        # try AP Loss
        m2 = re.search(r"AP Loss<[^0-9]+ight>(\d+)", html)
        if m2:
            ap_loss = int(m2.group(1))
            ips += ap_loss * 500
        data["IPS"] = ips
    else:
        data["IPS"] = 0

    # RECORD: multiple patterns
    recs = re.findall(r"([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+)\/([0-9]+)", html)
    data["RECORD"] = recs if recs else None

    # DIVISIONS extraction: eko_standings&competition=eko&division=...&region=...
    m = re.search(r"eko_standings&[+]?competition=eko&[+]?division=([^&]+)&[+]?region=([^&/]+)", html)
    if m:
        div_name = m.group(1)
        region = m.group(2)
        # find division index
        try:
            div_idx = DIVISIONS.index(div_name)
        except ValueError:
            div_idx = 0
        data["DIVISIONS"] = [div_idx, region]
    else:
        data["DIVISIONS"] = None

    # OPPONENT: pattern that contains feet, inches, team_id, and name
    m = re.search(r" ([0-9]) feet *([0-9]{0,2})[^>]*team_id=([0-9]+)&describe=[0-9]\">(.*)<[I\/][AM][G>]", html)
    if m:
        opp_height = convert_height(int(m.group(1)), int(m.group(2) or 0))
        opp_team = int(m.group(3))
        opp_name = m.group(4).strip()
        data["OPPONENT"] = [opp_height, opp_team, opp_name, 0]
    else:
        data["OPPONENT"] = None

    # TRAINING detection pattern used in PHP
    m = re.search(r" training <[Bb]>([\w\s]+)[^<]*<[^<]*[\<Bb\>]*([\w\s]+)", html)
    if m:
        t1 = m.group(1).strip().lower()
        t2 = m.group(2).strip().lower()
        try:
            t1_idx = STATS_STR.index(t1)
        except ValueError:
            t1_idx = None
        try:
            t2_idx = STATS_STR.index(t2)
        except ValueError:
            t2_idx = None
        data["TRAINING"] = [t1_idx, t2_idx, "(intensive)" in html]
    else:
        data["TRAINING"] = None

    # TYPE filled by later matching logic
    data["TYPE"] = 0

    return data

# ------------------------------
# Utility: fetch all fighter ids
# ------------------------------

def get_all_team_ids() -> List[int]:
    text = write_msg("eko_all_fighters_brief", "")
    ids = re.findall(r"team_id=([0-9]+)", text)
    return [int(x) for x in ids]

# ------------------------------
# Automation: process each fighter
# ------------------------------

def process_fighters():
    team_ids = get_all_team_ids()
    types = fighter_types()
    # initialize typesbyheight: list of dictionaries (for each type index)
    typesbyheight = []
    for _ in types:
        # height keys might range 0..??; we'll use dict default 0
        typesbyheight.append({})  # mapping height -> count

    for tid in team_ids:
        text = write_msg("eko_control_fighter", f"+team_id={tid}")
        data = parse_fighter_html(text)

        # Determine fighter TYPE using the PHP approach
        baseaps = data["STRENGTH"] + data["SPEED"] + data["AGILITY"]
        matchdiff = 1e9
        chosen_type = 0
        for i, t in enumerate(types):
            diff = abs(baseaps * (1.0 - t["SPEED"] - t["AGILITY"]) - data["STRENGTH"]) \
                   + abs(baseaps * t["SPEED"] - data["SPEED"]) \
                   + abs(baseaps * t["AGILITY"] - data["AGILITY"])
            if diff < matchdiff:
                matchdiff = diff
                chosen_type = i
        data["TYPE"] = chosen_type

        # Update typesbyheight counts
        hb = data["HEIGHT"]
        typesbyheight[data["TYPE"]][hb] = typesbyheight[data["TYPE"]].get(hb, 0) + 1

        # Retirement logic: PHP: if ($data["STATUS"] > 0 && $data["IPS"] / ($data["STATUS"] + 0.01) > 38.0) retire
        if data.get("STATUS", 0) > 0:
            if data["IPS"] / (data["STATUS"] + 0.01) > 38.0:
                write_msg("eko_retire_byid", f"verify_retire=1&+team_id={tid}")

        # find correct weight division; PHP loop: for ($i = count($divis_str) - 1; $i >= 0 && $data["WEIGHT"][1] <= $max_weights[$i]; $i--)
        # In PHP they used $max_weights with index -1..16; we approximate by scanning division indices descending
        try:
            current_div_idx = data["DIVISIONS"][0] if data.get("DIVISIONS") else None
        except Exception:
            current_div_idx = None
        # find division by comparing cutweight (data["WEIGHT"][1]) to MAX_WEIGHTS
        cutwt = data["WEIGHT"][1]
        found_div = None
        # iterate division indexes descending (16 down to 0)
        for i in range(len(DIVISIONS)-1, -1, -1):
            maxw_for_i = MAX_WEIGHTS.get(i, 1000)  # fallback
            prior_max = MAX_WEIGHTS.get(i-1, -1)
            if cutwt <= maxw_for_i:
                # ensure > previous, similar to PHP: if ($data["WEIGHT"][1] > $max_weights[$i - 1] && $i != $data["DIVISIONS"][0])
                if cutwt > prior_max:
                    found_div = i
                break
        if found_div is not None and current_div_idx is not None and found_div != current_div_idx:
            # request change division
            write_msg("eko_change_division", f"your_team={data['NAME']}&division={DIVISIONS[found_div]}weight")
            if data.get("DIVISIONS"):
                data["DIVISIONS"][0] = found_div

        # Opponent analysis & strategy selection (big chunk ported)
        opptacs = {
            "ROUNDS": 0,
            "STYLES": [0]*10,
            "AIMS": [0]*5,
            "FLASHES": [0]*3,
            "KP": 0
        }
        bouts = []

        # The PHP had an optional large block parsing query_scout with sessions;
        # here we mimic results by scanning / using query_scout results when available.
        if data["OPPONENT"] is not None:
            opp_team_id = data["OPPONENT"][1]
            # gather all session ids for opponent
            scout_html = write_msg("eko_career_nodesc", f"+team_id={opp_team_id}")
            sessions = re.findall(r"query_scout.*team_id=([0-9]+)&session=([0-9]+)", scout_html)
            sessions = [s[1] for s in sessions] if sessions else []
            # For performance, only fetch up to 3 sessions (PHP had break after >1)
            for sess in sessions[:3]:
                q = write_msg("query_scout", f"team_id={opp_team_id}&session={sess}")
                # Attempt to parse the same kinds of stats the PHP did:
                # We'll attempt to extract rounds, styles, aims, landed/throw numbers, endurance hints, etc.
                # Many of these regexes are complex; we'll look for round blocks and lines mentioning "(inside)", "(clinching)", etc.
                # Round-style detection
                round_blocks = re.findall(r"<[Bb][Rr]>(.+?)</[Bb][Rr]>", q, re.DOTALL | re.IGNORECASE)
                # Heuristic parsing:
                me = None
                opponent_in_reports = None
                # Try to recognise opponents by names inside the session
                # We'll keep the parsed round-level data minimal: detect style tokens and aims.
                for rb in round_blocks:
                    # style tokens per PHP:
                    for token, code in [("inside",2), ("clinching",3), ("feinting",4), ("counter-punching",5), ("using the ring",6), ("ropes",7), ("outside",8), ("all out",9)]:
                        if token in rb.lower():
                            opptacs["ROUNDS"] += 1
                            opptacs["STYLES"][code] += 1
                    # aims detection
                    if "goes to the body" in rb:
                        opptacs["AIMS"][1] += 1
                    if "jabs for the cut" in rb:
                        opptacs["AIMS"][2] += 1
                    if "head hunting" in rb or "head-hunting" in rb:
                        opptacs["AIMS"][4] += 1
                    # detect words implying powerpunches / stunning
                    if "stunning" in rb or "knockdown" in rb or "dominating" in rb:
                        opptacs["KP"] += 1  # small heuristic
                bouts.append(rb)
            # short KP/opponent stats based on PHP: count early-round KOs less than round 3
            if scout_html:
                early_kos = re.findall(r"n by \w* in round (\d+)", scout_html)
                for k in early_kos:
                    try:
                        if int(k) < 3 and data["OPPONENT"] is not None:
                            data["OPPONENT"][3] += 1
                    except Exception:
                        pass

            # Choose a strategy pattern (port of many PHP branches)
            # The PHP builds a fp string from heuristics; we'll implement the primary heuristics:
            if data["OPPONENT"] is not None:
                # choose an fp base list, emulate random picks
                if data["CHIN"] < 15:
                    choices = ["417clinchR", "5H105alloutR", "5H105insideR", "5H114alloutR", "5H114insideR", "5H87alloutR"]
                else:
                    choices = ["417clinchR", "5H105alloutR", "5H105insideR", "5H114alloutR", "5H114insideR", "5H87alloutR", "6H122alloutR"]
                fp_base = random.choice(choices)
                # randomly choose repetition factor influenced by heights
                hfactors = [1,1, (1 if data["HEIGHT"] > 14 else 3), (1 if data["HEIGHT"] > 14 else 3), (1 if data["HEIGHT"] - data["OPPONENT"][0] >= 0 else 3)]
                rep = random.choice(hfactors)
                fp = f"{fp_base}{rep}"
                # several PHP special-case branches:
                if random.randint(0,6) == 0 and (data["HEIGHT"] - data["OPPONENT"][0]) >= -3:
                    # uses a strange inline ternary combining strings; we'll pick a realistic fallback
                    fp = random.choice(["5H87clinchR", "5H105ringR"])
                if data["WEIGHT"][1] < 200:
                    if random.randint(0,6) < 5 and ((data["HEIGHT"] - data["OPPONENT"][0] <= -10) or (data.get("RECORD") and int(data["RECORD"][0][1]) > 9 and (int(data["RECORD"][0][4]) / int(data["RECORD"][0][1]) < 0.1 if int(data["RECORD"][0][1]) != 0 else False))):
                        fp = "6H122alloutR" + str(random.randint(1,3))
                    elif (data["HEIGHT"] - data["OPPONENT"][0] >= 0) and random.randint(0,4) == 0:
                        fp = "5H114insideR1"
                    elif (data["HEIGHT"] - data["OPPONENT"][0] >= 0):
                        fp = "5H87ringR1"
                    elif (data["HEIGHT"] - data["OPPONENT"][0] >= -3) and random.randint(0,1) == 1:
                        fp = "5H105insideR1"
                    elif (data["HEIGHT"] - data["OPPONENT"][0] >= -3):
                        fp = random.choice(["5H87", "5H105"]) + "clinchR1"
                if random.randint(0,9) == 0:
                    fp = "6H113alloutR1"
                if data["CHIN"] > 23:
                    fp = random.choice(["5H105alloutR", "5H114alloutR", "5H87alloutR", "6H122alloutR" if data["OPPONENT"][0] > data["HEIGHT"] else "5H105alloutR"]) + str(random.randint(1,2))
                # final write to select orders
                write_msg("eko_select_orders", f"your_team={data['NAME']}&+strategy_choice={fp}")

        # DEBUG prints of data similar to PHP print_r
        print("--- Fighter Info ---")
        print(f"Team ID: {tid}")
        for k, v in data.items():
            print(f"{k}: {v}")
        print("--------------------")

        # Training logic (port of PHP block where $tr decisions are made)
        tr = [0, 0, (1 if (data["CHIN"] < 11 or data["CONDITIONING"] > 11 or data["STATUS"] - data["RATING"] > 1) else 0)]
        # run two passes
        baseaps = data["STRENGTH"] + data["SPEED"] + data["AGILITY"]
        for i in range(2):
            if data["CHIN"] < 9 or (data["CHIN"] < 10 and data["STATUS"] > 20) or (data["KP"] and (data["CHIN"] - 10.0) < round((types[data["TYPE"]]["CHIN"] - 10.0) * data["STATUS"] / 28.0)):
                tr[i] = 4
                data["CHIN"] += 1
            elif data["CONDITIONING"] < 5:
                tr[i] = 5
                data["CONDITIONING"] += 1
            elif data["KP"] and data["KP"] < round((data["STRENGTH"] - 1) / 3.0):
                tr[i] = 1
                data["KP"] += 1
            elif data["WEIGHT"][0] > 299 or (data["WEIGHT"][1] > 102 and data["AGILITY"] < round(baseaps * types[data["TYPE"]]["AGILITY"]) and baseaps * types[data["TYPE"]]["AGILITY"] - data["AGILITY"] > baseaps * types[data["TYPE"]]["SPEED"] - data["SPEED"]):
                tr[i] = 3
                data["AGILITY"] += 1
                baseaps += 1
            elif data["STRENGTH"] < round(baseaps * types[data["TYPE"]]["STRENGTH"]) or data["SPEED"] > 29 or data["WEIGHT"][0] < MAX_WEIGHTS.get(data["DIVISIONS"][0], 0) if data.get("DIVISIONS") else False:
                data["STRENGTH"] += 1
                baseaps += 1
                if data["KP"]:
                    tr[i] = 1
            else:
                tr[i] = 2
                data["SPEED"] += 1
                baseaps += 1

        # The PHP had a special floating kp AI condition; implement equivalent
        if (opptacs.get("KP",0) + opptacs.get("FLASHES",[0])[0]) > (len(bouts) if bouts else 1) / 2.0 and tr[0] != 4 and (data["CHIN"] < 11 or (data["STATUS"] == 18 and (data.get("DIVISIONS") and data["DIVISIONS"][1] != "Contenders")) or data["STATUS"] == 28 or data["RATING"] < data["STATUS"]):
            tr = [4, tr[1], 0]

        # If training selection differs, send eko_training
        training_changed = False
        # PHP checked: if $data["TRAINING"] == null || $data["TRAINING"][0] != $tr[0] || (is_numeric($data["TRAINING"][1]) && $data["TRAINING"][1] != $tr[1]) || ($data["TRAINING"][2] !== false) != $tr[2]
        if data["TRAINING"] is None:
            training_changed = True
        else:
            try:
                if data["TRAINING"][0] != tr[0] or (isinstance(data["TRAINING"][1], int) and data["TRAINING"][1] != tr[1]) or (bool(data["TRAINING"][2]) != bool(tr[2])):
                    training_changed = True
            except Exception:
                training_changed = True

        if training_changed:
            tr0 = TRAIN_STR[tr[0]] if 0 <= tr[0] < len(TRAIN_STR) else TRAIN_STR[0]
            tr1 = TRAIN_STR[tr[1]] if 0 <= tr[1] < len(TRAIN_STR) else TRAIN_STR[0]
            intensive = "&intensive=1" if tr[2] else ""
            write_msg("eko_training", f"your_team={data['NAME']}&train={tr0}&train2={tr1}{intensive}")

    # After all fighters processed, creation of missing fighters (typesbyheight logic)
    # PHP had: foreach($typesbyheight as $key1 => $value1) foreach($value1 as $height => $value2) if ($value2 < fighter_types()[$key1]["COUNT"]) { ... create fighter ... }
    for tindex, height_map in enumerate(typesbyheight):
        required = types[tindex]["COUNT"]
        # iterate heights in a reasonable range (0..30) if height_map lacks keys; PHP used actual recorded heights only.
        heights_to_check = sorted(set(list(height_map.keys()) + list(range(1, 30))))
        for height in heights_to_check:
            count = height_map.get(height, 0)
            if count < required:
                # create fighters until satisfied
                while count < required:
                    chin = random.randint(12, 14)
                    condition = 6
                    strength = round((69 - height - chin - condition) * (1.0 - types[tindex]["SPEED"] - types[tindex]["AGILITY"]))
                    strength -= math.floor(strength / 9.0)
                    ko_punch = math.floor(strength / 3.0)
                    agility = round(max(1, (69 - height - chin - condition - ko_punch) * types[tindex]["AGILITY"]))
                    speed = round(69 - height - strength - ko_punch - agility - chin - condition)
                    team_name = find_name()
                    # build value: mimic PHP: compute_weight(...)[1] < 106 ? 3 : random_int(0,3)
                    cw = compute_weight(height, strength, agility, condition, -3)[1]
                    build_val = 3 if cw < 106 else random.randint(0, 3)
                    # send create request
                    write_msg("eko_create_fighter",
                              f"competition=eko&region=0&team={team_name}&height={height}&strength={strength}&ko_punch={ko_punch}&speed={speed}&agility={agility}&chin={chin}&condition={condition}&cut=1&build={build_val}")
                    print(f"Created fighter: {team_name} height {height} type {tindex}")
                    count += 1
                    # update typesbyheight map to avoid unlimited creation
                    height_map[height] = count

    # debug print typesbyheight
    print("=== typesbyheight summary ===")
    for idx, hm in enumerate(typesbyheight):
        print(f"type {idx}: {hm}")
    print("=============================")


# ------------------------------
# Main
# ------------------------------

if __name__ == "__main__":
    print(requests.get("https://ipinfo.io/json", timeout=5).json())
    # set some global seeds if desired (PHP used mt_rand/random_int)
    random.seed()

    try:
        #process_fighters()
        print("Automation run complete.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Error during automation run: {e}", file=sys.stderr)
        raise


    #print(find_name())
    print(GYM_PASSWORD, GYM_USERNAME)

    #https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=77894
    #to_manager=&77894   your_team=Sunny&    command=eko_transfer
    """for word in write_msg("eko_retired_fighters").split("<H4>Heavyweights")[1].split("Activate</A>"):
        if "regional_champion" not in word and "challenger.gif" not in word and "champion.gif" not in word:
            for team_id in re.findall(r"team_id=([0-9]+)", word):
                print(team_id, write_msg("eko_activate", f"team_id={team_id}", backoff=2))
                break
    """
    
    fighter = """
    <HTML>
    <HEAD>
    <script>
    document.cookie='timezone='+(new Date()).getTimezoneOffset();
    </script>
    <link rel=STYLESHEET type=text/css href=/eko/eko.css>
    <TITLE>WEBL Query Server (control)</TITLE>
</HEAD><BODY bgcolor=#eeeeee>
<center>
<img src="https://webl.vivi.com/images/webltitle.gif" width="200" height="110">
</center>

<BR><CENTER><SMALL>

</SMALL></CENTER>
<HR><BR><B>
<A name="df" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_career_privatebyid&+competition=eko&+division=Heavy&+region=16097&+team_id=544246">df</A> </B> (0-0-0 0/0)<BR>
<table border=1>
<TR><TD>Strength <TD align=right>13<BR>
<TD>Knockout Punch <TD  align=right>0<BR>
<TR><TD>Speed <TD align=right>18<BR>
<TD>Agility <TD align=right>7<BR>
<TR><TD>Chin <TD align=right>9<BR>
<TD>Conditioning <TD align=right>12<BR>
<TR><TD>Cut Resistance <TD align=right>High<BR>
<TD><a target=glossary onClick=help() href=https://cloudfront-webl.vivi.com/eko/glossary.html#streak>Winning Streak</A><TD align=right>0<TR><TD><script language=javascript>
    <!--
    function help() {
	window.open("", "glossary", "width=550,height=300,resizable=1,scrollbars=1");
    }
    //-->
</script>
<a href=https://cloudfront-webl.vivi.com/eko/glossary.html#rating target=glossary onClick=help()>Rating</A><TD align=right>0
<TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#status target=glossary onClick=help()>Status</A><TD align=right>0
<TR><TD><BR><TD><BR>
<TD>Total Earnings:<TD align=right>  $0 <TR><TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#injury target=glossary onClick=help()>Injury Points</A><TD align=right>0
<TD>AP Loss</A><TD align=right>0
<TR><TD>Height<TD colspan=3>6 feet 10 inches (177 centimeters)
<TR><TD>Build<TD colspan=3>light
<TR><TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#fweight target=glossary onClick=help()>Weight</A> <TD colspan=3>202 pounds (91 kilograms)
<TR><TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#minweight target=glossary onClick=help()>Minimum Weight</A> <TD colspan=3>194 pounds (87 kilograms)
</table>
<P>df fights in the <A name="Heavyweight" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_standings&+competition=eko&+division=Heavy&+region=1234567891&team=df">Heavyweight</A> division.  <P>df's next bout is a <B>title fight</B> against the 6 feet 2 inches, 
<A name="sunny" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1695461&describe=1">Sunny</A>  (0-0-0 0/0)  from the 
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=74575">1234567891</A> gym  for   $0  on <B>Sunday, December 14, 2025.</B>
<P>df is training <b>speed</b>, but you can instruct him to <A  HREF="/cgi-bin/prompt.fcgi?+command=eko_training&+competition=eko&+division=Heavy&+region=16097&+team=df">train for something else</A>.<P>df is currently using the <b>Rely on Hand Speed</b> fight plan. 
He may <UL>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_select_orders&+competition=eko&+division=Heavy&+region=16097&+team=df">choose a different fight plan</A>, 
<LI><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_echo&+competition=eko&+division=Heavy&+filename=fightplan_beginner.html&+region=16097&team=df">create a new fight plan</A>  
<LI>or <A  HREF="/cgi-bin/prompt.fcgi?+command=query_edit_orders&+competition=eko&+division=Heavy&+region=16097&+strategy_choice=Rely+on+Hand+Speed&strategy_id=555324">edit</A> your <B>Rely on Hand Speed</B> plan.

<LI>Experts can use the <A  HREF="/cgi-bin/prompt.fcgi?+command=query_orders&+competition=eko&+division=Heavy&+region=16097&+team=df">advanced fight plan form</A>.

<LI>Beginners might want to get into the ring with a  <A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_echo&+competition=eko&+division=Heavy&+filename=newbie_form.html&+region=16097&cname=df&fighter_name=df&team_id=544246">sparring partner.</A>

</UL>
<P>df may also do any of the following:<UL>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=query_press&+competition=eko&+division=Heavy&+region=16097&+team=df&team_id=544246">issue a press release.</A> 
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_change_division&+competition=eko&+division=Heavy&+region=16097&+team=df">change weight division.</A>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_rename&+competition=eko&+division=Heavy&+region=16097&+team=df">change his description.</A>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_retire_byid&+competition=eko&+division=Heavy&+region=16097&+team_id=544246">retire.</A></UL>

</BODY></HTML>

"""

    text = fighter

    ftr = {}

    ftr["NAME"] = quote(re.search(r'[\w]>(.*) fights in the <[\w]', text).group(1))
    ftr["STRENGTH"] = int(re.search(r'[\w]>[Ss]trength[^0-9]+(\d+)', text).group(1))
    ftr["KP"] = int(re.search(r'[\w]>[Kk]nockout[^0-9]+(\d+)', text).group(1))
    ftr["SPEED"] = int(re.search(r'[\w]>[Ss]peed[^0-9]+(\d+)', text).group(1))
    ftr["AGILITY"] = int(re.search(r'[\w]>[Aa]gility[^0-9]+(\d+)', text).group(1))
    ftr["CHIN"] = int(re.search(r'[\w]>[Cc]hin[^0-9]+(\d+)', text).group(1))
    ftr["CONDITIONING"] = int(re.search(r'[\w]>[Cc]onditioning[^0-9]+(\d+)', text).group(1))
    ftr["CUT"] = cut_str.index(re.search(r'[\w]>[Cc]ut [Rr]esista[^>]+>([HLNaghilmnorw]{1,6})', text).group(1).lower()) + 1
    ftr["RATING"] = int(re.search(r'>[Rr]ating[^0-9]+([0-9]+)', text).group(1))
    ftr["STATUS"] = int(re.search(r'>[Ss]tatus[^0-9]+([0-9]+)', text).group(1))
    ftr["HEIGHT"] = (int(m.group(1)) - 5) * 12 + int("0%s" % m.group(2)) if (m := re.search(r'[\w]>[Hh]eight[^>]+>([4-7]) feet ?([0-9]{0,2})', text)) else 0
    ftr["BUILD"] = build_str.index(re.search(r'[\w]>[Bb]uild[^>]+>([a-zA-Z ]+)', text).group(1).lower()) - 3
    ftr["IPS"] = int(re.search(r'>[Ii]njury [Pp]oints<[^0-9]+>(\d+)', text).group(1)) + int(re.search(r'[\w]>[Aa][Pp] [Ll]oss[^0-9]+>(-?\d+)', text).group(1)) * 500
    ftr["RECORD"] = [int("0%s" % i) for i in re.search(r'\(([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+)\/([0-9]+)\)', text).groups()]
    ftr["DIVISIONS"] = [i.lower() for i in re.search(r'eko_standings[\w&=+]+division=([\w-]+)[\w&=+]+region=([^&]+)', text).groups()]
    ftr["WEIGHT"] = round((ftr["HEIGHT"] + 60.0) ** 3.0 * (0.00001 * ftr["BUILD"] + 0.0005) *
        (1.0 + (math.sqrt(ftr["STRENGTH"] - 10.0) if (ftr["STRENGTH"] > 10) else -math.sqrt(10.0 - ftr["STRENGTH"])) * 0.05) *
        (1.0 - (math.sqrt(ftr["AGILITY"] - 10.0) if (ftr["AGILITY"] > 10) else -math.sqrt(10.0 - ftr["AGILITY"])) * 0.05) - 0.49999)
    ftr["MINIMUMWEIGHT"] = round(ftr["WEIGHT"] * (0.995 - 0.0025 * ftr["CONDITIONING"]))

    ftr["OPPONENT"] = re.search(r' ([0-9]) feet *([0-9]{0,2})[^>]*team_id=([0-9]+)&describe=[0-9]\">(.*)<[I\/][AM][G>]', text)
    if ftr["OPPONENT"]: ftr["OPPONENT"] = ((int("0%s" % ftr["OPPONENT"].group(1)) - 5) * 12 + int("0%s" % ftr["OPPONENT"].group(2)), int("0%s" % ftr["OPPONENT"].group(3)), ftr["OPPONENT"].group(4))

    ftr["DIVISIONS"].insert(3, divis_str[len([ True for i in max_weights if i < ftr["MINIMUMWEIGHT"]]) ].lower()) # find correct weight div
    if ftr["DIVISIONS"][0] != ftr["DIVISIONS"][2]: # in wrong div, make change
        print(team_id, write_msg("eko_change_division", f"to_manager=77894&your_team={ftr["NAME"]}&+division={ftr["DIVISIONS"][2]}weight", backoff=2))

    ftr["TRAINING"] = [stats_str.index(i.strip()) if i.strip() in stats_str else None for i in re.search(r' training <[Bb]>([a-z\s]+)[^<]*<[^<]*[\<Bb\>]*([a-z\s]+)', text).groups()] + [" (intensive) <" in text]

    ftr["GRADE"] = 1.0 / ftr["CUT"] * (42.0 * (1.0 - min(ftr["IPS"] / (ftr["STATUS"] + 1.0) / 38.0, 1.0)) + (10.0 + min(ftr["RECORD"][0] + ftr["RECORD"][1], 10.0)) * ftr["RECORD"][0] / (ftr["RECORD"][0] + ftr["RECORD"][1] + 0.001) +
        13.0 * ftr["RATING"] / 28.0 + 12.0 * min(ftr["RECORD"][0], 20.0) / 20.0 + 3.0 * ftr["STRENGTH"] / (ftr["STRENGTH"] + ftr["SPEED"] + ftr["AGILITY"]) + 2.0 / (ftr["KP"] + 1.0))

    types = [
        {"STRENGTH": 0.45, "SPEED": 0.33, "AGILITY": 0.22, "CHIN": 19, "COUNT": 3},
        {"STRENGTH": 0.55, "SPEED": 0.30, "AGILITY": 0.15, "CHIN": 22, "COUNT": 1},
        {"STRENGTH": 0.46, "SPEED": 0.25, "AGILITY": 0.29, "CHIN": 20, "COUNT": 2},
        {"STRENGTH": 0.38, "SPEED": 0.30, "AGILITY": 0.32, "CHIN": 19, "COUNT": 0},
    ]
    baseaps = ftr["STRENGTH"] + ftr["SPEED"] + ftr["AGILITY"]
    ftr["TYPE"] = min(range(len(types)), key=lambda i: (abs(baseaps * types[i]["STRENGTH"] - ftr["STRENGTH"]) + abs(baseaps * types[i]["SPEED"]    - ftr["SPEED"]) + abs(baseaps * types[i]["AGILITY"]  - ftr["AGILITY"])))

    if ftr["STATUS"] > 0 and ftr["IPS"] / (ftr["STATUS"] + 0.01) > 38.0:
        print(team_id, write_msg("eko_transfer", f"to_manager=77894&your_team={ftr["NAME"]}", backoff=2))




    print(ftr)
    print(team_id, write_msg("eko_transfer", f"to_manager=233330&your_team=Val`szam", backoff=2))

    #git add . && git commit -m "update" && git push