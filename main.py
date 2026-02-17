import os
import sys
import time
import math

import requests
import random
import re
import json
import unicodedata

from typing import List, Dict, Tuple


try:
    GYM_USERNAME = os.environ['GYM_USERNAME']
    GYM_PASSWORD = os.environ['GYM_PASSWORD']
except KeyError:
    GYM_USERNAME = ""
    GYM_PASSWORD = ""


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

fighter_builds = [
    { "STRENGTH": 0.46, "SPEED": 0.32, "AGILITY": 0.22, "CHIN": 19, "HEIGHT":  9, "COUNT": 3 }, # albino
    { "STRENGTH": 0.55, "SPEED": 0.30, "AGILITY": 0.15, "CHIN": 22, "HEIGHT":  7, "COUNT": 1 }, # zam
    { "STRENGTH": 0.46, "SPEED": 0.25, "AGILITY": 0.29, "CHIN": 18, "HEIGHT": 12, "COUNT": 2 }, # agl
#    { "STRENGTH": 0.38, "SPEED": 0.30, "AGILITY": 0.32, "CHIN": 17, "HEIGHT": 13, "COUNT": 0 }, # bal
]


# ------------------------------
# Small helpers
# ------------------------------

def write_msg(command: str = "", etc: str = "", script: str = "query.fcgi"):
    data = {
        "command": command,
        **{k.lstrip("+").strip(): v.strip() for p in etc.split("&") if "=" in p for k, v in (p.split("=", 1),)}
    }

    headers = {
        "Referer": "https://webl.vivi.com/eko/menubar.html",
        "Sec-CH-UA": '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/143.0.0.0 Safari/537.36"
        ),
    }

    cookies = {
        "timezone": "480",
        "username": GYM_USERNAME,
        "password": GYM_PASSWORD,
        "block_ad": "1",
        "vivi-date": time.strftime("%m/%d/%y %H:%M"),
    }

    for attempt in range(7):
        time.sleep(2.75 + 15 * attempt)
        try:
            print(command, etc)
            resp = requests.post(f"https://webl.vivi.com/cgi-bin/{script}", data=data, headers=headers, cookies=cookies, timeout=10)
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
        name = re.search(r"<title>\s*([\w]+)", unicodedata.normalize("NFKD", response.text).encode("ascii", "ignore").decode("ascii", "ignore"), flags=re.IGNORECASE).group(1).lower()
        return f"{random.choice([ 'Byl', 'Ell', 'Fel', 'Kel', 'Kul' ])}'{name}" if name not in [ 'adam', 'alex', 'andrew', 'ben', 'bill', 'brent', 'brian', 'chris', 'colin', 'craig', 'dave', 'jason', 'joe', 'john', 'karen', 'marc', 'mark', 'mike', 'patti', 'paul', 'peter', 'sarah', 'sean', 'sharon', 'shawn', 'tim', 'tom', 'zhang', '' ] else ""
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

    try:
        with open('data.json') as f: ftr = json.load(f)
    except: ftr = {}

    #print(write_msg("eko_select_orders", f"your_team=Byl`phillip&strategy_choice=5H114insideR1")) # 6H122alloutR1 4H97ringR1 5H105insideR1

    for word in write_msg("eko_retired_fighters").split("Activate</A>"):
            if "regional_champion" not in word and "challenger.gif" not in word and "champion.gif" not in word:
                for team_id in re.findall(r"team_id=([0-9]+)", word):
                    write_msg("eko_activate", f"team_id={team_id}")
                    break

    team_ids = sorted(set(re.findall(r"team_id=([0-9]+)", write_msg("eko_all_fighters_brief"))), key=int)
    for team_id in team_ids:
        if team_id not in ftr: ftr[team_id] = {}
        text = write_msg("eko_control_fighter", "team_id=" + team_id)

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
        ftr[team_id]['RECORD'] = [ int(i) for i in re.search(r'\(([0-9]+)-([0-9]+)-([0-9]+) [0-9]+\/[0-9]+\)', text).groups() ]
        ftr[team_id]['DIVISION'] = [ i.lower() for i in re.search(r'eko_standings[\w&=+]+division=([\w-]+)[\w&=+]+region=([^&]+)', text).groups() ] + [ divis_str[len([ True for i in max_weights if i < ftr[team_id]['WEIGHT'][1]]) ].lower() ] # find correct weight div
        ftr[team_id]['TRAINING'] = [ stats_str.index(i.strip()) if i.strip() in stats_str else None for i in re.search(r' training <[Bb]>([a-z\s]+)[^<]*<[^<]*[\<Bb\>]*([a-z\s]+)', text).groups() ] + [ ' (intensive) <' in text ]
        ftr[team_id]['FIGHTPLAN'] = m.group(1) if (m := re.search(r'> your <[Bb]>(.+)<\/[Bb]> plan.', text)) else None

        fgt, fgt_tacs, baseaps = re.search(r' ([4-7]) feet *([0-9]{0,2})[^>]*team_id=([0-9]+)&describe=[0-9]\">(.*)<[I\/][AM][G>]', text), [ [], [], [], [] ], ftr[team_id]['STRENGTH'] + ftr[team_id]['SPEED'] + ftr[team_id]['AGILITY']
        if fgt:
            if not ftr[team_id].get('OPPONENT') or int(fgt.group(3)) != ftr[team_id]['OPPONENT'][1]:
                ftr[team_id]['OPPONENT'] = [ (int(fgt.group(1)) - 5) * 12 + int("0%s" % fgt.group(2)), int(fgt.group(3)), fgt.group(4)] + [ round(((wl := tuple(map(int, re.search(r'(\d+)-(\d+)-\d+ \d+/\d+\)  from the', text).groups())))[0] - wl[1]) / (sum(wl) + 1) / max(1, 8 - sum(wl)) * 10), [] ]
                for sess in sorted([ [ m.group(1), int(m.group(2)), 'round 1 (' in w, 'Managed by' in w ] for w in write_msg("eko_career_nodesc", f"team_id={ftr[team_id]['OPPONENT'][1]}").split("query_scout") if (m := re.search(r'team_id=([0-9]+)&session=([0-9]+)', w)) ], key=lambda x: (x[3], x[2], -x[1]))[ :max(3, ftr[team_id]['OPPONENT'][3] + 1) ]:
                    fght_text = write_msg("query_scout", f"team_id={sess[0]}&session={sess[1]}")
                    ftr_intro = re.findall(r"<[Pp]>In this corner, standing ([4-7]) feet *[and ]*([0-9]{0,2}).*in at \d+ pound.* win.* loss.* is(?: <font color=green><B>| )(.+)!!", fght_text)
                    if len(ftr_intro) > 1:
                        ftr_order = 0 if ftr[team_id]['OPPONENT'][2].strip() != ftr_intro[1][2].strip() and (ftr[team_id]['OPPONENT'][2].strip() == ftr_intro[0][2].strip() or ftr[team_id]['HEIGHT'] == (int(ftr_intro[0][0]) - 5) * 12 + int(f"0{ftr_intro[0][1]}")) else 1
                        p = re.findall(r" landed \d+ [^\d]+(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]+\d+ right", fght_text)[ftr_order :: 2]
                        for i, r in enumerate(re.findall(r"<[Bb][Rr]><[Hh][Rr]> +ROUND[^\n]+\n([^\n]+)\n([^\n]+)\n", fght_text)):
                            s = next((i for i, k in enumerate([ "(inside)", "(clinching)", "(feinting)", "(counter-punching)", "(using the ring)", "(ropes)", "(outside)", "(all out)", "." ]) if k in r[ftr_order]), None)
                            a = next((i for i, k in enumerate([ "to the body.<", "for the cut.<", "s head hunting.<", "." ]) if k in r[ftr_order]), None)
                            t, n = ((t := [int(x) for x in p[i]]) + [t[2] / (t[1] + 0.001)] if i < len(p) else [ 0 ] * 4), None
                            if a == 2 and (s in (0, 7) or (s in (1, 5) and not t[0])) and (not t[1] or t[0] > 34 or t[1] > 5): n = 0 # flash
                            elif a == 0 and s != 7 and (not t[1] or t[0] > 29 or t[1] > 4) and (not t[0] or t[3] < 2): n = 1 # weardown
                            elif a == 3 and s != 7 and (not t[1] or t[0] > 29 or t[1] > 4) and (not t[0] or t[3] < 3.2):  n = 2 # balanced
                            elif (a == 3 and s in (2, 4, 6, 8)) or (t[0] > 29 and t[3] >= 3.2): n = 3 # slap
                            elif a == 2 and (not t[0] or t[1] > 4): n = 4 # defend
                            fgt_tacs[min(i, len(fgt_tacs) - 1) if not sess[3] else len(fgt_tacs) - 1].append([ s, a, n ])
                ftr[team_id]['OPPONENT'][4] = [ ([-1, 0, 0, 0, 0, 0, 0]) if not t else (lambda xs, s: [max(xs, key=lambda x: (xs.count(x), xs[::-1].index(x))), len(set(xs))] + [round(s.count(i)/(len(s)+0.0001), 2) for i in range(5)])([row[0] for row in t], [row[2] for row in t]) for t in fgt_tacs ]
        else: ftr[team_id]['OPPONENT'] = None

        ftr[team_id]['TYPE'] = min(range(len(fighter_builds)), key=lambda i: (abs(baseaps * fighter_builds[i]['STRENGTH'] - ftr[team_id]['STRENGTH']) + abs(baseaps * fighter_builds[i]['SPEED'] - ftr[team_id]['SPEED']) + abs(baseaps * fighter_builds[i]['AGILITY'] - ftr[team_id]['AGILITY'])))

        print(ftr[team_id])

        if ftr[team_id]['DIVISION'][0] != ftr[team_id]['DIVISION'][2] and (ftr[team_id]['RATING'] != 18 or ftr[team_id]['DIVISION'][1] == "contenders"): # in wrong div
            write_msg("eko_change_division", f"your_team={ftr[team_id]['NAME']}&division={ftr[team_id]['DIVISION'][2]}weight")

        tr = [ None, None, (ftr[team_id]['CHIN'] < 11 + ftr[team_id]['STATUS'] // 5 or not 6 <= ftr[team_id]['CONDITIONING'] <= 11 or ftr[team_id]['STATUS'] - ftr[team_id]['RATING'] > 2) ]
        for i in range(2):
            baseaps = ftr[team_id]['STRENGTH'] + ftr[team_id]['SPEED'] + ftr[team_id]['AGILITY'] + int(tr[0] is not None and 1 <= tr[0] <= 3) # add ap if training str/apd/agl primarily
            if not i and not tr[2] and (ftr[team_id]['RATING'] == 18 or ftr[team_id]['RATING'] == 28 or ftr[team_id]['RATING'] < ftr[team_id]['STATUS'] or ftr[team_id]['KP'] < ftr[team_id]['STRENGTH'] // 3): tr[i] = 1 # float KP if no chance to gain a ap
            elif ftr[team_id]['CONDITIONING'] + int(tr[0] == 5) < 6: tr[i] = 5
            elif ftr[team_id]['CHIN'] < 11 + ftr[team_id]['STATUS'] // 5 or ftr[team_id]['CHIN'] + int(tr[0] == 4) - 10.0 < (fighter_builds[ftr[team_id]['TYPE']]['CHIN'] - 10.0 - ftr[team_id]['HEIGHT'] // 3.5) * ftr[team_id]['STATUS'] / 28.0: tr[i] = 4
            elif ftr[team_id]['AGILITY'] + int(tr[0] == 3) < baseaps * fighter_builds[ftr[team_id]['TYPE']]['AGILITY'] and ftr[team_id]['AGILITY'] - baseaps * fighter_builds[ftr[team_id]['TYPE']]['AGILITY'] <= ftr[team_id]['SPEED'] - baseaps * fighter_builds[ftr[team_id]['TYPE']]['SPEED']: tr[i] = 3
            elif ftr[team_id]['SPEED'] + int(tr[0] == 2) < baseaps * fighter_builds[ftr[team_id]['TYPE']]['SPEED']: tr[i] = 2
            else: tr[i] = 1 # KP insead of str
        if ftr[team_id]['TRAINING'][0] != tr[0] or (ftr[team_id]['TRAINING'][1] and ftr[team_id]['TRAINING'][1] != tr[1]) or ftr[team_id]['TRAINING'][2] != tr[2]:
            write_msg("eko_training", f"your_team={ftr[team_id]['NAME']}&train={train_str[tr[0]]}&train2={train_str[tr[1]]}&intensive={int(tr[2])}")
            ftr[team_id]['TRAINING'] = [ tr[0], ftr[team_id]['TRAINING'][1] and tr[1], tr[2] ]

        if ftr[team_id]['OPPONENT']: # [ Most used style, Amount of unique styles, flash %, weardown %, balanced %, slap %, defend % ]
            rng, hd, opp = random.Random(int(team_id) + sum(ftr[team_id]['RECORD']) * ftr[team_id]['WEIGHT'][0]), ftr[team_id]['OPPONENT'][0] - ftr[team_id]['HEIGHT'], ftr[team_id]['OPPONENT'][4]

            if ftr[team_id]['STATUS'] > 18 and rng.random() < 0.05: fp = '6H113alloutR1' # -1nohistory 0inside 1clinch 2feint 3counter 4ring 5ropes 6outside 7allout 8nostyle
            elif ftr[team_id]['RATING'] > 25: fp = rng.choice([ '417clinchR', rng.choice([ '5H114insideR', '5H105insideR' ]), rng.choice([ '5H105alloutR', '5H114alloutR', '4H97alloutR' ]), '6H122alloutR' if hd >= 0 else '5H105alloutR' ]) + rng.choice([ '1', '2' ])
            elif ftr[team_id]['WEIGHT'][1] < 200: # non hw
                if hd > 9 and rng.random() < 0.66: fp = '6H122alloutR' + str(rng.randint(1, 2 if ftr[team_id]['RECORD'][0] > 9 else 3)) # He is much taller
                elif hd <= 2: fp = rng.choice([ '4H97clinchR1', '5H105clinchR1' ]) if rng.random() < 0.5 else '5H114insideR1' # Im slightly taller
                elif hd <= 0: fp = rng.choice([ '4H97ringR1', '5H114ringR1' ]) if rng.random() < 0.7 else '5H105insideR1' # equal or Im taller
                else: fp = rng.choice([ '417clinchR', '5H105alloutR', '5H105insideR', '5H114alloutR', '5H114insideR', '4H97alloutR', '6H122alloutR' ][ :6 if ftr[team_id]['CHIN'] < 15 else 7 ]) + rng.choice([ '1', '2', '3' ])
            else: fp = rng.choice([ '5H105alloutR', '4H97alloutR', '6H122alloutR', '5H114insideR', '5H105insideR', '5H105insideR', '5H105ringR' ]) + rng.choice([ '1', '1', '2' ])

            for r, f in ( (2, 3), (1, 2), (0, 1) ):
                if r == 0 and ftr[team_id]['WEIGHT'][1] > 199 and hd > 5 and (opp[r][0] == 0 or (opp[r][0] == 1 and opp[r][3] > 0.9) or opp[r][0] == 7) and rng.random() < 0.8: fp = f'{"4H97" if hd > 8 else "5H105"}counterR{f}' # taller heavyweight
                elif opp[r][0] == 7 and opp[r][1] <= 2: fp = f'4H97ringR{f}' if hd <= 0 or ftr[team_id]['AGILITY'] >= ftr[team_id]['SPEED'] else f'4H97clinchR{f}' # allout def
                elif opp[r][2] > 0.7 or (opp[r][0] == 7 and opp[r][1] <= 1): fp = rng.choice([ f'4H97ringR{f}', f'5H105ringR{f}', f'5H114ringR{f}' ] if hd <= 0 or ftr[team_id]['AGILITY'] >= ftr[team_id]['SPEED'] else [ f'4H97clinchR{f}', f'5H105clinchR{f}' ]) # anti flash
                elif opp[r][3] > 0.8: # always body
                    if opp[r][0] == 0: fp = f'5H114ringR{f}' if hd <= 0 or ftr[team_id]['AGILITY'] >= ftr[team_id]['SPEED'] else f'5H114clinchR{f}'  # usually inside
                    elif opp[r][0] == 4: fp = rng.choice([ f'5H114alloutR{f}', f'5H105alloutR{f}', f'5H114insideR2' ] if hd > 3 else [ f'4H97alloutR{f}', f'5H114insideR{f}', f'5H114insideR2', f'5H105insideR{f}' ]) # usually ring
                    elif hd > 9 and ftr[team_id]['WEIGHT'][1] < 200: fp = rng.choice([ f'6H122alloutR{f}', f'5H105alloutR{f}' ])
                    elif hd > 5 and ftr[team_id]['WEIGHT'][1] < 200: fp = rng.choice([ f'5H105alloutR{f}', f'5H114alloutR{f}', f'4H97alloutR{f}', f'5H105alloutR{f}' ])
                    elif hd > 2 and ftr[team_id]['WEIGHT'][1] < 200: fp = rng.choice([ f'5H114insideR{f}', f'5H105insideR{f}', f'4H97alloutR{f}', f'5H105alloutR{f}' ][ :3 if ftr[team_id]['CHIN'] > 15 else 4 ])
                    else: fp = rng.choice([ f'5H105insideR{f}', f'5H114insideR{f}', f'4H97alloutR{f}' if ftr[team_id]['CHIN'] > 13 else f'5H105insideR{f}', f'5H105ringR{f}' ])
                elif opp[r][4] > 0.9: # always balanced tactics
                        if hd > 9: fp = rng.choice([ f'6H122alloutR{f}', f'5H114alloutR{f}' ])
                        elif hd > 5: fp = rng.choice([ f'6H122alloutR{f}', f'5H114alloutR{f}' ] if opp[r][0] in (4, 6) else [ f'4H97alloutR{f}', f'5H105alloutR{f}', f'5H114insideR{f}' ])
                        elif hd > 2: fp = rng.choice([ f'5H105alloutR{f}', f'5H114alloutR{f}' ] if opp[r][0] in (4, 6) else [ f'4H97alloutR{f}', f'5H105alloutR{f}', f'5H114insideR{f}', f'5H114ringR{f}' ])
                        else: rng.choice([ f'5H105insideR{f}', f'5H114insideR{f}', f'4H97alloutR{f}' if ftr[team_id]['CHIN'] > 13 else f'5H105insideR{f}', f'5H105ringR{f}' ])
                elif opp[r][5] > 0.9: # always slap
                    fp = f'6H122alloutR{f}' if hd > 5 else f'5H114alloutR{f}'

            # make everything height based, add check for rd2 rd3 or 3 if they are better targets for flash, dont overwrite a slap round

            if ftr[team_id]['FIGHTPLAN'] != fp:
                write_msg("eko_select_orders", f"your_team={ftr[team_id]['NAME']}&strategy_choice={fp}")
                ftr[team_id]['FIGHTPLAN'] = fp

        if ftr[team_id]['IPS'] / (ftr[team_id]['STATUS'] + 1) > 35:
            if ftr[team_id]['DIVISION'][1] == "contenders" or ftr[team_id]['STATUS'] > 18:
                write_msg("eko_retire_byid", f"team_id={team_id}&verify_retire=1")
            else:
                write_msg("eko_transfer", f"your_team={ftr[team_id]['NAME']}&to_manager=77894")


    ftr_new = {k: ftr[k] for k in team_ids if k in ftr}

    ftr_by_height = [ { h: 0 for h in range(-2, 21) } for _ in range(len(fighter_builds)) ]
    for f in ftr_new: ftr_by_height[ftr_new[f]['TYPE']][ftr_new[f]['HEIGHT']] += 1

    for type_new, height, value in ( (i, h, v) for i, d in enumerate(ftr_by_height) for h, v in d.items() ):
        while value and ftr_by_height[type_new][height] < fighter_builds[type_new]['COUNT']:
            chin, condition, build = random.randint(12, 13), 6, random.randint(-2 if height > -2 else 3, 3) 
            strength = round((63 - height - chin - condition + height // 6) * fighter_builds[type_new]['STRENGTH'])
            agility = round((63 - height - chin - condition + height // 6) * fighter_builds[type_new]['AGILITY'])
            ko_punch = strength // 3
            speed = 69 - height - strength - ko_punch - agility - chin - condition
            while ((w := compute_weight(height, strength, agility, condition, build))[0] < max_weights[0] or 185 < w[0] < 200) and build < 3: build += 1
            write_msg("eko_create_fighter", f"competition=eko&region=0&team={find_name()}&height={height}&strength={strength}&ko_punch={ko_punch}&speed={speed}&agility={agility}&chin={chin}&condition={condition}&cut=1&build={build}")
            ftr_by_height[type_new][height] += 1
    # set build limit for min and max height, set max height and add hws

    with open('data.json.tmp', 'w', encoding='utf-8') as f:
        json.dump(ftr_new, f, ensure_ascii=False, indent=4)
    os.replace('data.json.tmp', 'data.json')
