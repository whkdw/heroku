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

import json
import datetime

from typing import List, Dict, Tuple
from urllib.parse import quote

try:
    GYM_PASSWORD = os.environ['GYM_PASSWORD']
    GYM_USERNAME = os.environ['GYM_USERNAME']
except KeyError:
    GYM_PASSWORD = ""
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

fighter_builds = [
    { "STRENGTH": 0.45, "SPEED": 0.33, "AGILITY": 0.22, "CHIN": 19, "HEIGHT": 10, "COUNT": 3 }, # albino
    { "STRENGTH": 0.55, "SPEED": 0.30, "AGILITY": 0.15, "CHIN": 22, "HEIGHT":  7, "COUNT": 1 }, # zam
    { "STRENGTH": 0.46, "SPEED": 0.25, "AGILITY": 0.29, "CHIN": 18, "HEIGHT": 12, "COUNT": 2 }, # agl
    { "STRENGTH": 0.40, "SPEED": 0.29, "AGILITY": 0.31, "CHIN": 17, "HEIGHT": 13, "COUNT": 0 }, # bal
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
):
    url = f"https://webl.vivi.com/cgi-bin/{script}"

    data = {
        **_parse_etc_params(etc),
        "username": GYM_PASSWORD,
        "password": GYM_PASSWORD,
        "block_ad": "1",
        "command": command,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        ),
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    for attempt in range(7):
        time.sleep(2.75 + 15 * attempt)
        try:
            print(command, etc)
            resp = requests.post(url, data=data, headers=headers, timeout=10)
            resp.raise_for_status()
            if "eeeeee" not in resp.text:
                raise requests.RequestException("Invalid WeBL response content")
            return resp.text
        except requests.RequestException as e:
            if attempt == 6:
                print(f"[write_msg] FAILED after 7 attempts:  script={script}, command={command}, etc='{etc}'\n{e}", file=sys.stderr)
    
    return ""


def find_name():
    try:
        response = requests.get("https://en.wikipedia.org/wiki/Special:RandomInCategory/Category:Living_people", headers={"User-Agent": "Mozilla/5.0 (compatible; FantasyNameBot/1.0)"}, timeout=10)
        response.raise_for_status()
        return random.choice(['Byl', 'Ell', 'Fel', 'Kel', 'Kul']) + "'" + re.search(r"<title>\s*([\w]+)", unicodedata.normalize("NFKD", response.text).encode("ascii", "ignore").decode("ascii", "ignore"), flags=re.IGNORECASE).group(1).lower()
    except:
        return ""


def compute_weight(hgtval: int, strval: int, aglval: int, cndval: int, bldval: int) -> Tuple[int, int]:
    wgtval = round((hgtval + 60.0) ** 3.0 * (0.0005 + bldval * 0.00001) *
        (1.0 + (math.sqrt(strval - 10.0) if (strval > 10) else -math.sqrt(10.0 - strval)) * 0.05) *
        (1.0 - (math.sqrt(aglval - 10.0) if (aglval > 10) else -math.sqrt(10.0 - aglval)) * 0.05) - 0.49999)
    return wgtval, round(wgtval * (0.995 - cndval * 0.0025))


# ------------------------------
# Main
# ------------------------------

if __name__ == "__main__":
    #print(requests.get("https://ipinfo.io/json", timeout=5).json())

    week = int(time.strftime("%W")) * 10000

    try: 
        with open('data.json') as f: ftr = json.load(f)
    except: ftr = {}

    #print(write_msg("eko_select_orders", f"your_team=Byl`phillip&strategy_choice=5H114insideR1")) # 6H122alloutR1 5H87ringR1 5H105insideR1
    print(write_msg("eko_select_orders", f"your_team=Byl`phillip&strategy_choice=5H114ringR1")) # 6H122alloutR1 5H87ringR1 5H105insideR1
    print(write_msg("eko_select_orders", f"your_team=Byl`phillip&strategy_choice=5H114insideR1")) # 6H122alloutR1 5H87ringR1 5H105insideR1
    
    try:
        for word in write_msg("eko_retired_fighters").split("Activate</A>"):
                if "regional_champion" not in word and "challenger.gif" not in word and "champion.gif" not in word:
                    for team_id in re.findall(r"team_id=([0-9]+)", word):
                        write_msg("eko_activate", f"team_id={team_id}")
                        break

        team_ids = sorted(set(re.findall(r"team_id=([0-9]+)", write_msg("eko_all_fighters_brief"))), key=int)
        print(team_ids)

        for team_id in team_ids:
            if team_id not in ftr: ftr[team_id] = {}
            text, rng = write_msg("eko_control_fighter", f"team_id={team_id}"), random.Random(week + int(team_id))


            ftr[team_id]['NAME'] = re.search(r'[\w]>(.*) fights in the <[\w]', text).group(1)
            ftr[team_id]['STRENGTH'] = int(re.search(r'[\w]>[Ss]trength[^0-9]+(\d+)', text).group(1))
            ftr[team_id]['KP'] = int(re.search(r'[\w]>[Kk]nockout[^0-9]+(\d+)', text).group(1))
            ftr[team_id]['SPEED'] = int(re.search(r'[\w]>[Ss]peed[^0-9]+(\d+)', text).group(1))
            ftr[team_id]['AGILITY'] = int(re.search(r'[\w]>[Aa]gility[^0-9]+(\d+)', text).group(1))
            ftr[team_id]['CHIN'] = int(re.search(r'[\w]>[Cc]hin[^0-9]+(\d+)', text).group(1))
            ftr[team_id]['CONDITIONING'] = int(re.search(r'[\w]>[Cc]onditioning[^0-9]+(\d+)', text).group(1))
            ftr[team_id]['CUT'] = cut_str.index(re.search(r'[\w]>[Cc]ut [Rr]esista[^>]+>([HLNaghilmnorw]{1,6})', text).group(1).lower()) + 1
            ftr[team_id]['RATING'] = int(re.search(r'>[Rr]ating[^0-9]+([0-9]+)', text).group(1))
            ftr[team_id]['STATUS'] = int(re.search(r'>[Ss]tatus[^0-9]+([0-9]+)', text).group(1))
            ftr[team_id]['HEIGHT'] = (int(m.group(1)) - 5) * 12 + int("0%s" % m.group(2)) if (m := re.search(r'[\w]>[Hh]eight[^>]+>([4-7]) feet ?([0-9]{0,2})', text)) else 0
            ftr[team_id]['BUILD'] = build_str.index(re.search(r'[\w]>[Bb]uild[^>]+>([a-zA-Z ]+)', text).group(1).lower()) - 3
            ftr[team_id]['WEIGHT'] = compute_weight(ftr[team_id]['HEIGHT'], ftr[team_id]['STRENGTH'], ftr[team_id]['AGILITY'], ftr[team_id]['CONDITIONING'], ftr[team_id]['BUILD'])
            ftr[team_id]['IPS'] = int(re.search(r'>[Ii]njury [Pp]oints<[^0-9]+>(\d+)', text).group(1)) + int(re.search(r'[\w]>[Aa][Pp] [Ll]oss[^0-9]+>(-?\d+)', text).group(1)) * 500
            ftr[team_id]['RECORD'] = [ int("0%s" % i) for i in re.search(r'\(([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+)\/([0-9]+)\)', text).groups() ]
            ftr[team_id]['DIVISION'] = [ i.lower() for i in re.search(r'eko_standings[\w&=+]+division=([\w-]+)[\w&=+]+region=([^&]+)', text).groups() ] + [ divis_str[len([ True for i in max_weights if i < ftr[team_id]['WEIGHT'][1]]) ].lower() ] # find correct weight div


            fgt, fgt_tacs = re.search(r' ([0-9]) feet *([0-9]{0,2})[^>]*team_id=([0-9]+)&describe=[0-9]\">(.*)<[I\/][AM][G>]', text), {}
            if fgt:
                if not ftr[team_id]['OPPONENT'] or int(fgt.group(3)) != ftr[team_id]['OPPONENT'][1]:
                    ftr[team_id]['OPPONENT'] = [ (int("0%s" % fgt.group(1)) - 5) * 12 + int("0%s" % fgt.group(2)), int("0%s" % fgt.group(3)), fgt.group(4)] + [ int("0%s" % i) for i in re.search(r'([0-9]+)-([0-9]+)-[0-9]+ [0-9]+\/[0-9]+\)  from the', text).groups() ]
                if len(ftr[team_id]['OPPONENT']) < 6:
                    for sess in re.findall(r"query_scout.*team_id=([0-9]+)&session=([0-9]+)", write_msg("eko_career_nodesc", f"team_id={ftr[team_id]['OPPONENT'][1]}"))[:5]:
                        fght_text = write_msg("query_scout", f"team_id={sess[0]}&session={sess[1]}")
                        ftr_intro, ftr_order = re.findall(r"<[Pp]>In this corner, standing ([4-7]) feet *[and ]*([0-9]{0,2}).*in at \d+ pound.* win.* loss.* is(?: <font color=green><B>| )(.+)!!", fght_text), 2
                        if len(ftr_intro) > 1:
                            if ftr[team_id]['OPPONENT'][2].strip() == ftr_intro[0][2].strip(): ftr_order = 1
                            elif ftr[team_id]['OPPONENT'][2].strip() == ftr_intro[1][2].strip(): ftr_order = 2
                            elif ftr[team_id]['HEIGHT'] == (int("0%s" % ftr_intro[0][0]) - 5) * 12 + int("0%s" % ftr_intro[0][1]): ftr_order = 1

                            for rnd in re.findall(r"<[Bb][Rr]><[Hh][Rr]> *ROUND *([0-9]+).*[\n](.+)[\n](.+)", fght_text) + []:
                                fgt_tacs.setdefault(int(rnd[0]), []).append(( next((i for i, k in enumerate([ "(inside)", "(clinching)", "(feinting)", "(counter-punching)", "(using the ring)", "(ropes)", "(outside)", "(all out)", "." ]) if k in rnd[ftr_order]), None),
                                    next((i for i, k in enumerate([ "to the body.<", "for the cut.<", "s head hunting.<", "." ]) if k in rnd[ftr_order]), None) ))
                    ftr[team_id]['OPPONENT'].append(fgt_tacs)
            else: ftr[team_id]['OPPONENT'] = None

            ftr[team_id]['TRAINING'] = [stats_str.index(i.strip()) if i.strip() in stats_str else None for i in re.search(r' training <[Bb]>([a-z\s]+)[^<]*<[^<]*[\<Bb\>]*([a-z\s]+)', text).groups()] + [" (intensive) <" in text]
            ftr[team_id]['FIGHTPLAN'] = m.group(1) if (m := re.search(r'> your <[Bb]>(.+)<\/[Bb]> plan.', text)) else None

            ftr[team_id]['GRADE'] = 1.0 / ftr[team_id]['CUT'] * (42.0 * (1.0 - min(ftr[team_id]['IPS'] / (ftr[team_id]['STATUS'] + 1.0) / 38.0, 1.0)) + (10.0 + min(ftr[team_id]['RECORD'][0] + ftr[team_id]['RECORD'][1], 10.0)) * ftr[team_id]['RECORD'][0] / (ftr[team_id]['RECORD'][0] + ftr[team_id]['RECORD'][1] + 0.001) +
                13.0 * ftr[team_id]['RATING'] / 28.0 + 12.0 * min(ftr[team_id]['RECORD'][0], 20.0) / 20.0 + 3.0 * ftr[team_id]['STRENGTH'] / (ftr[team_id]['STRENGTH'] + ftr[team_id]['SPEED'] + ftr[team_id]['AGILITY']) + 2.0 / (ftr[team_id]['KP'] + 1.0))

            baseaps = ftr[team_id]['STRENGTH'] + ftr[team_id]['SPEED'] + ftr[team_id]['AGILITY']
            ftr[team_id]['TYPE'] = min(range(len(fighter_builds)), key=lambda i: (abs(baseaps * fighter_builds[i]['STRENGTH'] - ftr[team_id]['STRENGTH']) + abs(baseaps * fighter_builds[i]['SPEED'] - ftr[team_id]['SPEED']) + abs(baseaps * fighter_builds[i]['AGILITY'] - ftr[team_id]['AGILITY'])))

            print(ftr[team_id])

            if ftr[team_id]['DIVISION'][0] != ftr[team_id]['DIVISION'][2]: # in wrong div
                write_msg("eko_change_division", f"your_team={ftr[team_id]['NAME']}&division={ftr[team_id]['DIVISION'][2]}weight")

            tr = [None, None, (ftr[team_id]['CHIN'] < 11 + ftr[team_id]['STATUS'] // 5 or ftr[team_id]['CONDITIONING'] > 11 or ftr[team_id]['STATUS'] - ftr[team_id]['RATING'] > 2)]
            for i in range(2):
                baseaps = ftr[team_id]['STRENGTH'] + ftr[team_id]['SPEED'] + ftr[team_id]['AGILITY'] + int(tr[0] is not None and 1 <= tr[0] <= 3) # add ap if training str/apd/agl primarily
                if not i and not tr[2] and (ftr[team_id]['RATING'] == 18 or ftr[team_id]['RATING'] == 28 or ftr[team_id]['RATING'] < ftr[team_id]['STATUS']):
                    tr[i] = 1 # float KP if no chance to gain a ap
                elif ftr[team_id]['CONDITIONING'] + int(tr[0] == 5) < 6:
                    tr[i] = 5
                elif ftr[team_id]['CHIN'] < 11 + ftr[team_id]['STATUS'] // 5 or ftr[team_id]['CHIN'] + int(tr[0] == 4) - 10.0 < (fighter_builds[ftr[team_id]['TYPE']]['CHIN'] - 10.0 - ftr[team_id]['HEIGHT'] // 3.5) * ftr[team_id]['STATUS'] / 28.0:
                    tr[i] = 4
                elif ftr[team_id]['AGILITY'] + int(tr[0] == 3) < baseaps * fighter_builds[ftr[team_id]['TYPE']]['AGILITY'] and ftr[team_id]['AGILITY'] - baseaps * fighter_builds[ftr[team_id]['TYPE']]['AGILITY'] <= ftr[team_id]['SPEED'] - baseaps * fighter_builds[ftr[team_id]['TYPE']]['SPEED']:
                    tr[i] = 3
                elif ftr[team_id]['SPEED'] + int(tr[0] == 2) < baseaps * fighter_builds[ftr[team_id]['TYPE']]['SPEED']:
                    tr[i] = 2
                else:
                    tr[i] = 1 # KP insead of str
            if ftr[team_id]['TRAINING'][0] != tr[0] or (ftr[team_id]['TRAINING'][1] and ftr[team_id]['TRAINING'][1] != tr[1]) or ftr[team_id]['TRAINING'][2] != tr[2]:
                write_msg("eko_training", f"your_team={ftr[team_id]['NAME']}&train={train_str[tr[0]]}&train2={train_str[tr[1]]}&intensive={int(tr[2])}")

            if ftr[team_id]['OPPONENT']:
                # choose an fp base list, emulate random picks
                if ftr[team_id]['CHIN'] < 15:
                    choices = ['417clinchR', '5H105alloutR', '5H105insideR', '5H114alloutR', '5H114insideR', '5H87alloutR']
                else:
                    choices = ['417clinchR', '5H105alloutR', '5H105insideR', '5H114alloutR', '5H114insideR', '5H87alloutR', '6H122alloutR']
                fp_base = rng.choice(choices)
                # randomly choose repetition factor influenced by heights
                hfactors = [1,1, (1 if ftr[team_id]['HEIGHT'] > 14 else 3), (1 if ftr[team_id]['HEIGHT'] > 14 else 3), (1 if ftr[team_id]['HEIGHT'] - ftr[team_id]['OPPONENT'][0] >= 0 else 3)]
                rep = rng.choice(hfactors)
                fp = f'{fp_base}{rep}'
                # several PHP special-case branches:
                if rng.randint(0,6) == 0 and (ftr[team_id]['HEIGHT'] - ftr[team_id]['OPPONENT'][0]) >= -3:
                    # uses a strange inline ternary combining strings; we'll pick a realistic fallback
                    fp = rng.choice(['5H87clinchR', '5H105ringR'])
                if ftr[team_id]['WEIGHT'][1] < 200:
                    if rng.randint(0,6) < 5 and (ftr[team_id]['HEIGHT'] - ftr[team_id]['OPPONENT'][0] <= -10 or (ftr[team_id]['RECORD'][1] > 9 and ftr[team_id]['RECORD'][4] / ftr[team_id]['RECORD'][1] < 0.1)):
                        fp = '6H122alloutR' + str(rng.randint(1,3))
                    elif (ftr[team_id]['HEIGHT'] - ftr[team_id]['OPPONENT'][0] >= 0) and rng.randint(0,4) == 0:
                        fp = '5H114insideR1'
                    elif (ftr[team_id]['HEIGHT'] - ftr[team_id]['OPPONENT'][0] >= 0):
                        fp = '5H87ringR1'
                    elif (ftr[team_id]['HEIGHT'] - ftr[team_id]['OPPONENT'][0] >= -3) and rng.randint(0,1) == 1:
                        fp = '5H105insideR1'
                    elif (ftr[team_id]['HEIGHT'] - ftr[team_id]['OPPONENT'][0] >= -3):
                        fp = rng.choice(['5H87', '5H105']) + 'clinchR1'
                if rng.randint(0,9) == 0 and ftr[team_id]['STATUS'] > 18:
                    fp = '6H113alloutR1'
                if ftr[team_id]['CHIN'] > 23:
                    fp = rng.choice(['5H105alloutR', '5H114alloutR', '5H87alloutR', '6H122alloutR' if ftr[team_id]['OPPONENT'][0] > ftr[team_id]['HEIGHT'] else '5H105alloutR']) + str(rng.randint(1,2))

                if len(ftr[team_id]['OPPONENT']) > 5:
                    opptac = [( tuple(round(s.count(i) / (len(s) + 0.0001), 2) for i in range(len(style_str))), tuple(round(t.count(i) / (len(t) + 0.0001), 2) for i in range(4))) for f in ftr[team_id]['OPPONENT'][5].values() for s, t in (( [x[0] for x in f ], [ x[1] for x in f ]),) ]
                    if len(opptac) > 1:
                        if opptac[0][0][7] > 0.9: # always allout
                            fp = rng.choice(['5H87clinchR1', '5H87ringR1'])
                        if opptac[0][0][1] > 0.9 and opptac[0][1][3] > 0.9: # always inside head
                            fp = rng.choice(['5H87clinchR1', '5H87ringR1', '5H105clinchR1', '5H105ringR1', ])
                        elif opptac[0][1][0] > 0.9: # always body round 1
                            if opptac[0][0][0] + opptac[0][0][1] + opptac[0][0][7] > 0.9: # always inside/clinch/allout round 1
                                fp = rng.choice([ '5H105insideR1', '5H114insideR1', '5H87alloutR1', '5H114ringR1' ])
                            else:
                                fp = rng.choice([ ['5H105alloutR', '5H114alloutR', '5H87alloutR', '6H122alloutR' if ftr[team_id]['OPPONENT'][0] - 2 > ftr[team_id]['HEIGHT'] else '5H105alloutR'] ])
                        #elif opptac[0][1][3] > 0.9: # always no target round 1
                        #    fp = rng.choice([ '5H105insideR1', '5H114insideR1', '5H87alloutR1', '5H114ringR1' ])

                if ftr[team_id]['FIGHTPLAN'] != fp:
                    write_msg("eko_select_orders", f"your_team={ftr[team_id]['NAME']}&strategy_choice={fp}")

            if (ftr[team_id]['STATUS'] > 0 and ftr[team_id]['IPS'] / (ftr[team_id]['STATUS'] + 0.01) > 38.0) or (ftr[team_id]['RECORD'][0] == 0 and ftr[team_id]['RECORD'][1] > 1):
                if ftr[team_id]['DIVISION'][1] == "contenders" or ftr[team_id]['STATUS'] > 18:
                    write_msg("eko_retire_byid", f"verify_retire=1&+team_id={team_id}")
                else:
                    write_msg("eko_transfer", f"to_manager=77894&your_team={ftr[team_id]['NAME']}")


        ftr_new = {k: ftr[k] for k in team_ids if k in ftr}


        ftr_by_height = [ { h: 0 for h in range(-2, 21) } for _ in range(len(fighter_builds)) ]
        for f in ftr_new: ftr_by_height[ftr_new[f]['TYPE']][ftr_new[f]['HEIGHT']] += 1

        for type_new, height, value in ( (i, h, v) for i, d in enumerate(ftr_by_height) for h, v in d.items() ):
            while value and ftr_by_height[type_new][height] < fighter_builds[type_new]['COUNT']:
                chin, condition, build = random.randint(12, 13), 6, random.randint(-2, 3)
                strength = round((63 - height - chin - condition + height // 6) * fighter_builds[type_new]['STRENGTH'])
                agility = round((63 - height - chin - condition + height // 6) * fighter_builds[type_new]['AGILITY'])
                ko_punch = strength // 3
                speed = 69 - height - strength - ko_punch - agility - chin - condition
                while compute_weight(height, strength, agility, condition, build)[0] < max_weights[0]: build += 1
                write_msg("eko_create_fighter", f"competition=eko&region=0&team={find_name()}&height={height}&strength={strength}&ko_punch={ko_punch}&speed={speed}&agility={agility}&chin={chin}&condition={condition}&cut=1&build={build}")
                ftr_by_height[type_new][height] += 1


        with open('data.json.tmp', 'w', encoding='utf-8') as f:
            json.dump(ftr_new, f, ensure_ascii=False, indent=4)
        os.replace('data.json.tmp', 'data.json')


    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Error during automation run: {e}", file=sys.stderr)
        raise
