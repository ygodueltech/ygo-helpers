"""
TODO  types are not consistent in the parsed output

have folder of
https://yugipedia.com/api.php?action=query&redirects=true&prop=revisions&rvprop=content&format=json&formatversion=2&titles=Man-Eater_Bug
dumped like ./data/135598
this has code to parse that folder into a list of ./data/single_from_wikitext.json

but the typings here are fucked

list properties are not always lists, have to know schema to actually tell from wikitext...:
support: "one value"
support: ["one value", "two values"]

"""

import glob
import json
import os
import re

import tqdm

DIR = os.path.dirname(os.path.abspath(__file__))

CARD_CACHE_DIR = f"{DIR}/../resources-updater-master/CardCache"


def parse_setline(line):
    """
    data = {
        "card_code": card_code,
        "rarity": rarity,
        "setcode": setcode,
        "card_number": card_number,
    }
    or
    data = {"unparsed_todo": line}
    for video games and stuff

    some have NOSETCODE, NOCARDNUMBER, NORARITY
    """

    # video game sets!!!
    # '''[[Yu-Gi-Oh! Nightmare Troubadour: Visitor from Beyond|Visitor from Beyond]]'''
    if ";" not in line:
        data = {"unparsed_todo": line}
        return data

    # 'VJMP-JP201; V Jump August 2021 promotional card'
    if line.count(";") == 1:
        card_code, rarity = [x.strip() for x in line.split(";")]
    else:
        # TSHD-KR036; The Shining Darkness; Common
        card_code, _setname, rarity = [x.strip() for x in line.split(";")]

    # cover no setcode etc
    # | jp_sets               =
    # ; Vol.3; Ultra Rare
    setcode, card_number = (
        card_code.split("-") if card_code else ("NOSETCODE", "NOCARDNUMBER")
    )

    data = {
        "card_code": card_code,
        "rarity": rarity,
        "setcode": setcode,
        "card_number": card_number,
    }
    return data


def parse_card(raw):
    """
    parse wikitext revisions like
    https://yugipedia.com/api.php?action=query&redirects=true&prop=revisions&rvprop=content&format=json&formatversion=2&titles=Man-Eater_Bug
    into json

    """
    trimmed = re.sub(".*CardTable2", "", raw, flags=re.DOTALL).strip()
    # print(trimmed)
    lines = [x.strip() for x in trimmed.split("\n")]
    # trim: }}"}]}]}}
    lines = lines[:-1]

    parsed_card = {}

    last_prop = None
    last_kind = None
    for line in lines:

        if not line or line.startswith("=="):
            continue

        # print(line)

        # | en_sets               =
        # TSHD-EN036; The Shining Darkness; Common
        # ''' [[video game | set]]'''
        if last_kind == "setlist" and line[0] not in ("|", "*"):
            try:
                parsed_card[last_prop].append(parse_setline(line))
            except Exception as e:
                print(e, "|", last_prop, "|", line)
                parsed_card[last_prop].append({"unparsed_todo": line})

        # | supports              =
        # * Beast
        if last_kind == "list_prop" and line.startswith("*"):
            parsed_card[last_prop].append(line.strip("* "))

        elif line.endswith("="):
            try:
                last_prop = re.match(r"\| (?P<prop>[^ ]+) *=", line).groupdict()["prop"]
            except:
                print(line)
                __import__("ipdb").set_trace()

            if re.match("[a-z0-9]+_sets", last_prop):
                last_kind = "setlist"  # this kind needs to be parsed!!
            else:
                last_kind = "list_prop"

            # print(">>>>", last_prop, last_kind)
            parsed_card[last_prop] = []

        # | fr_name               = Souris des Clés
        elif line.startswith("|"):
            try:
                # needs only split first bc of vals like:
                # '| ko_name               = {{Ruby|SR|스피드로이드|lang=ko}} {{Ruby|56|파이브식스|lang=ko}}프레인'
                prop, val = [x.strip("| ") for x in line.split("=", 1)]
            except:
                print(line)
                __import__("ipdb").set_trace()

            if prop == "types":  # 'types': 'Beast / Tuner' -> ['Beast' , 'Tuner']
                parsed_card[prop] = [x.strip() for x in val.split("/")]
            else:
                parsed_card[prop] = val

            last_kind = "singlevalue"
            last_prop = None

    return parsed_card


def to_json_all():

    parsed_cards = []
    # the cards do not have extensions and there are other random files with extensions
    card_files = [
        x for x in glob.glob(f"{CARD_CACHE_DIR}/*") if "." not in os.path.basename(x)
    ]
    for card_file in tqdm.tqdm(card_files):
        with open(card_file, "r") as f:
            raw = f.read()
        parsed_card = parse_card(raw)
        parsed_cards.append(parsed_card)
    return parsed_cards


# res = to_json_all()
# json.dump(res, open("./omega_wikitext.json", "w"))
