"""
dump of some analysis of the differences in windbot forks

-----

iceygo         8
edo            9
omega         10


List<BotClientCard> monsters = Enemy.GetMonsters();
List<ClientCard> monsters = Enemy.GetMonsters();

grep -r --with-filename -A 1 AddDeckType Decks | grep  ');'  | perl -pe 's/\);//' | perl -pe 's/"//g' | perl -pe 's/cs-\s+/cs,/g' | perl -pe 's/Decks.//' > decklists.csv

iceygo {'FurHireExecutor.cs', 'ABCExecutor.cs', 'IgnisterExecutor.cs', 'MathmechExecutor.cs', 'AI_TestExecutor.cs', 'ManualTest.cs', 'AdamatiaExecutor.cs', 'DragmaExecutor.cs'}
edo {'FurHireExecutor.cs', 'IgnisterExecutor.cs', 'MathmechExecutor.cs', 'AI_TestExecutor.cs', 'ManualTest.cs', 'AdamatiaExecutor.cs', 'TemplateExecutor.cs'}
omega {'FamiliarPossessedExecutor.cs', 'DoEveryThingExecutor.cs', 'ABCExecutor.cs', 'LuckyExecutor.cs', 'MathMechExecutor.cs', 'DragmaExecutor.cs', 'WitchcraftExecutor.cs', 'TemplateExecutor.cs'}

ipdb> has_missing
                             bot                        iceygo                           edo                omega  is_missing
0   FamiliarPossessedExecutor.cs  FamiliarPossessedExecutor.cs  FamiliarPossessedExecutor.cs                  NaN        True
1        DoEveryThingExecutor.cs       DoEveryThingExecutor.cs       DoEveryThingExecutor.cs                  NaN        True
4          WitchcraftExecutor.cs         WitchcraftExecutor.cs         WitchcraftExecutor.cs                  NaN        True
25              LuckyExecutor.cs              LuckyExecutor.cs              LuckyExecutor.cs                  NaN        True
40           MathMechExecutor.cs           MathMechExecutor.cs           MathMechExecutor.cs                  NaN        True
44             DragmaExecutor.cs                           NaN             DragmaExecutor.cs                  NaN        True
45                ABCExecutor.cs                           NaN                ABCExecutor.cs                  NaN        True
46            FurHireExecutor.cs                           NaN                           NaN   FurHireExecutor.cs        True
47           MathmechExecutor.cs                           NaN                           NaN  MathmechExecutor.cs        True
48            AI_TestExecutor.cs                           NaN                           NaN   AI_TestExecutor.cs        True
49           AdamatiaExecutor.cs                           NaN                           NaN  AdamatiaExecutor.cs        True
50                 ManualTest.cs                           NaN                           NaN        ManualTest.cs        True
51           IgnisterExecutor.cs                           NaN                           NaN  IgnisterExecutor.cs        T:

"""
import glob
import os
from collections import defaultdict
from functools import reduce

import pandas as pd

from translate import _decode_omega, _peek_into_ydk, from_ids

DIR = os.path.dirname(os.path.abspath(__file__))

ROOT = f"{DIR}/.."
W_ICEYGO = f"{ROOT}/windbot"
W_EDO = f"{ROOT}/ignis_windbot"
W_OMEGA = f"{ROOT}/YGOAIScripts"

mine = {"ToonExecutor.cs", "BeaterExecutor.cs"}

repos = ["iceygo", "edo", "omega"]


def to_cids(cards):
    return {card["id"] for card in cards}


def windbot_ydk_df(repo):
    ydks = glob.glob(f"{repo}/Decks/*ydk")
    ydk_to_decklist = {
        os.path.basename(ydk).replace(".ydk", "").lower(): _peek_into_ydk(ydk)
        for ydk in ydks
    }
    ice_df = (
        pd.DataFrame([ydk_to_decklist])
        .T.reset_index()
        .rename(columns={0: "decklist", "index": "bot"})
    )
    ice_df["cids"] = ice_df["decklist"].apply(to_cids)
    return ice_df


def by_decks():
    """
    compare the decklists of different windbot forks
    """

    # make csv with grep and perl in file docstring
    omega_df = pd.read_csv(f"{DIR}/decklists.csv", names=["bot", "omega_code"])

    omega_df["bot"] = omega_df["bot"].apply(
        lambda x: f"AI_{x.replace('Executor.cs','')}".lower()
    )
    omega_df["decklist"] = omega_df.omega_code.apply(_decode_omega)
    omega_df["cids"] = omega_df["decklist"].apply(to_cids)

    # ydks = glob.glob(f"{W_ICEYGO}/Decks/*ydk")

    # omega_df = windbot_ydk_df(W_ICEYGO)
    ice_df = windbot_ydk_df(W_EDO)
    merged = ice_df.merge(omega_df, on=["bot"])

    merged["delta_cid"] = merged.apply(
        lambda x: x["cids_x"].symmetric_difference(x["cids_y"]), axis=1
    )
    merged["only_ice"] = merged.apply(lambda x: x["cids_x"] - (x["cids_y"]), axis=1)
    merged["only_omega"] = merged.apply(lambda x: x["cids_y"] - (x["cids_x"]), axis=1)
    __import__("ipdb").set_trace()


def by_filenames():
    """
    compare the filename differences in different windbot forks
    """
    repo_to_decks = {}
    for repo, folder in [
        ("iceygo", f"{W_ICEYGO}/Game/AI/Decks"),
        ("edo", f"{W_EDO}/Game/AI/Decks"),
        ("omega", f"{W_OMEGA}/Decks"),
    ]:
        fls = [os.path.basename(x).lower() for x in glob.glob(f"{folder}/*cs")]
        repo_to_decks[repo] = list(set(fls) - mine)

        print(repo, len(fls))

    dfs = [
        pd.DataFrame({"bot": vals, repo: vals}) for repo, vals in repo_to_decks.items()
    ]
    df = reduce(lambda df1, df2: df1.merge(df2, on=["bot"], how="outer"), dfs)
    df["is_missing"] = df.apply(lambda x: any(x.isna()), axis=1)

    has_missing = df.query("is_missing == True")
    print(has_missing)
    print(has_missing.apply(lambda x: x.isna()).sum())

    for repo in repos:
        print(repo, set(has_missing.query(f"{repo} != {repo}").bot))
    # iceygo {'IgnisterExecutor.cs', 'DragmaExecutor.cs', 'MathmechExecutor.cs', 'FurHireExecutor.cs', 'ManualTest.cs', 'AI_TestExecutor.cs', 'ABCExecutor.cs', 'AdamatiaExecutor.cs'}
    # edo {'IgnisterExecutor.cs', 'MathmechExecutor.cs', 'FurHireExecutor.cs', 'ManualTest.cs', 'AI_TestExecutor.cs', 'TemplateExecutor.cs', 'AdamatiaExecutor.cs'}
    # omega {'DragmaExecutor.cs', 'DoEveryThingExecutor.cs', 'MathMechExecutor.cs', 'FamiliarPossessedExecutor.cs', 'LuckyExecutor.cs', 'TemplateExecutor.cs', 'WitchcraftExecutor.cs', 'ABCExecutor.cs'}
    __import__("ipdb").set_trace()


# by_decks()
# by_filenames()
