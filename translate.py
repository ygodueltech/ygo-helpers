"""
Some code for peeking inside yu-gi-oh deck formats
"""
import base64
import json
import os
import re
import sqlite3
import struct
import zlib
from collections import defaultdict

import click

DIR = os.path.dirname(os.path.abspath(__file__))

dbfile = os.getenv("YGO_CARDS_CDB") or f"{DIR}/cards.cdb"

YDKE_PREFIX = "ydke://"
YDKE_SEPARATOR = "!"
YDKE_SUFFIX = "!"

RE_YDKE = f"{YDKE_PREFIX}(?P<deck>.*){YDKE_SUFFIX}"

SIDE = "SIDE"
EXTRA = "EXTRA"
MAIN = "MAIN"

STANDARD_DECKTYPES = (MAIN, EXTRA, SIDE)


def to_ydk(deck):
    """
    [{'id':0, 'name':'foo', 'type':'MAIN}] -> ydk
    includes comments at top with the mapping of "$cardid = $name"

    """

    uniq_id_names = sorted(
        {(x["id"], x["name"]) for x in deck if x["type"] in STANDARD_DECKTYPES}
    )
    comments = "\n".join([f"# {cid} = {name};" for cid, name in uniq_id_names])

    ydk_decklist = [comments]
    current_decktype = None
    for card in deck:

        card_type = card["type"]
        if card_type not in STANDARD_DECKTYPES:
            continue  # ignore nonstandard types like THUMBNAIL

        if card_type != current_decktype:
            ydk_decklist.append(f"!{card_type.lower()}")
            current_decktype = card_type

        ydk_decklist.append(str(card["id"]))
    print("\n".join(ydk_decklist))
    return ydk_decklist


def get_db():
    con = sqlite3.connect(dbfile)
    con.row_factory = sqlite3.Row
    return con


def gzinflate(compressed):
    return zlib.decompress(base64.b64decode(compressed), -8)


def from_ids(cids):
    con = get_db()
    cur = con.cursor()
    cids = ",".join(map(str, cids))
    cur.execute(
        f"""select datas.id, name
            ,CASE
                WHEN type & 0x40 THEN 'EXTRA' -- Fusion
                WHEN type & 0x2000 THEN 'EXTRA' -- Synchro
                WHEN type & 0x800000 THEN 'EXTRA' -- XYZ
                WHEN type & 0x4000000 THEN 'EXTRA' -- Link
                ELSE 'MAIN'
            END AS type
            from texts
            join datas
            on datas.id = texts.id
            where datas.id in ({cids})"""
    )
    res = list(cur.fetchall())
    return res


def _decode_omega(omega_code):
    """decode omega and print out cards in it
    based on https://github.com/vonas/omega-api-decks/blob/master/src/Format/decoders/OmegaFormatDecoder.php
    """
    raw = gzinflate(omega_code.strip())

    main_and_extra_count = raw[0]
    # side_count = raw[1]
    tail = raw[2:]

    cards = [x[0] for x in struct.iter_unpack("i", tail)]
    mapping = {x["id"]: dict(x) for x in from_ids(set(cards))}

    deck = [dict(mapping[card]) for card in cards]
    for card in deck[main_and_extra_count:]:
        card["type"] = "SIDE"

    deck[-1]["type"] = "THUMBNAIL"

    for card in deck:
        print(card)
    return deck


def normalize_name(name):
    normalized = re.sub("[^a-zA-Z0-9]", "", name)
    if not normalized:
        raise ValueError(f"{name} normalized into empty string!")

    if not normalized[0].isalpha():  # prepend "A" to make valid id...
        normalized = f"A{normalized}"
    return normalized


def to_windbot_deck_constants(deck):
    uniq_id_names = sorted(
        set([(normalize_name(x["name"]), x["id"]) for x in deck if x["type"] != "SIDE"])
    )
    formatted = [f"public const int {name} = {cid};" for name, cid in uniq_id_names]
    print("\n".join(formatted))
    return formatted


def _decode_ydke(ydke):
    """
    ydke string to decklist
    based on https://github.com/vonas/omega-api-decks/blob/master/src/Format/decoders/YdkeFormatDecoder.php
    """

    match = re.match(RE_YDKE, ydke)
    if not match:
        raise ValueError(f"must match {RE_YDKE}, got {ydke}")

    raw = match.groupdict()["deck"]

    result = []
    for i, subdeck in enumerate(raw.split(YDKE_SEPARATOR)):

        decoded = base64.b64decode(subdeck)
        card_ids = [x[0] for x in struct.iter_unpack("i", decoded)]

        mapping = {x["id"]: dict(x) for x in from_ids(set(card_ids))}
        subcards = [mapping[x] for x in card_ids]

        deck_type = {0: "MAIN", 1: "EXTRA", 2: "SIDE"}.get(i)
        for card in subcards:
            card["type"] = deck_type
        result.append(subcards)
    result = sum(result, [])

    for card in result:
        print(card)

    return result


def get_name_to_id():
    cur = get_db().cursor()
    cur.execute(
        f"""select datas.id, name
            ,CASE
                WHEN type & 0x40 THEN 'EXTRA' -- Fusion
                WHEN type & 0x2000 THEN 'EXTRA' -- Synchro
                WHEN type & 0x800000 THEN 'EXTRA' -- XYZ
                WHEN type & 0x4000000 THEN 'EXTRA' -- Link
                ELSE 'MAIN'
            END AS type
            from texts
            join datas
            on datas.id = texts.id
    """
    )
    mapping = {name.lower(): (dbid, typ) for dbid, name, typ in cur.fetchall()}
    return mapping


def from_json():
    """
    this was for messing with local files of data scraped for decklists on yugipedia
    """
    infile = "./sd_decks2_2021_06_02.json"
    # infile = "./chars_2021_06_02.json"
    decks = json.load(open(infile))

    mapping = get_name_to_id()

    parsed_decks = []
    for deck in decks:

        parsed_deck = []

        deckname = deck["deckname"]
        if "(incomplete)" in deckname:
            continue

        cards = deck["cards"]
        parsed_cards = defaultdict(list)

        comment_cards = set()
        for card in cards:
            cardname = card["cardname"].lower().strip()
            if cardname not in mapping:
                print(deckname, "|", cardname)
                # __import__("ipdb").set_trace()
                raise Exception("wtf")
            num = card["num"]

            dbid, typ = mapping[cardname]

            card["id"] = dbid
            card["type"] = typ
            card["name"] = card["cardname"]

            parsed_cards[typ].extend([str(dbid) for _ in range(num)])
            comment_cards.add(f'# {dbid} = {card["cardname"]} ({num})')

        ydkname = re.sub("[^a-z0-9]", "_", deckname.lower())

        maindeck = "\n".join(parsed_cards[MAIN])
        extradeck = "\n".join(parsed_cards[EXTRA])
        comments = "\n".join(sorted(comment_cards))
        # comments = "\n".join(sorted(to_windbot_deck_constants(cards)))

        final_ydk = "\n".join(
            [f"## {deckname}", comments, f"#main", maindeck, "#extra", extradeck]
        )
        # print(final_ydk)
        # __import__("ipdb").set_trace()
        with open(f"dldecks/DLAI__{ydkname}.ydk", "w") as f:
            # with open(f"chardecks/DLAI__{ydkname}.ydk", "w") as f:
            f.write(final_ydk)


def _peek_into_ydk(infile):
    """print out cards in a ydk"""
    cur = get_db().cursor()
    cur.execute("select name,id from texts")
    # mapping = {name:dbid for name, dbid in cur.fetchall()}
    mapping = {dbid: name for name, dbid in cur.fetchall()}

    with open(infile) as f:
        lines = f.readlines()
        ydk_data = [line.strip() for line in lines if line.strip()]

    deck = [
        {"id": line, "name": mapping[int(line)]}
        for line in ydk_data
        if not re.match("^[#!'\ufeff]", line)
    ]
    for card in deck:
        print(f"{card['id']} - {card['name']}")
    return deck


@click.group()
def cli():
    pass


@cli.command()
@click.argument("infile")
def peek_into_ydk(infile):
    _peek_into_ydk(infile)


@cli.command()
@click.argument("omega_code")
def decode_omega(omega_code):
    _decode_omega(omega_code)


@cli.command()
def testit():
    from_json()


if __name__ == "__main__":
    cli()
