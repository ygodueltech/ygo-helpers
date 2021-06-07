"""
https://www.semantic-mediawiki.org/wiki/Help:Inline_queries#Parser_function_.23ask
https://yugipedia.com/wiki/Category:Properties_(SMW)

http 'https://yugipedia.com/wiki/Special:Ask/format%3Djson/limit%3D500/offset%3D6500/link%3Dall/headers%3Dshow/searchlabel%3DJSON/class%3D-20sortable-20wikitable-20smwtable-20card-2Dlist/sort%3D-23/order%3Dasc/-5B-5BCategory:Yu-2DGi-2DOh!-20Duel-20Links-20cards-5D-5D-20-5B-5BCard-20type::!Monster-20card-5D-5D/-3FJapanese-20name/-3FCard-20type%3D-5B-5BCard-20type-5D-5D/-3FProperty%3D-5B-5BProperty-5D-5D/mainlabel%3D/prettyprint%3Dtrue/unescape%3Dtrue' > example_res.json


"""
import json
import pprint
import time

import requests

# py2 compat
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

RELEASE_TCG = "[[Medium::TCG]]"

YUGIPEDIA_HOST = f"https://yugipedia.com"
YUGIPEDIA_PATH = "index.php?title=Special:Ask"

ASK_URI = f"{YUGIPEDIA_HOST}/{YUGIPEDIA_PATH}"

SINGLE_FIELD = [
    "Database ID",
    "Password",
    "English name",
    "Lore",
    "Card type",
    "Level",
    "Rank",
    "ATK",
    "DEF",
    "Link Arrows",
    "Link Rating",
    "Japanese name",
    "Translated name",
    "Modification date",
]


# 'Modification date': {'raw': '1/2021/1/6/16/56/30/0',
#                       'timestamp': '1609952190'},
GET_FULLTEXT = [
    "Card type",
    "Belongs to",
    "TCG status",
    "OCG status",
]

MAP_GET_FULLTEXT = [
    "Support",
    "Effect type",
    "Type",
    "Attribute",
    "Secondary type",
    "Primary type",
]
MULTIFIELD = [
    "MonsterSpellTrap",
    "Effect type",
    "Archseries",
    "Anti-support",
    "Actions",
    "Materials",
    "Summoning",
    "Banishing",
    "Counters",
    "Stats",
    "Property",
    "Misc",
]

DISPLAYS1 = [
    "Database ID",
    "Password",
    "English name",
    "Lore",
    "Card type",
    "Primary type",
    "Secondary type",
    "Attribute",
    "Level",
    "Rank",
    "MonsterSpellTrap",
    "Type",
    "Effect type",
    "Archseries",
    "ATK",
    "DEF",
]
DISPLAYS2 = [
    "Database ID",
    "Anti-support",
    "Actions",
    "Materials",
    "Summoning",
    "Banishing",
    "Support",
    "Counters",
    "Stats",
    "Rarity",
    "Property",
    "Japanese name",
    "Translated name",
    "Modification date",
    "Misc",
    "TCG status",
    "OCG status",
    "Belongs to",
    "Link Arrows",
    "Link Rating",
]

ALL_DISPLAYS = list(set(DISPLAYS1 + DISPLAYS2))

# https://yugipedia.com/wiki/Special:Ask/format%3Djson/limit%3D500/offset%3D6500/link%3Dall/headers%3Dshow/searchlabel%3DJSON/class%3D-20sortable-20wikitable-20smwtable-20card-2Dlist/sort%3D-23/order%3Dasc/-5B-5BCategory:Yu-2DGi-2DOh!-20Duel-20Links-20cards-5D-5D-20-5B-5BCard-20type::!Monster-20card-5D-5D/-3FJapanese-20name/-3FCard-20type%3D-5B-5BCard-20type-5D-5D/-3FProperty%3D-5B-5BProperty-5D-5D/mainlabel%3D/prettyprint%3Dtrue/unescape%3Dtrue

# "https://yugipedia.com/wiki/Special:Ask/format%3Djson/limit%3D500/link%3Dall/headers%3Dshow/searchlabel%3DJSON/class%3D-20sortable-20wikitable-20smwtable-20card-2Dlist/sort%3D-23/order%3Dasc/"

# uri_prefix = "https://yugipedia.com/wiki/Special:Ask/format=json/limit=10/offset=0/link=all/headers=show/searchlabel=JSON/class= sortable wikitable smwtable card-2Dlist/sort=-23/order=asc/mainlabel=/prettyprint=true/unescape=true"
uri_prefix = "https://yugipedia.com/wiki/Special:Ask/format=json/offset=0/link=all/headers=show/searchlabel=JSON/class= sortable wikitable smwtable card-2Dlist/sort=-23/order=asc/mainlabel=/prettyprint=true/unescape=true"

decoded_uri = "https://yugipedia.com/wiki/Special:Ask/format=json/limit=10/offset=0/link=all/headers=show/searchlabel=JSON/class= sortable wikitable smwtable card-2Dlist/sort=-23/order=asc/mainlabel=/prettyprint=true/unescape=true/[[Category:Yu-2DGi-2DOh! Duel Links cards]] [[Card type::!Monster card]]/?Japanese name/?Card type=[[Card type]]/?Property=[[Property]]"


BRACK_L = "-5B-5B"
BRACK_R = "-5D-5D"
SPACE = "-20"
Q_MARK = "-3F"

replaces = {
    "[[": BRACK_L,
    "]]": BRACK_R,
    "?": Q_MARK,
    ">": "-3E",
    "<": "-3C",
}

# , ' ':SPACE


def encode_sm_uri(uri):  # TODO is a shit. '|'.join(
    """

    re.sub maybe better
    pattern = re.compile(r'\b(' + '|'.join(d.keys()) + r')\b')
    result = pattern.sub(lambda x: d[x.group()], s)
    https://stackoverflow.com/questions/2400504/easiest-way-to-replace-a-string-using-a-dictionary-of-replacements
    """

    encoded = uri
    for pat, replace in replaces.items():
        encoded = encoded.replace(pat, replace)
    return encoded


def ask_yugipedia(search_query, raw_printouts, limit=10, do_sleep=2):

    add_q = lambda x: f"{Q_MARK}{x}"
    printouts = "/".join(map(add_q, raw_printouts))

    sort = ""  # "Database Id"
    order = ""  # "desc"
    limit = f"limit={limit}"

    query = f"{search_query}/{printouts}/{limit}"
    query = encode_sm_uri(query)

    uri = f"{uri_prefix}/{query}"
    if do_sleep:
        time.sleep(do_sleep)
    res = requests.get(uri)
    # __import__("ipdb").set_trace()
    print(res.url)
    data = res.json() if res.content else {}
    return data


def display(displays):

    # add_q = lambda x: f"?{x}"
    add_q = lambda x: f"{Q_MARK}{x}"
    # printouts = ''.join(map(add_q, DISPLAYS))
    search_query = "[[Medium::TCG]] [[MonsterSpellTrap::+]]"

    limit = 10
    sort = ""  # "Database Id"
    order = ""  # "desc"

    # query = f"{search_query}{printouts}{limit}{sort}{order}"
    # qparams = {"query":query, "format":"jsonfm"}
    qparams = {}

    # limit = "limit=10"
    printouts = "/".join(map(add_q, displays))
    query = f"{search_query}{printouts}/{limit}"
    query = encode_sm_uri(query)
    uri = f"{uri_prefix}/{query}"
    res = requests.get(uri)
    data = res.json()

    # uri = "https://yugipedia.com/wiki/Special:Ask/format%3Djson/limit%3D10/link%3Dall/headers%3Dshow/mainlabel%3D-2D/searchlabel%3DJSON/class%3D-20sortable-20wikitable-20smwtable-20card-2Dlist/sort%3D-23/order%3Dasc/offset%3D0/-5B-5BMedium::TCG-5D-5D-20-5B-5BMonsterSpellTrap::%2B-5D-5D/-3FDatabase-20ID/-3FPassword/-3FEnglish-20name/-3FCard-20type/-3FMonsterSpellTrap/prettyprint%3Dtrue/unescape%3Dtrue"
    # for x in totest:
    #     printouts = "/".join(map(add_q, DISPLAYS + [x]))
    #     # printouts = "/".join(map(add_q, [x]))
    #     # printouts = "/".join(map(add_q, totest))
    #     query = f"{search_query}{printouts}/{limit}"
    #     query = encode_sm_uri(query)
    #     uri = f"{uri_prefix}/{query}"
    #     res = requests.get(uri)
    #     try:

    #         data = res.json()
    #         print(uri)
    #         # print(res)
    #         print(res.url)
    #         print("workeddddddddddddddddddddddddd:", x)
    #         __import__("ipdb").set_trace()
    #     except Exception as e:
    #         print("fail:", x)
    #         # print(x)
    #     time.sleep(1)

    # print(res.content)
    # __import__("ipdb").set_trace()


# print(encode_sm_uri(decoded_uri))


def craw_all():
    """

    > is >= by default for semantic wiki!
    """

    min_kdb_id = 4_000  #  4007 is actual lowest but rounding! https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=4007
    min_kdb_id = 114_000  #  4007 is actual lowest but rounding! https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=4007
    base_query = "[[Medium::TCG]]"

    final_output = []
    has_res = True
    kdb_id = min_kdb_id
    step = 400
    while has_res:
        query = "%s [[Database ID::>%s]] [[Database ID::<%s]]" % (
            base_query,
            kdb_id,
            kdb_id + step,
        )
        print(query)

        __import__("ipdb").set_trace()
        for i, disp in enumerate((DISPLAYS1, DISPLAYS2)):
            data = ask_yugipedia(query, disp, limit=500)
            check(data, disp)
            data["query"] = query
            data["disp"] = disp
            data["disp_i"] = i
            final_output.append(data)

            has_res = bool(data)
    return final_output


def check(data, raw_printouts):
    data_printouts = list(data["results"].values())[0]["printouts"]
    if len(data_printouts) != len(raw_printouts):
        print(set(raw_printouts) - set(data_printouts))
        __import__("ipdb").set_trace()


def get_examples():

    base_query = "[[Medium::TCG]] [[Database ID::+]]"
    base_printouts = [
        "Password",
        "English name",
        "Card type",
    ]
    all_res = {}

    n = len(ALL_DISPLAYS)
    for i, x in enumerate(ALL_DISPLAYS):
        query = f"{base_query} [[{x}::+]]"
        print(i, n, query)
        try:
            data = ask_yugipedia(query, base_printouts + [x])
        except:
            print("ERROR", i, x)
            continue
        all_res[x] = data
    return all_res


def parse_examples():
    data = json.load(open("example_has_prop.json"))

    parsed_data = {}
    for property_name, example_data in data.items():

        rows = [
            (x["fullurl"], dict(x["printouts"]))
            for x in example_data["results"].values()
        ]

        # {'Password': ['78310590'],
        #  'English name': ['Abyss Actor - Mellow Madonna'],
        #  'Card type': [{'fulltext': 'Monster Card',
        #    'fullurl': 'https://yugipedia.com/wiki/Monster_Card',
        #    'namespace': 0,
        #    'exists': '1',
        #    'displaytitle': ''}],
        #  'Stats': ['This card gains ATK']}]

        try:
            for fullurl, row in rows:
                for k, v in dict(row).items():
                    if k in GET_FULLTEXT:
                        row[k] = row[k][0]["fulltext"]
                    elif k in MAP_GET_FULLTEXT:
                        row[k] = [subitem["fulltext"] for subitem in row[k]]
                    elif k not in MULTIFIELD:
                        row[k] = row[k][0]
                row["fullurl"] = fullurl
        except Exception as e:
            print(e)
            __import__("ipdb").set_trace()
        parsed_data[property_name] = [x[1] for x in rows]
    for k, v in parsed_data.items():
        print("\n\n")
        print(k)
        try:
            print(v[0][k])
        except:
            print(v[0])
            # __import__("ipdb").set_trace()
        pprint.pprint(v[:1])


# display(DISPLAYS1)
# get_examples(DISPLAYS1)
# display(totest)
# print(len(DISPLAYS), len(totest))


def write_examples():
    res = get_examples()
    with open("example_has_prop.json", "w") as f:
        json.dump(res, f)
        print(len(res))


# parse_examples()
# res = craw_all()
# with open("tcg_cards.json", "w") as f:
#     json.dump(res, f)
#     print(len(res))

data = ask_yugipedia(RELEASE_TCG, DISPLAYS1)
