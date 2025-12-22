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

fighter_builds = [
    { "STRENGTH": 0.45, "SPEED": 0.33, "AGILITY": 0.22, "CHIN": 19, "HEIGHT": 10, "COUNT": 3 }, # albino
    { "STRENGTH": 0.55, "SPEED": 0.30, "AGILITY": 0.15, "CHIN": 22, "HEIGHT":  7, "COUNT": 1 }, # zam
    { "STRENGTH": 0.46, "SPEED": 0.25, "AGILITY": 0.29, "CHIN": 18, "HEIGHT": 12, "COUNT": 2 }, # agl
    { "STRENGTH": 0.40, "SPEED": 0.29, "AGILITY": 0.31, "CHIN": 17, "HEIGHT": 13, "COUNT": 0 }, # bal
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


kk = """

    <HTML>
    <HEAD>
    <script>
    document.cookie='timezone='+(new Date()).getTimezoneOffset();
    </script>
    <link rel=STYLESHEET type=text/css href=/eko/eko.css>
    <TITLE>WEBL Query Server (careerbyid)</TITLE>
</HEAD><BODY bgcolor=#eeeeee>
<center>
<img src="https://webl.vivi.com/images/webltitle.gif" width="200" height="110">
</center>

<BR><CENTER><SMALL>

</SMALL></CENTER>
<H1>Gonzo Young 4</H1><P><font size=-1>To report offensive fighter names and descriptions <a href=https://webl.vivi.com/cgi-bin/forum.fpl?operation=contact_webmaster>click here.</A><A  HREF="/cgi-bin/prompt.fcgi?+command=query_censor_team&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382"><P>censor fighter's name</A><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_retire_byid&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382"><P>retire fighter</A><P><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_unschedule_match&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382">Unschedule next bout (must be more than one day in advance)</A><P>

<P><A  HREF="/cgi-bin/prompt.fcgi?+command=query_censor_team_descr&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382">censor description</A><P>Gonzo Young 4 stands 5 feet 4 inches (162 centimeters) tall. He fights for the 
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=172393">Pump Tech and Sim Roids Gym Of Stars(UBA)</A> gym
 in Portland, Maine
and is ranked #18 in the <A name="Bantamweight" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_standings&+competition=eko&+describe=1&+division=Bantam&+region=Eurasia&team=gonzoyoung4">Bantamweight</A> division (Eurasia).
<P>Gonzo Young 4's next opponent is the 4 feet 11 inches, 
<A name="zolfederico" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1650328&describe=1">Zol`federico<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (24-13-0 22/12)  from the 
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=246874">Bannerlords</A> gym  for   $1,310,720  on <B>Monday, December 22, 2025.</B>
<HR><H3>Gonzo Young 4's Record</H3><P>Gonzo Young 4's record is 30-23-2 (20/16).<BR>His current <script language=javascript>
    <!--
    function help() {
	window.open("", "glossary", "width=550,height=300,resizable=1,scrollbars=1");
    }
    //-->
</script>
<a href=https://cloudfront-webl.vivi.com/eko/glossary.html#rating target=glossary onClick=help()>rating</A> is 16 and his <a href=https://cloudfront-webl.vivi.com/eko/glossary.html#status target=glossary onClick=help()> status</A> is 18.
<BR>His career earnings are   $22,555,512 .<P>Select any icon for a detailed account of a fight.
<P><table border=0><tr><td><td align=left>vs 
<A name="zolfederico" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1650328&describe=1">Zol`federico<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=246874">Bannerlords</A>) - 4 feet 11 inches - Bantamweight bout on  December 22, 2025, week 1234: </table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1233"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="likqidyo-yo" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1566946&describe=1">LikQid Yo-Yo</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=157762">Auto-LikQid</A>) - 5 feet 3 inches - Bantamweight bout on  December 15, 2025, week 1233: won by unanimous decision.  Earned   $1,012,500 . Score: 120-108, 120-108, 120-108 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1233">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1232"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png></NOBR></A><td align=left>vs 
<A name="toweropower" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1512332&describe=1">Tower O`Power<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=246240">"Brainiac Descends" - AI Build v0.4</A>) - 5 feet 1 inch - Bantamweight bout on  December 8, 2025, week 1232: lost by KO in round 2 (2:42 ) Score: 10-9, 10-9, 10-9 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1232">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1231"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="quintonthehorsebrownweather" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1686886&describe=1">Quinton "The Horse" Brownweather</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245731">A Very Brown Weather</A>) - 5 feet 7 inches - Bantamweight bout on  December 1, 2025, week 1231: won by KO in round 12 (2:58 ) Earned   $1,113,750 . Score: 107-101, 107-100, 106-101 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1231">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1230"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png></NOBR></A><td align=left>vs 
<A name="prominent" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1571555&describe=1">Prominent</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 1 inch - Bantamweight bout on  November 24, 2025, week 1230: lost by TKO in round 7 (3:00 ) Score: 65-69, 64-69, 66-69 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1230">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1229"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="edgarsbreakdancerjekabsons" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1561815&describe=1">Edgars "Breakdancer" Jekabsons<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=246240">"Brainiac Descends" - AI Build v0.4</A>) - 5 feet 5 inches - Bantamweight bout on  November 17, 2025, week 1229: won by TKO in round 9 (3:00 ) Earned   $1,267,200 . Score: 89-87, 88-87, 88-86 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1229">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1228"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="quintonthehorsebrownweather" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1686886&describe=1">Quinton "The Horse" Brownweather</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245731">A Very Brown Weather</A>) - 5 feet 7 inches - Bantamweight bout on  November 10, 2025, week 1228: won by KO in round 10 (2:47 ) Earned   $845,152 . Score: 87-83, 87-83, 87-83 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1228">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1227"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/loss.png border=0 ALT=loss.png></NOBR></A><td align=left>vs 
<A name="freakropist7" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1635314&describe=1">"Freak Ropist" 7</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 4 inches - Bantamweight bout on  November 3, 2025, week 1227: lost by unanimous decision. Score: 112-116, 112-116, 111-115 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1227">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1226"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png></NOBR></A><td align=left>vs 
<A name="carterhelicoptermarks" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1651838&describe=1">Carter "Helicopter" MARKS</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 8 inches - Bantamweight bout on  October 27, 2025, week 1226: lost by KO in round 11 (2:24 ) Score: 94-96, 94-96, 94-96 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1226">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1225"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/tie.png border=0 ALT=tie.png></NOBR></A><td align=left>vs 
<A name="hmraasikumanor" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1613213&describe=1">"HM" Raasiku Manor</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 7 inches - Bantamweight bout on  October 20, 2025, week 1225: fought to a draw.  Earned   $655,360 . Score: 115-115, 114-114, 115-113 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1225">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1224"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png></NOBR></A><td align=left>vs 
<A name="prominent" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1571555&describe=1">Prominent</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 1 inch - Bantamweight bout on  October 13, 2025, week 1224: lost by KO in round 12 (2:51 ) Score: 100-109, 100-110, 101-109 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1224">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1223"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="hmraasikumanor" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1613213&describe=1">"HM" Raasiku Manor</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 7 inches - Bantamweight bout on  October 6, 2025, week 1223: won by majority decision.  Earned   $1,310,720 . Score: 114-114, 115-113, 115-114 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1223">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1222"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="hmraasikumanor" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1613213&describe=1">"HM" Raasiku Manor</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 7 inches - Bantamweight bout on  September 29, 2025, week 1222: won by unanimous decision.  Earned   $1,300,500 . Score: 115-113, 115-113, 115-113 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1222">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1221"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqLost.png border=0 ALT=DqLost.png></NOBR></A><td align=left>vs 
<A name="carterhelicoptermarks" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1651838&describe=1">Carter "Helicopter" MARKS</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 8 inches - Bantamweight bout on  September 22, 2025, week 1221: lost by a foul in round 12 (1:15 ) Score: 104-105, 103-105, 103-105 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1221">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1220"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="quintonthehorsebrownweather" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1686886&describe=1">Quinton "The Horse" Brownweather</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245731">A Very Brown Weather</A>) - 5 feet 7 inches - Bantamweight bout on  September 15, 2025, week 1220: won by KO in round 11 (1:07 ) Earned   $1,267,200 . Score: 97-92, 97-92, 97-92 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1220">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1219"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/loss.png border=0 ALT=loss.png></NOBR></A><td align=left>vs 
<A name="hmraasikumanor" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1613213&describe=1">"HM" Raasiku Manor</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 7 inches - Bantamweight bout on  September 8, 2025, week 1219: lost by split decision. Score: 113-114, 114-113, 113-114 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1219">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1218"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqLost.png border=0 ALT=DqLost.png></NOBR></A><td align=left>vs 
<A name="brothercaboose" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1028009&describe=1">Brother Caboose<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=145700">Brothers of the Fist</A>) - 5 feet 8 inches - Bantamweight bout on  September 1, 2025, week 1218: lost by a foul in round 1 (1:32 ) <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1218">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1217"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="carterhelicoptermarks" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1651838&describe=1">Carter "Helicopter" MARKS</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 8 inches - Bantamweight bout on  August 25, 2025, week 1217: won by KO in round 12 (2:25 ) Earned   $1,430,550 . Score: 105-106, 104-105, 105-104 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1217">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1216"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="hmraasikumanor" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1613213&describe=1">"HM" Raasiku Manor</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 7 inches - Bantamweight bout on  August 18, 2025, week 1216: won by unanimous decision.  Earned   $882,000 . Score: 115-113, 115-113, 115-113 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1216">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1215"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="freakropist7" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1635314&describe=1">"Freak Ropist" 7</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 4 inches - Bantamweight bout on  August 11, 2025, week 1215: won by unanimous decision.  Earned   $571,220 . Score: 115-113, 114-113, 115-113 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1215">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1214"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqWon.png border=0 ALT=DqWon.png></NOBR></A><td align=left>vs 
<A name="freakropist7" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1635314&describe=1">"Freak Ropist" 7</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 4 inches - Bantamweight bout on  August 4, 2025, week 1214: won by a foul in round 1 (1:46 ) Earned   $564,480 . <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1214">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1213"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/loss.png border=0 ALT=loss.png></NOBR></A><td align=left>vs 
<A name="freakropist7" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1635314&describe=1">"Freak Ropist" 7</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 4 inches - Bantamweight bout on  July 28, 2025, week 1213: lost by unanimous decision. Score: 111-115, 113-115, 111-115 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1213">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1212"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqLost.png border=0 ALT=DqLost.png></NOBR></A><td align=left>vs 
<A name="brothercaboose" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1028009&describe=1">Brother Caboose<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=145700">Brothers of the Fist</A>) - 5 feet 8 inches - Bantamweight bout on  July 21, 2025, week 1212: lost by a foul in round 1 (2:53 ) <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1212">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1211"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="russlightningjoeezra" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1528383&describe=1">Russ "Lightning Joe" Ezra<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 8 inches - Bantamweight bout on  July 14, 2025, week 1211: won by KO in round 12 (1:52 ) Earned   $728,728 . Score: 104-107, 105-104, 106-106 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1211">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1210"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqLost.png border=0 ALT=DqLost.png><IMG VALIGN=TOP src=https://webl-images.vivi.com/00BeltRegionals.png border=0 ALT=championship></NOBR></A><td align=left>vs 
<A name="hankeypankey" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1691313&describe=1">Hankey Pankey <IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=247645">Bathroom Brawlers [SALT]</A>) - 6 feet - Bantamweight bout on  July 7, 2025, week 1210: lost by a foul in round 10 (2:06 ) Score: 83-88, 83-88, 83-88 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1210">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1209"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="edgarsbreakdancerjekabsons" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1561815&describe=1">Edgars "Breakdancer" Jekabsons<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=246240">"Brainiac Descends" - AI Build v0.4</A>) - 5 feet 5 inches - Bantamweight bout on  June 30, 2025, week 1209: won by TKO in round 9 (3:00 ) Earned   $628,342 . Score: 88-83, 89-84, 88-84 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1209">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1208"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png></NOBR></A><td align=left>vs 
<A name="hmraasikumanor" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1613213&describe=1">"HM" Raasiku Manor</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 7 inches - Bantamweight bout on  June 23, 2025, week 1208: lost by KO in round 11 (1:50 ) Score: 95-95, 95-96, 94-96 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1208">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1207"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="russlightningjoeezra" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1528383&describe=1">Russ "Lightning Joe" Ezra<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 8 inches - Bantamweight bout on  June 16, 2025, week 1207: won by KO in round 12 (2:22 ) Earned   $836,550 . Score: 103-107, 104-105, 105-105 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1207">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1206"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/loss.png border=0 ALT=loss.png></NOBR></A><td align=left>vs 
<A name="freakropist7" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1635314&describe=1">"Freak Ropist" 7</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 4 inches - Bantamweight bout on  June 9, 2025, week 1206: lost by unanimous decision. Score: 112-115, 112-115, 113-115 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1206">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1205"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/loss.png border=0 ALT=loss.png><IMG VALIGN=TOP src=https://webl-images.vivi.com/00BeltRegionals.png border=0 ALT=championship></NOBR></A><td align=left>vs 
<A name="isaactopaz" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=32656&describe=1">Isaac Topaz<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 6 feet - Bantamweight bout on  June 2, 2025, week 1205: lost by unanimous decision. Score: 112-117, 112-116, 112-115 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1205">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1204"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="edgarsbreakdancerjekabsons" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1561815&describe=1">Edgars "Breakdancer" Jekabsons<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=246240">"Brainiac Descends" - AI Build v0.4</A>) - 5 feet 5 inches - Bantamweight bout on  May 26, 2025, week 1204: won by TKO in round 10 (3:00 ) Earned   $845,152 . Score: 98-96, 97-96, 99-96 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1204">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1203"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/tie.png border=0 ALT=tie.png></NOBR></A><td align=left>vs 
<A name="russlightningjoeezra" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1528383&describe=1">Russ "Lightning Joe" Ezra<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 8 inches - Bantamweight bout on  May 19, 2025, week 1203: fought to a draw.  Earned   $441,000 . Score: 115-115, 114-114, 114-115 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1203">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1202"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="russlightningjoeezra" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1528383&describe=1">Russ "Lightning Joe" Ezra<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 8 inches - Bantamweight bout on  May 12, 2025, week 1202: won by KO in round 12 (2:41 ) Earned   $951,808 . Score: 106-104, 104-106, 104-106 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1202">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1201"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqLost.png border=0 ALT=DqLost.png></NOBR></A><td align=left>vs 
<A name="russlightningjoeezra" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1528383&describe=1">Russ "Lightning Joe" Ezra<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 8 inches - Bantamweight bout on  May 5, 2025, week 1201: lost by a foul in round 12 (2:56 ) Score: 104-106, 103-108, 105-106 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1201">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1200"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/loss.png border=0 ALT=loss.png></NOBR></A><td align=left>vs 
<A name="isaactopaz" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=32656&describe=1">Isaac Topaz<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 6 feet - Bantamweight bout on  April 28, 2025, week 1200: lost by unanimous decision. Score: 113-116, 114-116, 113-115 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1200">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1199"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/loss.png border=0 ALT=loss.png></NOBR></A><td align=left>vs 
<A name="albinosgym" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=242192&describe=1">Albinos Gym<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 8 inches - Bantamweight bout on  April 21, 2025, week 1199: lost by majority decision. Score: 114-116, 114-115, 114-114 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1199">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1198"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqLost.png border=0 ALT=DqLost.png></NOBR></A><td align=left>vs 
<A name="rishtonsquare" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1631461&describe=1">Rishton Square<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245611">Armo [SALT]</A>) - 5 feet 11 inches - Bantamweight bout on  April 14, 2025, week 1198: lost by a foul in round 10 (1:23 ) Score: 81-89, 81-89, 81-89 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1198">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1197"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png><IMG VALIGN=TOP src=https://webl-images.vivi.com/00BeltRegionals.png border=0 ALT=championship></NOBR></A><td align=left>vs 
<A name="cohenhazardlightshammond" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1687507&describe=1">Cohen "Hazard Lights" HAMMOND<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=244354">Elektrik Church</A>) - 5 feet 1 inch - Bantamweight bout on  April 7, 2025, week 1197: lost by KO in round 12 (1:18 ) Score: 103-105, 104-105, 104-105 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1197">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1196"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png><IMG VALIGN=TOP src=https://webl-images.vivi.com/00BeltRegionals.png border=0 ALT=championship></NOBR></A><td align=left>vs 
<A name="dutch1" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1172797&describe=1">Dutch 1<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=181510">The Strike Team Gym</A>) - 5 feet - Bantamweight bout on  March 31, 2025, week 1196: lost by KO in round 1 (1:49 ) <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1196">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1195"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="roger60mphodonnell" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1650307&describe=1">Roger "60 MPH" ODONNELL<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 8 inches - Bantamweight bout on  March 24, 2025, week 1195: won by KO in round 12 (2:56 ) Earned   $1,441,792 . Score: 105-105, 104-104, 105-104 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1195">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1194"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="geekpdancer" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1604657&describe=1">Gee Kp Dancer</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=153052">Tha Rows Finest |-| Gee Money |-| Nomads</A>) - 5 feet 7 inches - Bantamweight bout on  March 17, 2025, week 1194: won by KO in round 12 (1:50 ) Earned   $1,113,750 . Score: 104-105, 104-105, 104-105 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1194">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1193"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="yell0wmyownfighterone" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1274593&describe=1">Yell0w "My Own Fighter" One</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=117799">Yell0w -- The Comeback</A>) - 5 feet 3 inches - Bantamweight bout on  March 10, 2025, week 1193: won by KO in round 3 (2:59 ) Earned   $845,152 . Score: 20-17, 20-17, 20-17 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1193">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1192"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqLost.png border=0 ALT=DqLost.png></NOBR></A><td align=left>vs 
<A name="yell0wmyownfighterone" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1274593&describe=1">Yell0w "My Own Fighter" One</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=117799">Yell0w -- The Comeback</A>) - 5 feet 3 inches - Bantamweight bout on  March 3, 2025, week 1192: lost by a foul in round 2 (2:16 ) Score: 10-9, 10-9, 10-9 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1192">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1191"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="yell0wmyownfighterone" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1274593&describe=1">Yell0w "My Own Fighter" One</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=117799">Yell0w -- The Comeback</A>) - 5 feet 3 inches - Bantamweight bout on  February 24, 2025, week 1191: won by KO in round 10 (2:33 ) Earned   $845,152 . Score: 87-79, 87-79, 87-79 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1191">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1190"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png></NOBR></A><td align=left>vs 
<A name="brothercaboose" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1028009&describe=1">Brother Caboose<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=145700">Brothers of the Fist</A>) - 5 feet 8 inches - Bantamweight bout on  February 17, 2025, week 1190: lost by KO in round 12 (2:35 ) Score: 103-107, 106-106, 105-105 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1190">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1189"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="carterhelicoptermarks" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1651838&describe=1">Carter "Helicopter" MARKS</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 8 inches - Bantamweight bout on  February 10, 2025, week 1189: won by unanimous decision.  Earned   $768,320 . Score: 116-112, 116-111, 116-112 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1189">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1188"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="fiorenzobucci" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1686375&describe=1">Fiorenzo Bucci</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=44555">smoke and fly</A>) - 5 feet 5 inches - Bantamweight bout on  February 3, 2025, week 1188: won by split decision.  Earned   $662,480 . Score: 115-114, 115-114, 114-115 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1188">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1187"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KOd.png border=0 ALT=KOd.png></NOBR></A><td align=left>vs 
<A name="youssefyoussef" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1371465&describe=1">Youssef Youssef</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=209943">Dave31</A>) - 4 feet 10 inches - Bantamweight bout on  January 27, 2025, week 1187: lost by KO in round 1 (1:56 ) <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1187">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1186"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="maybeslightlyoverratedfighter" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=981040&describe=1">May be slightly overrated fighter</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=131815">Kung Fu Kimono</A>) - 5 feet 9 inches - Bantamweight bout on  January 20, 2025, week 1186: won by KO in round 12 (2:44 ) Earned   $202,752 . Score: 104-104, 104-104, 105-104 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1186">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1185"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/DqWon.png border=0 ALT=DqWon.png></NOBR></A><td align=left>vs 
<A name="canopener" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=61064&describe=1">can opener</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 3 inches - Bantamweight bout on  January 13, 2025, week 1185: won by a foul in round 1 (2:16 ) Earned   $2,000 . <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1185">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1184"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="whiskybrewerduncanonisleofislay" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1578830&describe=1">Whisky Brewer "Duncan" on Isle of Islay</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=47591">The Dark Side of Albino  &lt; Evil Empire ></A>) - 5 feet 2 inches - Bantamweight bout on  January 6, 2025, week 1184: won by TKO in round 12 (0:56 ) Earned   $12,672 . Score: 107-105, 107-105, 107-104 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1184">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1183"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="frankbelinsky" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1646595&describe=1">Frank Belinsky</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=246588">Rotting Corpses and the Otherwise Exhumed</A>) - 5 feet 2 inches - Bantamweight bout on  December 30, 2024, week 1183: won by KO in round 9 (2:40 ) Earned   $7,128 . Score: 76-77, 75-79, 76-77 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1183">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1182"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/decision.png border=0 ALT=decision.png></NOBR></A><td align=left>vs 
<A name="cairoicyboxblevins" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1667075&describe=1">Cairo "Icy Box" BLEVINS</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A>) - 5 feet 2 inches - Bantamweight bout on  December 23, 2024, week 1182: won by unanimous decision.  Earned   $320 . Score: 116-113, 116-112, 115-113 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1182">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1181"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="quintonthehorsebrownweather" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1686886&describe=1">Quinton "The Horse" Brownweather</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245731">A Very Brown Weather</A>) - 5 feet 7 inches - Bantamweight bout on  December 16, 2024, week 1181: won by KO in round 11 (2:49 ) Earned   $1,782 . Score: 94-96, 94-96, 94-96 
 <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=1181">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=293"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="chippie" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=18791&describe=1">Chippie</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=4649">Cippie</A>) - 5 feet 4 inches - Bantamweight bout on  July 18, 2005, week 293: won by KO in round 1 (2:03 ) <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=293">highlights</A>.</table>
<P><table border=0><tr><td><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_scout&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=292"><NOBR><IMG ALIGN=MIDDLE src=https://webl-images.vivi.com/KO.png border=0 ALT=KO.png></NOBR></A><td align=left>vs 
<A name="whiphubley" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=16097&+team_id=1032644&describe=1">Whip Hubley</A>  (
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=124779">George Takei Psychic Friends Network</A>) - 5 feet 7 inches - Bantamweight bout on  July 11, 2005, week 292: won by TKO in round 1 (0:11 ) <A name="highlights" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_highlights&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1133382&session=292">highlights</A>.</table>

</BODY></HTML>


"""



llp = """
    <HTML>
    <HEAD>
    <script>
    document.cookie='timezone='+(new Date()).getTimezoneOffset();
    </script>
    <link rel=STYLESHEET type=text/css href=/eko/eko.css>
    <TITLE>WEBL Query Server (scout)</TITLE>
</HEAD><BODY bgcolor=#eeeeee>
<center>
<img src="https://webl.vivi.com/images/webltitle.gif" width="200" height="110">
</center>

<BR><CENTER><SMALL>

</SMALL></CENTER>
<P>Back to the <A name="bio+page" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+describe=1&+division=Heavy&+region=16097&+team_id=1480661">bio page.</A>
<HR><H1>TUESDAY   DECEMBER  16, 2025</H1>
<P>In this corner, standing 5 feet  and 5 inches (165 centimeters) tall weighing in at 130 pounds (59 kilograms) with a record of 12 wins, 0 draws, and 6 losses fighting for Gray Area out of Columbus, Ohio is <font color=green><B>"Irresistible" Emma Starr!!</B></font>


<P>In this corner, standing 5 feet  and 2 inches (157 centimeters) tall weighing in at 130 pounds (59 kilograms) with a record of 42 wins, 1 draw, and 52 losses fighting for The Dark Side of Albino  &lt; Evil Empire > out of Sydney, Australia is <font color=green><B>ClinchGeneralNusuki!!</B></font>


<P>This bout is scheduled for 12 rounds.<BR>

<BR><HR> ROUND 1<HR><BR>
Irresistible feints and fakes (feinting).<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and goes to the body.<BR>
<BR>
...<BR>
...<BR>
...<BR>
<B>Irresistible attacks with a hook to the solar plexus.  </B><BR>
<B>Irresistible feints with a right but then lands a clean hook to the stomach.  </B>ClinchGeneralNusuki ignores it.<BR>
...<BR>
Irresistible throws a right hand to the mouth, but it''s soft .<BR>
ClinchGeneralNusuki lunges with a hook to the solar plexus, but Irresistible slips it .<BR>
...<BR>
<B>Irresistible feints with a left but then hits ClinchGeneralNusuki with a quick jab to the solar plexus.  </B>ClinchGeneralNusuki sneers!<font color=blue> </font> <BR>
...<BR>
<B>Irresistible throws a clean straight right to the nose.  </B><BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
<B>Irresistible feints with a left but then annoys ClinchGeneralNusuki with a quick jab to the temple.  </B><BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
ClinchGeneralNusuki fires a sweeping right to the face, but Irresistible knocks it away .<BR>
...<BR>
<B>ClinchGeneralNusuki jars Irresistible with a big overhand right to the nose!! The crowd is on its feet!!  <font color=blue></font> </B><BR>
ClinchGeneralNusuki tries a roundhouse to the stomach, but Irresistible partially deflects it .<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
Irresistible lashes out with a jab to the jaw, but is ineffective .<BR>
...<BR>
Irresistible feints with a jab.  <BR>
...<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
ClinchGeneralNusuki tries an uppercut to the stomach, but Irresistible deflects it .<BR>
ClinchGeneralNusuki tries to land a right hand to the solar plexus, but Irresistible partially deflects it .<BR>
<B>Irresistible feints with a left but then lands a quick hook to the eye.  </B><BR>
<B>Irresistible annoys ClinchGeneralNusuki with a quick straight right to the ribs.  </B><BR>
...<BR>
<B>Irresistible feints with a left but then lands a quick straight right to the solar plexus.  </B><BR>
...<BR>
<B>ClinchGeneralNusuki throws a hook to the head.  </B><BR>
ClinchGeneralNusuki probes with an uppercut to the face, but Irresistible blocks it .<BR>
...<BR>
Irresistible reaches with an uppercut to the head, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
<B>ClinchGeneralNusuki fires a nice left to the stomach.  </B><BR>
...<BR>
<B>Irresistible feints with a left but then throws an uppercut to the stomach.  </B><BR>
...<BR>
<B>Irresistible throws a right to the ribs.  </B><BR>
...<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 38 of 51 punches -- 14 power punches, 10 jabs, 14 rights.  (118 points)<BR>ClinchGeneralNusuki landed 11 of 34 punches -- 7 power punches, 0 jabs, 4 rights.  (40 points)<BR><BR>"Irresistible" Emma Starr won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 10-9.  <BR>
<BR>
<BR>
Irresistible doesn''t need to rest.<BR>
<BR>
ClinchGeneralNusuki doesn''t need to rest.<BR>
<BR>
<BR>

<BR><HR> ROUND 2<HR><BR>
Irresistible feints and fakes (feinting).<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and goes to the body.<BR>
<BR>
...<BR>
<B>Irresistible annoys ClinchGeneralNusuki with a hook to the stomach.  </B><BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
<B>Irresistible feints with a left but then annoys ClinchGeneralNusuki with a quick overhand right to the head.  </B>ClinchGeneralNusuki sneers!<font color=blue> </font> <BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
<B>Irresistible feints with a left but then punches ClinchGeneralNusuki with an excellent hook to the jaw.  </B>ClinchGeneralNusuki hangs on until the referee breaks them up.<BR>
ClinchGeneralNusuki probes with a roundhouse to the head, but doesn''t quite connect .<BR>
...<BR>
ClinchGeneralNusuki charges with a sweeping right to the stomach, but is ineffective .<BR>
ClinchGeneralNusuki reaches with a hook to the stomach, but Irresistible partially deflects it .<BR>
...<BR>
...<BR>
<B>Irresistible connects with a cross to the mouth.  </B>ClinchGeneralNusuki ignores it.<BR>
<B>Irresistible feints with a right but then tags ClinchGeneralNusuki with a clean jab to the ribs.  </B><BR>
...<BR>
ClinchGeneralNusuki charges with an uppercut to the chest, but Irresistible partially deflects it .<BR>
Irresistible charges with a jab to the stomach, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
<B>ClinchGeneralNusuki throws an uppercut to the solar plexus.  </B><BR>
...<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
Irresistible lunges with a right to the head, but misses .<BR>
<B>Irresistible fires a hook to the stomach.  </B>ClinchGeneralNusuki quickly recovers.<BR>
ClinchGeneralNusuki lunges with a hook to the chest, but misses completely .<BR>
Irresistible attacks with a left to the ribs, but it''s soft .<BR>
Irresistible tries to land a sweeping right to the chin, but is ineffective .<BR>
ClinchGeneralNusuki lashes out with a right hand to the ribs, but it''s short .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
<B>Irresistible throws a quick jab to the solar plexus.  </B><BR>
<B>Irresistible feints with a right but then lands a right to the stomach.  </B>ClinchGeneralNusuki ignores it.<font color=blue> </font> <BR>
<B>Irresistible throws a straight right to the nose.  </B><BR>
Irresistible lashes out with a hook to the head, but ClinchGeneralNusuki ties him up .<BR>
ClinchGeneralNusuki launches an uppercut to the ribs, but falls short .<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
...<BR>
Irresistible feints with a uppercut.  <BR>
<B>ClinchGeneralNusuki jars Irresistible with a big sweeping right to the head!! The crowd is on its feet!!  <font color=blue></font> </B><BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
Irresistible launches a hook to the jaw, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 36 of 60 punches -- 13 power punches, 10 jabs, 13 rights.  (111 points)<BR>ClinchGeneralNusuki landed 9 of 37 punches -- 6 power punches, 0 jabs, 3 rights.  (33 points)<BR><BR>"Irresistible" Emma Starr won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 20-18.  <BR>
<BR>
<BR>
Irresistible remains standing while the trainer wipes him down.<BR>
<BR>
ClinchGeneralNusuki remains standing while the trainer wipes him down.<BR>
<BR>
<BR>

<BR><HR> ROUND 3<HR><BR>
Irresistible feints and fakes (feinting) and goes to the body.<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and goes to the body.<BR>
<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
...<BR>
Irresistible charges with a hook to the stomach, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
<B>ClinchGeneralNusuki throws a quick cross to the ribs.  </B>Irresistible ignores it.<font color=blue> </font> <BR>
...<BR>
ClinchGeneralNusuki attempts an uppercut to the stomach, but doesn''t quite connect .<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
ClinchGeneralNusuki throws a hook to the chest, but Irresistible slips it .<BR>
ClinchGeneralNusuki throws a straight right to the nose, but Irresistible slips it .<BR>
...<BR>
...<BR>
<B>Irresistible feints with a right but then attacks with a hook to the stomach.  </B><BR>
...<BR>
ClinchGeneralNusuki fires an overhand right to the stomach, but Irresistible deflects it .<BR>
Irresistible attempts an overhand right to the head, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
ClinchGeneralNusuki tries to land an uppercut to the solar plexus, but Irresistible pushes away .<BR>
<B>Irresistible feints with a right but then lands a sweeping right to the stomach.  </B><BR>
...<BR>
...<BR>
...<BR>
Irresistible throws an uppercut to the solar plexus, but can''t connect .<BR>
ClinchGeneralNusuki lunges with a left to the stomach, but Irresistible takes it on the gloves .<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
<B>Irresistible feints with a right but then throws a sweeping right to the stomach.  </B>ClinchGeneralNusuki ignores it.<font color=blue> </font> <BR>
<B>Irresistible feints with a right but then lands a straight right to the head.  </B><BR>
...<BR>
...<BR>
...<BR>
Irresistible lunges with a right hand to the ribs, but it''s short .<BR>
Irresistible lunges with a sweeping right to the stomach, but comes up empty .<BR>
...<BR>
...<BR>
...<BR>
Irresistible charges with a cross to the stomach, but he''s off balance .<BR>
...<BR>
<B>ClinchGeneralNusuki wallops Irresistible with a big uppercut to the chest!! The crowd is on its feet!!  <font color=blue></font> </B><BR>
...<BR>
<B>Irresistible feints with a right but then hits ClinchGeneralNusuki with a hook to the stomach.  </B><BR>
Irresistible charges with a left to the chest, but misses completely .<BR>
Irresistible feints with a right.  <BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 20 of 46 punches -- 9 power punches, 2 jabs, 9 rights.  (67 points)<BR>ClinchGeneralNusuki landed 8 of 33 punches -- 5 power punches, 0 jabs, 3 rights.  (29 points)<BR><BR>"Irresistible" Emma Starr won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 30-27.  <BR>
<BR>
<BR>
Irresistible grabs a water bottle and rests on his stool.<BR>
<BR>
ClinchGeneralNusuki remains standing while the trainer wipes him down.<BR>
<BR>
<BR>

<BR><HR> ROUND 4<HR><BR>
Irresistible feints and fakes (feinting) and goes to the body.<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and goes to the body.<BR>
<BR>
ClinchGeneralNusuki launches an uppercut to the stomach, but Irresistible knocks it away .<BR>
Irresistible tries to land an uppercut to the stomach, but ClinchGeneralNusuki ties him up .<BR>
...<BR>
Irresistible feints with a hook.  <BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki tries a hook to the chest, but Irresistible takes it on the gloves .<BR>
...<BR>
...<BR>
...<BR>
The referee warns ClinchGeneralNusuki about holding and hitting.<BR>
...<BR>
...<BR>
<B>Irresistible feints with a left but then fires a clean roundhouse to the stomach.  </B><BR>
...<BR>
...<BR>
<B>Irresistible fires a sweeping right to the stomach.  </B><BR>
...<BR>
...<BR>
...<BR>
The referee warns ClinchGeneralNusuki about holding and hitting.<BR>
ClinchGeneralNusuki fires a roundhouse to the ribs, but Irresistible pushes away .<BR>
<B>Irresistible throws a quick hook to the stomach.  </B>ClinchGeneralNusuki sneers!<font color=blue> </font> <BR>
Irresistible tries to land a hook to the stomach, but it''s short .<BR>
Irresistible lunges with a jab to the solar plexus, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
ClinchGeneralNusuki tries a right hand to the ribs, but misses completely .<BR>
...<BR>
...<BR>
...<BR>
<B>Irresistible feints with a left but then throws a clean left to the nose.  </B><BR>
Irresistible reaches with an uppercut to the chest, but ClinchGeneralNusuki ties him up .<BR>
Irresistible fires a left to the stomach, but falls short .<BR>
ClinchGeneralNusuki lunges with a roundhouse to the stomach, but Irresistible takes it in the forearms .<BR>
<B>ClinchGeneralNusuki scores with a right to the stomach.  </B>Irresistible covers up.<BR>
...<BR>
<B>ClinchGeneralNusuki slams Irresistible with a vicious uppercut to the ribs!! The crowd roars!! </B><BR>
Irresistible lunges with a left to the stomach, but misses completely .<BR>
Irresistible launches a roundhouse to the ribs, but doesn''t really connect .<BR>
Irresistible tries to land a cross to the solar plexus, but falls short .<BR>
...<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
Irresistible lunges with a straight right to the chest, but ClinchGeneralNusuki ties him up .<BR>
<B>Irresistible hits ClinchGeneralNusuki with a right hand to the head.  </B>ClinchGeneralNusuki quickly recovers.<BR>
ClinchGeneralNusuki attempts a straight right to the stomach, but Irresistible pushes away .<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
ClinchGeneralNusuki attacks with a cross to the stomach, but Irresistible takes it on the gloves .<BR>
...<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 18 of 53 punches -- 8 power punches, 2 jabs, 8 rights.  (60 points)<BR>ClinchGeneralNusuki landed 8 of 35 punches -- 5 power punches, 0 jabs, 3 rights.  (29 points)<BR><BR>"Irresistible" Emma Starr won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 40-36.  <BR>
<BR>
<BR>
Irresistible is obviously tired.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>

<BR><HR> ROUND 5<HR><BR>
Irresistible feints and fakes (feinting) and goes to the body.<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and goes to the body.<BR>
<BR>
ClinchGeneralNusuki launches an overhand right to the stomach, but Irresistible deflects it .<BR>
...<BR>
ClinchGeneralNusuki throws an uppercut to the solar plexus, but comes up empty .<BR>
ClinchGeneralNusuki probes with a hook to the ribs, but Irresistible knocks it away .<BR>
Irresistible attempts an overhand right to the stomach, but ClinchGeneralNusuki ties him up .<BR>
...<BR>
ClinchGeneralNusuki probes with an overhand right to the chest, but Irresistible blocks it .<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
Irresistible reaches with a right to the stomach, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
<B>ClinchGeneralNusuki slams Irresistible with a big right to the stomach!! The crowd is on its feet!!  <font color=blue></font> </B><BR>
Irresistible throws a roundhouse to the ribs, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
Irresistible throws a hook to the ribs, but ClinchGeneralNusuki falls into a clinch .<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
<B>Irresistible connects with a hook to the temple.  </B><BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
ClinchGeneralNusuki throws a straight right to the stomach, but Irresistible pushes away .<BR>
...<BR>
...<BR>
...<BR>
<B>Irresistible feints with a left but then belts ClinchGeneralNusuki with a hard overhand right to the chest!  </B>ClinchGeneralNusuki hangs on until the referee breaks them up.<BR>
Irresistible tries to land an uppercut to the chest, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
...<BR>
Irresistible feints with a roundhouse.  <BR>
<B>ClinchGeneralNusuki fires a hook to the chest.  </B><BR>
ClinchGeneralNusuki attempts an overhand right to the stomach, but Irresistible takes it on the gloves .<BR>
ClinchGeneralNusuki attempts an overhand right to the stomach, but Irresistible blocks it .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki throws a right to the stomach, but misses completely .<BR>
Irresistible throws a right hand to the ribs, but ClinchGeneralNusuki ties him up .<BR>
Irresistible reaches with a jab to the ribs, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
Irresistible fires a left to the chest, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
<B>Irresistible connects with a right hand to the stomach.  </B><BR>
<B>Irresistible annoys ClinchGeneralNusuki with a straight right to the stomach.  </B>ClinchGeneralNusuki sneers!<font color=blue> </font> <BR>
<B>Irresistible annoys ClinchGeneralNusuki with a sweeping right to the temple.  </B>ClinchGeneralNusuki ignores it.<font color=blue> </font> <BR>
...<BR>
ClinchGeneralNusuki throws a straight right to the ribs, but Irresistible deflects it .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 18 of 50 punches -- 8 power punches, 2 jabs, 8 rights.  (60 points)<BR>ClinchGeneralNusuki landed 8 of 44 punches -- 5 power punches, 0 jabs, 3 rights.  (29 points)<BR><BR>"Irresistible" Emma Starr won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 50-45.  <BR>
<BR>
<BR>
Irresistible is obviously tired.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>

<BR><HR> ROUND 6<HR><BR>
Irresistible feints and fakes (feinting) and goes to the body.<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and goes to the body.<BR>
<BR>
...<BR>
ClinchGeneralNusuki charges with a cross to the chin, but Irresistible pushes away .<BR>
Irresistible lunges with a hook to the ribs, but falls short .<BR>
ClinchGeneralNusuki tries a roundhouse to the head, but Irresistible knocks it away .<BR>
ClinchGeneralNusuki probes with a hook to the stomach, but Irresistible slips it .<BR>
Irresistible charges with a right hand to the head, but ClinchGeneralNusuki ties him up .<BR>
Irresistible feints with a cross.  <BR>
...<BR>
...<BR>
...<BR>
...<BR>
Irresistible charges with an uppercut to the chest, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
...<BR>
...<BR>
<B>Irresistible connects with a right to the stomach.  </B><BR>
<B>Irresistible feints with a right but then punches ClinchGeneralNusuki with a cross to the ribs.  </B><BR>
...<BR>
...<BR>
ClinchGeneralNusuki attacks with a hook to the ribs, but Irresistible slips it .<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
Irresistible tries a roundhouse to the solar plexus, but goes wide .<BR>
...<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
...<BR>
Irresistible launches a left to the solar plexus, but can''t connect .<BR>
...<BR>
ClinchGeneralNusuki lunges with a cross to the solar plexus, but Irresistible blocks .<BR>
...<BR>
<B>ClinchGeneralNusuki jars Irresistible with a big uppercut to the chest!! The crowd is on its feet!!  <font color=blue></font> </B><BR>
Irresistible lunges with a left to the stomach, but ClinchGeneralNusuki ties him up .<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
...<BR>
...<BR>
...<BR>
...<BR>
Irresistible tries to land a jab to the solar plexus, but ClinchGeneralNusuki ties him up .<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
ClinchGeneralNusuki throws a hook to the stomach, but Irresistible slips it .<BR>
...<BR>
ClinchGeneralNusuki tries to land a hook to the ribs, but falls short .<BR>
Irresistible attacks with a hook to the stomach, but doesn''t quite connect .<BR>
...<BR>
<B>Irresistible feints with a left but then connects with an uppercut to the stomach.  </B><BR>
...<BR>
...<BR>
...<BR>
...<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 13 of 43 punches -- 6 power punches, 1 jab, 6 rights.  (44 points)<BR>ClinchGeneralNusuki landed 4 of 30 punches -- 3 power punches, 0 jabs, 1 right.  (15 points)<BR><BR>"Irresistible" Emma Starr won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 60-54.  <BR>
<BR>
<BR>
Irresistible is sucking wind.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>

<BR><HR> ROUND 7<HR><BR>
Irresistible feints and fakes (feinting) and goes to the body.<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and goes to the body.<BR>
<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
Irresistible fires an overhand right to the solar plexus, but ClinchGeneralNusuki falls into a clinch .<BR>
ClinchGeneralNusuki probes with a hook to the ribs, but is ineffective .<BR>
ClinchGeneralNusuki probes with an uppercut to the stomach, but it''s weak .<BR>
<B>ClinchGeneralNusuki jars Irresistible with a painful uppercut to the ribs!! The crowd is on its feet!!  <font color=blue></font> </B>Irresistible grimaces in pain.<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
...<BR>
...<BR>
Irresistible lunges with a jab to the stomach, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
Irresistible fires a sweeping right to the stomach, but ClinchGeneralNusuki ties him up .<BR>
Irresistible tries to land a hook to the temple, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
...<BR>
Irresistible tries to land a cross to the stomach, but ClinchGeneralNusuki falls into a clinch .<BR>
ClinchGeneralNusuki tries to land an uppercut to the head, but Irresistible knocks it away .<BR>
...<BR>
ClinchGeneralNusuki attempts a right to the mouth, but can''t connect .<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki fires a roundhouse to the mouth, but falls short .<BR>
...<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
<B>Irresistible feints with a left but then throws a quick hook to the solar plexus.  </B><BR>
Irresistible feints with a hook.  <BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki attempts a cross to the ribs, but Irresistible pushes away .<BR>
...<BR>
<B>Irresistible annoys ClinchGeneralNusuki with a clean straight right to the head.  </B><BR>
Irresistible lashes out with an overhand right to the stomach, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
...<BR>
Irresistible reaches with a straight right to the mouth, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
Irresistible throws a hook to the solar plexus, but it''s too slow .<BR>
...<BR>
...<BR>
<B>Irresistible feints with a left but then fires a sweeping right to the ribs.  </B><BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 11 of 44 punches -- 5 power punches, 1 jab, 5 rights.  (37 points)<BR>ClinchGeneralNusuki landed 5 of 30 punches -- 4 power punches, 0 jabs, 1 right.  (19 points)<BR><BR>"Irresistible" Emma Starr won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 70-63.  <BR>
<BR>
<BR>
Irresistible is sucking wind.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>

<BR><HR> ROUND 8<HR><BR>
Irresistible covers up and he''s head hunting.<BR>
ClinchGeneralNusuki is clinching a lot (clinching).<BR>
<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
Irresistible launches a hook to the jaw, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
ClinchGeneralNusuki fires an uppercut to the stomach, but Irresistible blocks it .<BR>
<B>ClinchGeneralNusuki lands a quick jab to the head.  </B>Irresistible sneers!<font color=blue> </font> <BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki lunges with a sweeping right to the jaw, but Irresistible covers himself well .<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
<B>Irresistible scores with a clean hook to the nose.  </B>ClinchGeneralNusuki quickly recovers.<BR>
...<BR>
...<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
ClinchGeneralNusuki attempts a left to the solar plexus, but doesn''t quite connect .<BR>
...<BR>
Irresistible reaches with a hook to the head, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
Irresistible lashes out with a hook to the jaw, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
ClinchGeneralNusuki attacks with an uppercut to the head, but Irresistible ducks .<BR>
Irresistible launches a left to the chin, but ClinchGeneralNusuki ties him up .<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki reaches with a right hand to the stomach, but Irresistible slips it .<BR>
ClinchGeneralNusuki attacks with a jab to the stomach, but doesn''t land it very well .<BR>
...<BR>
...<BR>
Irresistible throws a left to the eye, but he''s off balance .<BR>
<B>ClinchGeneralNusuki fires a hook to the mouth.  </B><BR>
...<BR>
<B>ClinchGeneralNusuki clocks Irresistible with an excellent right hand to the chin.  </B><BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
ClinchGeneralNusuki tries to land a jab to the head, but Irresistible evades it .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki charges with a jab to the mouth, but comes up empty .<BR>
...<BR>
ClinchGeneralNusuki throws a hook to the head, but Irresistible hides behind his gloves .<BR>
...<BR>
...<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 4 of 25 punches -- 3 power punches, 0 jabs, 1 right.  (15 points)<BR>ClinchGeneralNusuki landed 13 of 50 punches -- 4 power punches, 5 jabs, 4 rights.  (38 points)<BR><BR>ClinchGeneralNusuki won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 79-73.  <BR>
<BR>
<BR>
Irresistible is sucking wind.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>

<BR><HR> ROUND 9<HR><BR>
Irresistible covers up and he''s head hunting.<BR>
ClinchGeneralNusuki is clinching a lot (clinching).<BR>
<BR>
...<BR>
ClinchGeneralNusuki lunges with an uppercut to the temple, but Irresistible covers up .<BR>
Irresistible fires a roundhouse to the eye, but ClinchGeneralNusuki falls into a clinch .<BR>
<B>ClinchGeneralNusuki surprises Irresistible with a jab to the eye.  </B>Irresistible covers up.<BR>
ClinchGeneralNusuki launches a jab to the solar plexus, but is ineffective .<BR>
Irresistible fires an overhand right to the chin, but it''s weak .<BR>
...<BR>
Irresistible charges with an uppercut to the nose, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
...<BR>
...<BR>
ClinchGeneralNusuki attempts a right to the temple, but doesn''t land it very well .<BR>
Irresistible lunges with a roundhouse to the mouth, but comes up empty .<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
...<BR>
ClinchGeneralNusuki fires a jab to the face, but Irresistible ducks .<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki tries to land a left to the chin, but Irresistible covers himself well .<BR>
The referee admonishes ClinchGeneralNusuki to stop clinching.<BR>
ClinchGeneralNusuki lunges with a hook to the mouth, but Irresistible evades it .<BR>
ClinchGeneralNusuki reaches with a hook to the stomach, but Irresistible covers himself well .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki lunges with a jab to the mouth, but Irresistible ducks .<BR>
...<BR>
<B>Irresistible hits ClinchGeneralNusuki with a hook to the nose.  </B><BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki throws a left to the temple, but Irresistible covers himself well .<BR>
<B>ClinchGeneralNusuki takes charge with a wild overhand right to the stomach.  </B><BR>
<B>ClinchGeneralNusuki annoys Irresistible with a right to the head.  </B><BR>
Irresistible launches a right hand to the stomach, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
Irresistible probes with a hook to the head, but ClinchGeneralNusuki hangs on until the referee breaks them up .<BR>
ClinchGeneralNusuki throws an uppercut to the eye, but Irresistible ducks .<BR>
...<BR>
...<BR>
Irresistible tries a left to the chin, but ClinchGeneralNusuki ties him up .<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 4 of 33 punches -- 3 power punches, 0 jabs, 1 right.  (15 points)<BR>ClinchGeneralNusuki landed 10 of 49 punches -- 3 power punches, 4 jabs, 3 rights.  (29 points)<BR><BR>ClinchGeneralNusuki won the round 10-9 by landing more punches.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 88-83.  <BR>
<BR>
<BR>
Irresistible is sucking wind.  He has a  cut below his right eye.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>

<BR><HR> ROUND 10<HR><BR>
Irresistible covers up and he''s head hunting.<BR>
ClinchGeneralNusuki is clinching a lot (clinching) and he''s head hunting.<BR>
<BR>
...<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
<B>Irresistible fires a roundhouse to the head.  </B>ClinchGeneralNusuki covers up.<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki probes with an overhand right to the nose, but Irresistible covers himself well .<BR>
Irresistible tries to attack, but ClinchGeneralNusuki hangs on until the referee separates them.<BR>
...<BR>
ClinchGeneralNusuki reaches with a sweeping right to the chest, but Irresistible blocks it .<BR>
...<BR>
...<BR>
...<BR>
<B>ClinchGeneralNusuki pops Irresistible with a hook to the nose.  </B><BR>
...<BR>
...<BR>
ClinchGeneralNusuki fires a roundhouse to the temple, but doesn''t land it very well .<BR>
Irresistible launches an uppercut to the head, but misses .<BR>
...<BR>
ClinchGeneralNusuki attacks with a hook to the chin, but Irresistible ducks .<BR>
ClinchGeneralNusuki lashes out with a hook to the temple, but Irresistible slips it .<BR>
<B>ClinchGeneralNusuki slams Irresistible with a big hook to the head!! The crowd is on its feet!!  <font color=blue></font> <font color=red>Irresistible stumbles, but remains on his feet!  He looks hurt!!</font></B><BR>
...<BR>
Irresistible reaches with a cross to the face, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
...<BR>
Irresistible probes with an uppercut to the head, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
Irresistible tries to close, but ClinchGeneralNusuki ties him up.<BR>
ClinchGeneralNusuki fires an overhand right to the face, but falls short .<BR>
ClinchGeneralNusuki throws a hook to the temple, but Irresistible blocks it .<BR>
...<BR>
Irresistible charges with a hook to the head, but ClinchGeneralNusuki falls into a clinch .<BR>
...<BR>
ClinchGeneralNusuki attacks with a cross to the head, but is ineffective .<BR>
Irresistible tries to land a right hand to the mouth, but it''s short .<BR>
...<BR>
ClinchGeneralNusuki charges with an uppercut to the chin, but Irresistible ducks .<BR>
...<BR>
Irresistible tries a hook to the chin, but it''s short .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
<BR>
BELL!<BR>
<BR>
<P>According to the Commentators: <BR>
<BR>"Irresistible" Emma Starr landed 3 of 27 punches -- 2 power punches, 0 jabs, 1 right.  (11 points)<BR>ClinchGeneralNusuki landed 8 of 42 punches -- 6 power punches, 0 jabs, 2 rights.  (30 points)<BR><BR>ClinchGeneralNusuki won the round 10-9 by stunning Irresistible.<BR>
<BR>"Irresistible" Emma Starr is winning the fight 97-93.  <BR>
<BR>
<BR>
Irresistible is sucking wind.  He has a  cut below his right eye.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>

<BR><HR> ROUND 11<HR><BR>
Irresistible covers up and he''s head hunting.<BR>
ClinchGeneralNusuki goes toe-to-toe (inside) and he''s head hunting.<BR>
<BR>
ClinchGeneralNusuki launches an uppercut to the nose, but Irresistible ducks .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki attempts a straight right to the jaw, but Irresistible evades it .<BR>
ClinchGeneralNusuki launches an uppercut to the head, but Irresistible slips it .<BR>
...<BR>
Irresistible attempts an uppercut to the head, but ClinchGeneralNusuki covers up .<BR>
...<BR>
ClinchGeneralNusuki charges with a hook to the nose, but Irresistible slips it .<BR>
...<BR>
Irresistible lunges with an uppercut to the eye, but ClinchGeneralNusuki ducks .<BR>
...<BR>
<B>ClinchGeneralNusuki jars Irresistible with a big straight right to the chin!! The crowd is on its feet!!  <font color=blue></font> </B><BR>
...<BR>
ClinchGeneralNusuki launches a straight right to the head, but Irresistible blocks it .<BR>
...<BR>
...<BR>
...<BR>
Irresistible charges with a roundhouse to the head, but ClinchGeneralNusuki knocks it away .<BR>
<B>Irresistible lashes out with a solid uppercut to the stomach.  </B><BR>
Irresistible charges with a left to the head, but fails to score .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
ClinchGeneralNusuki launches an uppercut to the head, but Irresistible slips it .<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
...<BR>
<B>ClinchGeneralNusuki backs up Irresistible with a hard hook to the head.  </B><BR>
ClinchGeneralNusuki charges with an uppercut to the eye, but Irresistible blocks it .<BR>
<BR>
...<BR>
...<BR>
<font color=red><BR><B> ClinchGeneralNusuki lands a telling right uppercut and Irresistible is knocked down!! <BR><BR>ONE!  <BR>  <BR>TWO!  <BR>  <BR>THREE!  <BR>  <BR>FOUR!  <BR>  <BR>FIVE!  <BR>  <BR>SIX!  <BR>  <BR>SEVEN!  <BR>  <BR>EIGHT!  <BR>  <BR> NINE!  <BR><BR> TEN! <BR>  He''s out!!!</B><BR>
ClinchGeneralNusuki <B>wins by a Knock Out!!</B></font><BR>
<BR><B>Time: 2:36</B>
<P><BR>
Irresistible looks exhausted.  He has  swelling around his left eye.  He has a  cut below his right eye.<BR>
<BR>
ClinchGeneralNusuki grabs a water bottle and rests on his stool.<BR>
<BR>
<BR>
<BR><HR><BR><BR><BR><BR><P><strong>Judge Roy Bean </strong> had the fight scored as follows: <BR><BR>Round 1:  "Irresistible" Emma Starr 10-9<BR>
Round 2:  "Irresistible" Emma Starr 10-9<BR>
Round 3:  "Irresistible" Emma Starr 10-9<BR>
Round 4:  "Irresistible" Emma Starr 10-9<BR>
Round 5:  "Irresistible" Emma Starr 10-9<BR>
Round 6:  "Irresistible" Emma Starr 10-9<BR>
Round 7:  "Irresistible" Emma Starr 10-9<BR>
Round 8:  ClinchGeneralNusuki 10-9<BR>
Round 9:  ClinchGeneralNusuki 10-9<BR>
Round 10:  ClinchGeneralNusuki 10-9<BR>
<BR><BR><P><strong>Judge Judy </strong> had the fight scored as follows: <BR><BR>Round 1:  "Irresistible" Emma Starr 10-9<BR>
Round 2:  "Irresistible" Emma Starr 10-9<BR>
Round 3:  "Irresistible" Emma Starr 10-9<BR>
Round 4:  "Irresistible" Emma Starr 10-9<BR>
Round 5:  "Irresistible" Emma Starr 10-9<BR>
Round 6:  "Irresistible" Emma Starr 10-9<BR>
Round 7:  "Irresistible" Emma Starr 10-9<BR>
Round 8:  ClinchGeneralNusuki 10-9<BR>
Round 9:  ClinchGeneralNusuki 10-9<BR>
Round 10:  ClinchGeneralNusuki 10-9<BR>
<BR><BR><P><strong>Judge Lao Mang Chen </strong> had the fight scored as follows: <BR><BR>Round 1:  "Irresistible" Emma Starr 10-9<BR>
Round 2:  "Irresistible" Emma Starr 10-9<BR>
Round 3:  "Irresistible" Emma Starr 10-9<BR>
Round 4:  "Irresistible" Emma Starr 10-9<BR>
Round 5:  "Irresistible" Emma Starr 10-9<BR>
Round 6:  "Irresistible" Emma Starr 10-9<BR>
Round 7:  "Irresistible" Emma Starr 10-9<BR>
Round 8:  ClinchGeneralNusuki 10-9<BR>
Round 9:  ClinchGeneralNusuki 10-9<BR>
Round 10:  ClinchGeneralNusuki 10-9<BR>
<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>
</BODY></HTML>


"""


gul = """
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
<A name="guljames" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_career_privatebyid&+competition=eko&+division=Heavy&+region=Contenders&+team_id=1650094">Gul`james<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A> </B> (41-29-0 41/20)<BR>
<table border=1>
<TR><TD>Strength <TD align=right>25<BR>
<TD>Knockout Punch <TD  align=right>8<BR>
<TR><TD>Speed <TD align=right>14<BR>
<TD>Agility <TD align=right>16<BR>
<TR><TD>Chin <TD align=right>16<BR>
<TD>Conditioning <TD align=right>6<BR>
<TR><TD>Cut Resistance <TD align=right>Low<BR>
<TD><a target=glossary onClick=help() href=https://cloudfront-webl.vivi.com/eko/glossary.html#streak>Winning Streak</A><TD align=right>0<TR><TD><script language=javascript>
    <!--
    function help() {
        window.open("", "glossary", "width=550,height=300,resizable=1,scrollbars=1");
    }
    //-->
</script>
<a href=https://cloudfront-webl.vivi.com/eko/glossary.html#rating target=glossary onClick=help()>Rating</A><TD align=right>16
<TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#status target=glossary onClick=help()>Status</A><TD align=right>18
<TR><TD>Rank<TD align=right>24
<TD>Total Earnings:<TD align=right>  $29,413,384 <TR><TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#injury target=glossary onClick=help()>Injury Points</A><TD align=right>424
<TD>AP Loss</A><TD align=right>0
<TR><TD>Height<TD colspan=3>5 feet 9 inches (175 centimeters)
<TR><TD>Build<TD colspan=3>normal
<TR><TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#fweight target=glossary onClick=help()>Weight</A> <TD colspan=3>172 pounds (78 kilograms)
<TR><TD><a href=https://cloudfront-webl.vivi.com/eko/glossary.html#minweight target=glossary onClick=help()>Minimum Weight</A> <TD colspan=3>168 pounds (76 kilograms)
</table>
<P>Gul`james fights in the <A name="Light-Heavyweight" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_standings&+competition=eko&+division=Light-Heavy&+region=Eurasia&team=guljames">Light-Heavyweight</A> division.  <P>Gul`james's next opponent is the 5 feet 6 inches, 
<A name="dariusmountainbikeatkins" HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=eko_careerbyid&+competition=eko&+division=Heavy&+region=Contenders&+team_id=1654696&describe=1">Darius "Mountain Bike" ATKINS<IMG SRC="https://webl-images.vivi.com/regional_champion.gif" ALT="regional_champion"
                              border=0 align=bottom></A>  (40-31-1 39/31)  from the 
<A HREF="https://webl.vivi.com/cgi-bin/query.fcgi?competition=eko&command=eko_managerbyid&manager_to_view=245353">Melchester Rovers</A> gym  for   $1,310,720  on <B>Friday, December 26, 2025.</B>
<P>Gul`james is training <b>knockout punch</b>, but you can instruct him to <A  HREF="/cgi-bin/prompt.fcgi?+command=eko_training&+competition=eko&+division=Heavy&+region=Contenders&+team=Gul`james">train for something else</A>.<P>Gul`james is currently using the <b>5H87ringR1</b> fight plan. 
He may <UL>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_select_orders&+competition=eko&+division=Heavy&+region=Contenders&+team=Gul`james">choose a different fight plan</A>, 
<LI><A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_echo&+competition=eko&+division=Heavy&+filename=fightplan_beginner.html&+region=Contenders&team=guljames">create a new fight plan</A>  
<LI>or <A  HREF="/cgi-bin/prompt.fcgi?+command=query_edit_orders&+competition=eko&+division=Heavy&+region=Contenders&+strategy_choice=5H87ringR1&strategy_id=1922845">edit</A> your <B>5H87ringR1</B> plan.

<LI>Experts can use the <A  HREF="/cgi-bin/prompt.fcgi?+command=query_orders&+competition=eko&+division=Heavy&+region=Contenders&+team=Gul`james">advanced fight plan form</A>.

<LI>Beginners might want to get into the ring with a  <A  HREF="https://webl.vivi.com/cgi-bin/query.fcgi?+command=query_echo&+competition=eko&+division=Heavy&+filename=newbie_form.html&+region=Contenders&cname=guljames&fighter_name=Gul`james&team_id=1650094">sparring partner.</A>

</UL>
<P>Gul`james may also do any of the following:<UL>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=query_press&+competition=eko&+division=Heavy&+region=Contenders&+team=Gul`james&team_id=1650094">issue a press release.</A> 
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_change_division&+competition=eko&+division=Heavy&+region=Contenders&+team=Gul`james">change weight division.</A>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_rename&+competition=eko&+division=Heavy&+region=Contenders&+team=Gul`james">change his description.</A>
<LI><A  HREF="/cgi-bin/prompt.fcgi?+command=eko_retire_byid&+competition=eko&+division=Heavy&+region=Contenders&+team_id=1650094">retire.</A></UL>

</BODY></HTML>
"""

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
    wgtval = round((hgtval + 60.0) ** 3.0 * (0.0005 + bldval * 0.00001) *
        (1.0 + (math.sqrt(strval - 10.0) if (strval > 10) else -math.sqrt(10.0 - strval)) * 0.05) *
        (1.0 - (math.sqrt(aglval - 10.0) if (aglval > 10) else -math.sqrt(10.0 - aglval)) * 0.05) - 0.49999)
    return wgtval, round(wgtval * (0.995 - cndval * 0.0025))

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
    data['NAME'] = m.group(1).strip() if m else ""

    # Numeric stats
    def find_int(pattern, default=0):
        mm = re.search(pattern, html, re.IGNORECASE)
        return int(mm.group(1)) if mm and mm.group(1).isdigit() else default

    data['STRENGTH'] = find_int(r"[Dd]>[Ss]trength[^0-9]+(\d+)")
    data['KP'] = find_int(r"[Dd]>[Kk]nockout[^0-9]+(\d+)")
    data['SPEED'] = find_int(r"[Dd]>[Ss]peed[^0-9]+(\d+)")
    data['AGILITY'] = find_int(r"[Dd]>[Aa]gility[^0-9]+(\d+)")
    data['CHIN'] = find_int(r"[Dd]>[Cc]hin[^0-9]+(\d+)")
    data['CONDITIONING'] = find_int(r"[Dd]>[Cc]onditioning[^0-9]+(\d+)")
    # CUT: map "Cut Resistance <...>ight>(word)"
    m = re.search(r"Cut Resistance <[^>]*>([a-zA-Z]+)", html)
    if m:
        try:
            cutval = m.group(1).strip().lower()
            data['CUT'] = next((k for k, v in CUTS_STR.items() if v == cutval), 0)
        except Exception:
            data['CUT'] = 0
    else:
        data['CUT'] = 0

    data['RATING'] = find_int(r"Rating[^0-9]+ight>(\d+)")
    data['STATUS'] = find_int(r"Status[^0-9]+ight>(\d+)")

    # Height: "Height<TD colspan=3>(\d+) feet ?([0-9]{0,2})"
    m = re.search(r"Height<TD colspan=3>(\d+)\s*feet\s*([0-9]{0,2})", html)
    if m:
        data['HEIGHT'] = convert_height(int(m.group(1)), int(m.group(2) or 0))
    else:
        data['HEIGHT'] = 0

    # Build
    m = re.search(r"Build<TD colspan=3>([a-zA-Z ]+)", html)
    if m:
        build_str = m.group(1).strip().lower()
        # reverse mapping: find key in BUILD_STR with matching string
        found = next((k for k, v in BUILD_STR.items() if v.lower() == build_str), 0)
        data['BUILD'] = found
    else:
        data['BUILD'] = 0

    # Weight computed
    data['WEIGHT'] = compute_weight(data['HEIGHT'], data['STRENGTH'], data['AGILITY'], data['CONDITIONING'], data['BUILD'])

    # IPS (Injury Points) and AP Loss stuff approximation; the PHP added AP Loss * 500 if present
    m = re.search(r"Injury Points<[^0-9]+ight>(\d+)", html)
    if m:
        ips = int(m.group(1))
        # try AP Loss
        m2 = re.search(r"AP Loss<[^0-9]+ight>(\d+)", html)
        if m2:
            ap_loss = int(m2.group(1))
            ips += ap_loss * 500
        data['IPS'] = ips
    else:
        data['IPS'] = 0

    # RECORD: multiple patterns
    recs = re.findall(r"([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+)\/([0-9]+)", html)
    data['RECORD'] = recs if recs else None

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
        data['DIVISIONS'] = [div_idx, region]
    else:
        data['DIVISIONS'] = None

    # OPPONENT: pattern that contains feet, inches, team_id, and name
    m = re.search(r" ([0-9]) feet *([0-9]{0,2})[^>]*team_id=([0-9]+)&describe=[0-9]\">(.*)<[I\/][AM][G>]", html)
    if m:
        opp_height = convert_height(int(m.group(1)), int(m.group(2) or 0))
        opp_team = int(m.group(3))
        opp_name = m.group(4).strip()
        data['OPPONENT'] = [opp_height, opp_team, opp_name, 0]
    else:
        data['OPPONENT'] = None

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
        data['TRAINING'] = [t1_idx, t2_idx, "(intensive)" in html]
    else:
        data['TRAINING'] = None

    # TYPE filled by later matching logic
    data['TYPE'] = 0

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
        baseaps = data['STRENGTH'] + data['SPEED'] + data['AGILITY']
        matchdiff = 1e9
        chosen_type = 0
        for i, t in enumerate(types):
            diff = abs(baseaps * (1.0 - t['SPEED'] - t['AGILITY']) - data['STRENGTH']) \
                   + abs(baseaps * t['SPEED'] - data['SPEED']) \
                   + abs(baseaps * t['AGILITY'] - data['AGILITY'])
            if diff < matchdiff:
                matchdiff = diff
                chosen_type = i
        data['TYPE'] = chosen_type

        # Update typesbyheight counts
        hb = data['HEIGHT']
        typesbyheight[data['TYPE']][hb] = typesbyheight[data['TYPE']].get(hb, 0) + 1

        # Retirement logic: PHP: if ($data['STATUS'] > 0 && $data['IPS'] / ($data['STATUS'] + 0.01) > 38.0) retire
        if data.get("STATUS", 0) > 0:
            if data['IPS'] / (data['STATUS'] + 0.01) > 38.0:
                write_msg("eko_retire_byid", f"verify_retire=1&+team_id={tid}")

        # find correct weight division; PHP loop: for ($i = count($divis_str) - 1; $i >= 0 && $data['WEIGHT'][1] <= $max_weights[$i]; $i--)
        # In PHP they used $max_weights with index -1..16; we approximate by scanning division indices descending
        try:
            current_div_idx = data['DIVISIONS'][0] if data.get("DIVISIONS") else None
        except Exception:
            current_div_idx = None
        # find division by comparing cutweight (data['WEIGHT'][1]) to MAX_WEIGHTS
        cutwt = data['WEIGHT'][1]
        found_div = None
        # iterate division indexes descending (16 down to 0)
        for i in range(len(DIVISIONS)-1, -1, -1):
            maxw_for_i = MAX_WEIGHTS.get(i, 1000)  # fallback
            prior_max = MAX_WEIGHTS.get(i-1, -1)
            if cutwt <= maxw_for_i:
                # ensure > previous, similar to PHP: if ($data['WEIGHT'][1] > $max_weights[$i - 1] && $i != $data['DIVISIONS'][0])
                if cutwt > prior_max:
                    found_div = i
                break
        if found_div is not None and current_div_idx is not None and found_div != current_div_idx:
            # request change division
            write_msg("eko_change_division", f"your_team={data['NAME']}&division={DIVISIONS[found_div]}weight")
            if data.get("DIVISIONS"):
                data['DIVISIONS'][0] = found_div

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
        if data['OPPONENT'] is not None:
            opp_team_id = data['OPPONENT'][1]
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
                            opptacs['ROUNDS'] += 1
                            opptacs['STYLES'][code] += 1
                    # aims detection
                    if "goes to the body" in rb:
                        opptacs['AIMS'][1] += 1
                    if "jabs for the cut" in rb:
                        opptacs['AIMS'][2] += 1
                    if "head hunting" in rb or "head-hunting" in rb:
                        opptacs['AIMS'][4] += 1
                    # detect words implying powerpunches / stunning
                    if "stunning" in rb or "knockdown" in rb or "dominating" in rb:
                        opptacs['KP'] += 1  # small heuristic
                bouts.append(rb)
            # short KP/opponent stats based on PHP: count early-round KOs less than round 3
            if scout_html:
                early_kos = re.findall(r"n by \w* in round (\d+)", scout_html)
                for k in early_kos:
                    try:
                        if int(k) < 3 and data['OPPONENT'] is not None:
                            data['OPPONENT'][3] += 1
                    except Exception:
                        pass

            # Choose a strategy pattern (port of many PHP branches)
            # The PHP builds a fp string from heuristics; we'll implement the primary heuristics:
            if data['OPPONENT'] is not None:
                # choose an fp base list, emulate random picks
                if data['CHIN'] < 15:
                    choices = ['417clinchR", "5H105alloutR", "5H105insideR", "5H114alloutR", "5H114insideR", "5H87alloutR']
                else:
                    choices = ['417clinchR", "5H105alloutR", "5H105insideR", "5H114alloutR", "5H114insideR", "5H87alloutR", "6H122alloutR']
                fp_base = random.choice(choices)
                # randomly choose repetition factor influenced by heights
                hfactors = [1,1, (1 if data['HEIGHT'] > 14 else 3), (1 if data['HEIGHT'] > 14 else 3), (1 if data['HEIGHT'] - data['OPPONENT'][0] >= 0 else 3)]
                rep = random.choice(hfactors)
                fp = f"{fp_base}{rep}"
                # several PHP special-case branches:
                if random.randint(0,6) == 0 and (data['HEIGHT'] - data['OPPONENT'][0]) >= -3:
                    # uses a strange inline ternary combining strings; we'll pick a realistic fallback
                    fp = random.choice(['5H87clinchR", "5H105ringR'])
                if data['WEIGHT'][1] < 200:
                    if random.randint(0,6) < 5 and ((data['HEIGHT'] - data['OPPONENT'][0] <= -10) or (data.get("RECORD") and int(data['RECORD'][0][1]) > 9 and (int(data['RECORD'][0][4]) / int(data['RECORD'][0][1]) < 0.1 if int(data['RECORD'][0][1]) != 0 else False))):
                        fp = "6H122alloutR" + str(random.randint(1,3))
                    elif (data['HEIGHT'] - data['OPPONENT'][0] >= 0) and random.randint(0,4) == 0:
                        fp = "5H114insideR1"
                    elif (data['HEIGHT'] - data['OPPONENT'][0] >= 0):
                        fp = "5H87ringR1"
                    elif (data['HEIGHT'] - data['OPPONENT'][0] >= -3) and random.randint(0,1) == 1:
                        fp = "5H105insideR1"
                    elif (data['HEIGHT'] - data['OPPONENT'][0] >= -3):
                        fp = random.choice(['5H87", "5H105']) + "clinchR1"
                if random.randint(0,9) == 0:
                    fp = "6H113alloutR1"
                if data['CHIN'] > 23:
                    fp = random.choice(["5H105alloutR", "5H114alloutR", "5H87alloutR", "6H122alloutR" if data['OPPONENT'][0] > data['HEIGHT'] else "5H105alloutR"]) + str(random.randint(1,2))
                # final write to select orders
                write_msg("eko_select_orders", f"your_team={data['NAME']}&+strategy_choice={fp}")

        # DEBUG prints of data similar to PHP print_r
        print("--- Fighter Info ---")
        print(f"Team ID: {tid}")
        for k, v in data.items():
            print(f"{k}: {v}")
        print("--------------------")

        # Training logic (port of PHP block where $tr decisions are made)
        tr = [0, 0, (1 if (data['CHIN'] < 11 or data['CONDITIONING'] > 11 or data['STATUS'] - data['RATING'] > 1) else 0)]
        # run two passes
        baseaps = data['STRENGTH'] + data['SPEED'] + data['AGILITY']
        for i in range(2):
            if data['CHIN'] < 9 or (data['CHIN'] < 10 and data['STATUS'] > 20) or (data['KP'] and (data['CHIN'] - 10.0) < round((types[data['TYPE']]['CHIN'] - 10.0) * data['STATUS'] / 28.0)):
                tr[i] = 4
                data['CHIN'] += 1
            elif data['CONDITIONING'] < 5:
                tr[i] = 5
                data['CONDITIONING'] += 1
            elif data['KP'] and data['KP'] < round((data['STRENGTH'] - 1) / 3.0):
                tr[i] = 1
                data['KP'] += 1
            elif data['WEIGHT'][0] > 299 or (data['WEIGHT'][1] > 102 and data['AGILITY'] < round(baseaps * types[data['TYPE']]['AGILITY']) and baseaps * types[data['TYPE']]['AGILITY'] - data['AGILITY'] > baseaps * types[data['TYPE']]['SPEED'] - data['SPEED']):
                tr[i] = 3
                data['AGILITY'] += 1
                baseaps += 1
            elif data['STRENGTH'] < round(baseaps * types[data['TYPE']]['STRENGTH']) or data['SPEED'] > 29 or data['WEIGHT'][0] < MAX_WEIGHTS.get(data['DIVISIONS'][0], 0) if data.get("DIVISIONS") else False:
                data['STRENGTH'] += 1
                baseaps += 1
                if data['KP']:
                    tr[i] = 1
            else:
                tr[i] = 2
                data['SPEED'] += 1
                baseaps += 1

        # The PHP had a special floating kp AI condition; implement equivalent
        if (opptacs.get("KP",0) + opptacs.get("FLASHES",[0])[0]) > (len(bouts) if bouts else 1) / 2.0 and tr[0] != 4 and (data['CHIN'] < 11 or (data['STATUS'] == 18 and (data.get("DIVISIONS") and data['DIVISIONS'][1] != "Contenders")) or data['STATUS'] == 28 or data['RATING'] < data['STATUS']):
            tr = [4, tr[1], 0]

        # If training selection differs, send eko_training
        training_changed = False
        # PHP checked: if $data['TRAINING'] == null || $data['TRAINING'][0] != $tr[0] || (is_numeric($data['TRAINING'][1]) && $data['TRAINING'][1] != $tr[1]) || ($data['TRAINING'][2] !== false) != $tr[2]
        if data['TRAINING'] is None:
            training_changed = True
        else:
            try:
                if data['TRAINING'][0] != tr[0] or (isinstance(data['TRAINING'][1], int) and data['TRAINING'][1] != tr[1]) or (bool(data['TRAINING'][2]) != bool(tr[2])):
                    training_changed = True
            except Exception:
                training_changed = True

        if training_changed:
            tr0 = TRAIN_STR[tr[0]] if 0 <= tr[0] < len(TRAIN_STR) else TRAIN_STR[0]
            tr1 = TRAIN_STR[tr[1]] if 0 <= tr[1] < len(TRAIN_STR) else TRAIN_STR[0]
            intensive = "&intensive=1" if tr[2] else ""
            write_msg("eko_training", f"your_team={data['NAME']}&train={tr0}&train2={tr1}{intensive}")

    # After all fighters processed, creation of missing fighters (typesbyheight logic)
    # PHP had: foreach($typesbyheight as $key1 => $value1) foreach($value1 as $height => $value2) if ($value2 < fighter_types()[$key1]['COUNT']) { ... create fighter ... }
    for tindex, height_map in enumerate(typesbyheight):
        required = types[tindex]['COUNT']
        # iterate heights in a reasonable range (0..30) if height_map lacks keys; PHP used actual recorded heights only.
        heights_to_check = sorted(set(list(height_map.keys()) + list(range(1, 30))))
        for height in heights_to_check:
            count = height_map.get(height, 0)
            if count < required:
                # create fighters until satisfied
                while count < required:
                    chin = random.randint(12, 14)
                    condition = 6
                    strength = round((69 - height - chin - condition) * (1.0 - types[tindex]['SPEED'] - types[tindex]['AGILITY']))
                    strength -= math.floor(strength / 9.0)
                    ko_punch = math.floor(strength / 3.0)
                    agility = round(max(1, (69 - height - chin - condition - ko_punch) * types[tindex]['AGILITY']))
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

    week = int(time.strftime("%W")) * 10000

    try: with open('data.json') as f: ftr = json.load(f)
    except: ftr = {}

    # print(write_msg("eko_select_orders", f"your_team=Byl`phillip&strategy_choice=5H114insideR1")) # 6H122alloutR1 5H87ringR1 5H105insideR1

    try:
        for word in write_msg("eko_retired_fighters").split("Activate</A>"):
                if "regional_champion" not in word and "challenger.gif" not in word and "champion.gif" not in word:
                    for team_id in re.findall(r"team_id=([0-9]+)", word):
                        write_msg("eko_activate", f"team_id={team_id}")
                        break

        team_ids = sorted(set(re.findall(r"team_id=([0-9]+)", write_msg("eko_all_fighters_brief"))), key=int)
        print(team_ids)

        for team_id in team_ids:
            text, ftr[team_id], rng = write_msg("eko_control_fighter", f"team_id={team_id}"), {}, random.Random(week + int(team_id))


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
            ftr[team_id]['IPS'] = int(re.search(r'>[Ii]njury [Pp]oints<[^0-9]+>(\d+)', text).group(1)) + int(re.search(r'[\w]>[Aa][Pp] [Ll]oss[^0-9]+>(-?\d+)', text).group(1)) * 500
            ftr[team_id]['RECORD'] = [int("0%s" % i) for i in re.search(r'\(([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+)\/([0-9]+)\)', text).groups()]
            ftr[team_id]['DIVISIONS'] = [i.lower() for i in re.search(r'eko_standings[\w&=+]+division=([\w-]+)[\w&=+]+region=([^&]+)', text).groups()]
            ftr[team_id]['WEIGHT'] = compute_weight(ftr[team_id]['HEIGHT'], ftr[team_id]['STRENGTH'], ftr[team_id]['AGILITY'], ftr[team_id]['CONDITIONING'], ftr[team_id]['BUILD'])


            ftr[team_id]['OPPONENT'] = re.search(r' ([0-9]) feet *([0-9]{0,2})[^>]*team_id=([0-9]+)&describe=[0-9]\">(.*)<[I\/][AM][G>]', text)
            if ftr[team_id]['OPPONENT']:
                ftr[team_id]['OPPONENT'] = [ (int("0%s" % ftr[team_id]['OPPONENT'].group(1)) - 5) * 12 + int("0%s" % ftr[team_id]['OPPONENT'].group(2)), int("0%s" % ftr[team_id]['OPPONENT'].group(3)), ftr[team_id]['OPPONENT'].group(4)
                    ] + [int("0%s" % i) for i in re.search(r'([0-9]+)-([0-9]+)-[0-9]+ [0-9]+\/[0-9]+\)  from the', text).groups() ]


            ftr[team_id]['TRAINING'] = [stats_str.index(i.strip()) if i.strip() in stats_str else None for i in re.search(r' training <[Bb]>([a-z\s]+)[^<]*<[^<]*[\<Bb\>]*([a-z\s]+)', text).groups()] + [" (intensive) <" in text]
            ftr[team_id]['FIGHTPLAN'] = m.group(1) if (m := re.search(r'> your <[Bb]>(.+)<\/[Bb]> plan.', text)) else None

            ftr[team_id]['GRADE'] = 1.0 / ftr[team_id]['CUT'] * (42.0 * (1.0 - min(ftr[team_id]['IPS'] / (ftr[team_id]['STATUS'] + 1.0) / 38.0, 1.0)) + (10.0 + min(ftr[team_id]['RECORD'][0] + ftr[team_id]['RECORD'][1], 10.0)) * ftr[team_id]['RECORD'][0] / (ftr[team_id]['RECORD'][0] + ftr[team_id]['RECORD'][1] + 0.001) +
                13.0 * ftr[team_id]['RATING'] / 28.0 + 12.0 * min(ftr[team_id]['RECORD'][0], 20.0) / 20.0 + 3.0 * ftr[team_id]['STRENGTH'] / (ftr[team_id]['STRENGTH'] + ftr[team_id]['SPEED'] + ftr[team_id]['AGILITY']) + 2.0 / (ftr[team_id]['KP'] + 1.0))

            baseaps = ftr[team_id]['STRENGTH'] + ftr[team_id]['SPEED'] + ftr[team_id]['AGILITY']
            ftr[team_id]['TYPE'] = min(range(len(fighter_builds)), key=lambda i: (abs(baseaps * fighter_builds[i]['STRENGTH'] - ftr[team_id]['STRENGTH']) + abs(baseaps * fighter_builds[i]['SPEED'] - ftr[team_id]['SPEED']) + abs(baseaps * fighter_builds[i]['AGILITY'] - ftr[team_id]['AGILITY'])))

            print(ftr[team_id])

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

            ftr[team_id]['DIVISIONS'].insert(3, divis_str[len([ True for i in max_weights if i < ftr[team_id]['WEIGHT'][1]]) ].lower()) # find correct weight div
            if ftr[team_id]['DIVISIONS'][0] != ftr[team_id]['DIVISIONS'][2]: # in wrong div, make change
                write_msg("eko_change_division", f"your_team={ftr[team_id]['NAME']}&+division={ftr[team_id]['DIVISIONS'][2]}weight")

            if ftr[team_id]['OPPONENT']:

                if ftr[team_id]['OPPONENT'][3] + ftr[team_id]['OPPONENT'][4] > 0 and len(ftr[team_id]['OPPONENT']) < 6:

                    ftr_bouts = {}

                    for sess in re.findall(r"query_scout.*team_id=([0-9]+)&session=([0-9]+)", write_msg("eko_career_nodesc", f"team_id={ftr[team_id]['OPPONENT'][1]}"))[:4]:
                        fght_text = write_msg("query_scout", f"team_id={sess[0]}&session={sess[1]}")
                        ftr_intro, ftr_order = re.findall(r"<[Pp]>In this corner, standing ([4-7]+) feet *[and ]*([0-9]{0,2}).*in at \d+ pound.* win.* loss.* is(?: <font color=green><B>| )(.+)!!", fght_text), 2
                        if len(ftr_intro) > 1:
                            if ftr[team_id]['OPPONENT'][2] == ftr_intro[0][2]: ftr_order = 1
                            elif ftr[team_id]['OPPONENT'][2] == ftr_intro[1][2]: ftr_order = 2
                            elif (int("0%s" % ftr_intro[0][0]) - 5) * 12 + int("0%s" % ftr_intro[0][1]): ftr_order = 1

                        for rnd in re.findall(r"<[Bb][Rr]><[Hh][Rr]> *ROUND *([0-9]+).*[\n](.+)[\n](.+)", fght_text) + []:
                            ftr_style = next((i for i, k in enumerate([ "(inside)", "(clinching)", "(feinting)", "(counter-punching)", "(using the ring)", "(ropes)", "(outside)", "(all out)", "." ]) if k in rnd[ftr_order]), None)
                            ftr_target = next((i for i, k in enumerate([ "to the body.<", "for the cut.<", "s head hunting.<", "." ]) if k in rnd[ftr_order]), None)
                            ftr_bouts.setdefault(int(rnd[0]), []).append((ftr_style, ftr_target))


                    ftr[team_id]['OPPONENT'].append(ftr_bouts)
                    print(ftr[team_id]['OPPONENT'])


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
                if rng.randint(0,9) == 0:
                    fp = '6H113alloutR1'
                if ftr[team_id]['CHIN'] > 23:
                    fp = rng.choice(['5H105alloutR', '5H114alloutR', '5H87alloutR', '6H122alloutR' if ftr[team_id]['OPPONENT'][0] > ftr[team_id]['HEIGHT'] else '5H105alloutR']) + str(rng.randint(1,2))

                if ftr[team_id]['FIGHTPLAN'] != fp:
                    write_msg("eko_select_orders", f"your_team={ftr[team_id]['NAME']}&strategy_choice={fp}")

            if (ftr[team_id]['STATUS'] > 0 and ftr[team_id]['IPS'] / (ftr[team_id]['STATUS'] + 0.01) > 38.0) or (ftr[team_id]['RECORD'][0] == 0 and ftr[team_id]['RECORD'][1] > 1):
                if ftr[team_id]['DIVISIONS'][1] == "contenders" or ftr[team_id]['STATUS'] > 18:
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

    # git add . && git commit -m "update" && git push