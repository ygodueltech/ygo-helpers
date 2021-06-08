# WARNGING
i'm working on parsing some data and currently have dumped ~50MB of json into the `data` folder so the repo got fat

# env vars

`YGO_CARDS_CDB` location of `cards.cdb`

# example run

## peek-into-ydk
`python translate.py peek-into-ydk AI_BlueEyes.ydk`

```
89631139 - Blue-Eyes White Dragon
89631139 - Blue-Eyes White Dragon
89631139 - Blue-Eyes White Dragon
38517737 - Blue-Eyes Alternative White Dragon
[...]
```

## decode-omega

```
$python translate.py decode-omega '0+a6LjWfEYbv\/L\/MAMIXps0AY4kjoiww\/PbQdlYYFuz7zgDDKmaXWGB4zsmPjCC8uMSeGYRfys5kheHgpcuZQXj3GXs4XnDhIQscP7oGx\/ll7xlguPCSLrM1cx1L\/+bXjBYbk1k0uaWYg753MQcD8Ub3TWD8MGIuGIPsBNkBAA=='

{'id': 27204311, 'name': 'Nibiru, the Primal Being', 'type': 'MAIN'}
{'id': 27204311, 'name': 'Nibiru, the Primal Being', 'type': 'MAIN'}
{'id': 27204311, 'name': 'Nibiru, the Primal Being', 'type': 'MAIN'}
[...]
```

# misc

can just alias like this I'll set up pipx later

`alias ydkr="$PATH_TO/ygo-helpers/.venv/bin/python $PATH_TO/ygo-helpers/translate.py "`
