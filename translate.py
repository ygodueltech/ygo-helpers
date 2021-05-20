import click
import re
import sqlite3

import os
DIR = os.path.dirname(os.path.abspath(__file__))

def translate(infile, dbfile=f"{DIR}/cards.cdb"):
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    cur.execute("select name,id from texts")
    # mapping = {name:dbid for name, dbid in cur.fetchall()}
    mapping = {dbid:name for name, dbid in cur.fetchall()}

    with open(infile) as f:
        lines = f.readlines()
        ydk_data = [line.strip() for line in lines if line.strip()]

    for line in ydk_data:
        if re.match(f'^[#!]', line):
            print(line)
            continue
        print(f"{line} - {mapping[int(line)]}")

@click.group()
def cli():
    pass

@cli.command()
@click.argument('infile')
def maincli(infile):
    translate(infile)

if __name__ == "__main__":
    cli()
