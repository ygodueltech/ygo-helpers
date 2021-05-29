"""
https://github.com/vonas/omega-api-decks/blob/master/src/Format/decoders/OmegaFormatDecoder.php
"""
import base64
import os
import re
import sqlite3
import struct
import zlib

import click

DIR = os.path.dirname(os.path.abspath(__file__))

dbfile = os.getenv("YGO_CARDS_CDB") or f"{DIR}/cards.cdb"

YDKE_PREFIX = "ydke://"
YDKE_SEPARATOR = "!"
YDKE_SUFFIX = "!"

RE_YDKE = f"{YDKE_PREFIX}(?P<deck>.*){YDKE_SUFFIX}"


def _decode_ydke(ydke):

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
    """decode omega and print out cards in it"""
    raw = gzinflate(omega_code.strip())

    # main_and_extra_count = raw[0]
    # side_count = raw[1]
    tail = raw[2:]

    cards = [x[0] for x in struct.iter_unpack("i", tail)]
    mapping = {x["id"]: dict(x) for x in from_ids(set(cards))}

    deck = [mapping[card] for card in cards]
    for card in deck:
        print(card)
    return deck


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
        if not re.match("^[#!]", line)
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


if __name__ == "__main__":
    cli()
