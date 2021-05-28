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


def get_db():
    con = sqlite3.connect(dbfile)
    con.row_factory = sqlite3.Row
    return con


def gzinflate(compressed):
    """
    php gzinflate in python
    raise ValueError if bad input
    https://github.com/Fitblip/Snippits/blob/master/python/eval.gzinflate.base64.py
    """
    left = compressed.count("(")
    right = compressed.count(")")

    if left != right:
        raise ValueError("Truncated input? should have same '( 'and ')' count")

    if left > 0:
        return zlib.decompressobj().decompress(
            b"x\x9c" + base64.b64decode(compressed.split("(")[-1].split("'")[1])
        )
    if left == 0:
        return zlib.decompressobj().decompress(b"x\x9c" + base64.b64decode(compressed))
    raise ValueError("no idea what to do")


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
