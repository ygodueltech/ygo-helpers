import translate

def test_decode_omega():
    omega_code = "0+a6LjWfEYbv\/L\/MAMIXps0AY4kjoiww\/PbQdlYYFuz7zgDDKmaXWGB4zsmPjCC8uMSeGYRfys5kheHgpcuZQXj3GXs4XnDhIQscP7oGx\/ll7xlguPCSLrM1cx1L\/+bXjBYbk1k0uaWYg753MQcD8Ub3TWD8MGIuGIPsBNkBAA=="
    expected = [{'id': 27204311, 'name': 'Nibiru, the Primal Being', 'type': 'MAIN'}
    ,{'id': 27204311, 'name': 'Nibiru, the Primal Being', 'type': 'MAIN'}
    ,{'id': 27204311, 'name': 'Nibiru, the Primal Being', 'type': 'MAIN'}
    ,{'id': 13893596, 'name': 'Exodius the Ultimate Forbidden Lord', 'type': 'MAIN'}
    ,{'id': 13893596, 'name': 'Exodius the Ultimate Forbidden Lord', 'type': 'MAIN'}
    ,{'id': 10000080, 'name': 'The Winged Dragon of Ra - Sphere Mode', 'type': 'MAIN'}
    ,{'id': 10000080, 'name': 'The Winged Dragon of Ra - Sphere Mode', 'type': 'MAIN'}
    ,{'id': 68535320, 'name': 'Fire Hand', 'type': 'MAIN'}
    ,{'id': 68535320, 'name': 'Fire Hand', 'type': 'MAIN'}
    ,{'id': 68535320, 'name': 'Fire Hand', 'type': 'MAIN'}
    ,{'id': 95929069, 'name': 'Ice Hand', 'type': 'MAIN'}
    ,{'id': 95929069, 'name': 'Ice Hand', 'type': 'MAIN'}
    ,{'id': 95929069, 'name': 'Ice Hand', 'type': 'MAIN'}
    ,{'id': 16223761, 'name': 'Thunder Hand', 'type': 'MAIN'}
    ,{'id': 16223761, 'name': 'Thunder Hand', 'type': 'MAIN'}
    ,{'id': 16223761, 'name': 'Thunder Hand', 'type': 'MAIN'}
    ,{'id': 80885284, 'name': 'Ghostrick Jiangshi', 'type': 'MAIN'}
    ,{'id': 80885284, 'name': 'Ghostrick Jiangshi', 'type': 'MAIN'}
    ,{'id': 80885284, 'name': 'Ghostrick Jiangshi', 'type': 'MAIN'}
    ,{'id': 32623004, 'name': 'Nopenguin', 'type': 'MAIN'}
    ,{'id': 32623004, 'name': 'Nopenguin', 'type': 'MAIN'}
    ,{'id': 54490275, 'name': 'Ghostrick Yuki-onna', 'type': 'MAIN'}
    ,{'id': 54490275, 'name': 'Ghostrick Yuki-onna', 'type': 'MAIN'}
    ,{'id': 93920745, 'name': 'Penguin Soldier', 'type': 'MAIN'}
    ,{'id': 93920745, 'name': 'Penguin Soldier', 'type': 'MAIN'}
    ,{'id': 93920745, 'name': 'Penguin Soldier', 'type': 'MAIN'}
    ,{'id': 61318483, 'name': 'Ghostrick Jackfrost', 'type': 'MAIN'}
    ,{'id': 61318483, 'name': 'Ghostrick Jackfrost', 'type': 'MAIN'}
    ,{'id': 54512827, 'name': 'Ghostrick Lantern', 'type': 'MAIN'}
    ,{'id': 54512827, 'name': 'Ghostrick Lantern', 'type': 'MAIN'}
    ,{'id': 54512827, 'name': 'Ghostrick Lantern', 'type': 'MAIN'}
    ,{'id': 81907872, 'name': 'Ghostrick Specter', 'type': 'MAIN'}
    ,{'id': 81907872, 'name': 'Ghostrick Specter', 'type': 'MAIN'}
    ,{'id': 81907872, 'name': 'Ghostrick Specter', 'type': 'MAIN'}
    ,{'id': 81191584, 'name': 'Recurring Nightmare', 'type': 'MAIN'}
    ,{'id': 81191584, 'name': 'Recurring Nightmare', 'type': 'MAIN'}
    ,{'id': 81191584, 'name': 'Recurring Nightmare', 'type': 'MAIN'}
    ,{'id': 15693423, 'name': 'Evenly Matched', 'type': 'MAIN'}
    ,{'id': 15693423, 'name': 'Evenly Matched', 'type': 'MAIN'}
    ,{'id': 15693423, 'name': 'Evenly Matched', 'type': 'MAIN'}
    ,{'id': 53334641, 'name': 'Ghostrick Angel of Mischief', 'type': 'EXTRA'}
    ,{'id': 75367227, 'name': 'Ghostrick Alucard', 'type': 'EXTRA'}
    ,{'id': 32224143, 'name': 'Ghostrick Socuteboss', 'type': 'EXTRA'}
    ,{'id': 73642296, 'name': 'Ghost Belle & Haunted Mansion', 'type': 'MAIN'}
    ,{'id': 52038441, 'name': 'Ghost Mourner & Moonlit Chill', 'type': 'MAIN'}
    ,{'id': 59438930, 'name': 'Ghost Ogre & Snow Rabbit', 'type': 'MAIN'}
    ,{'id': 59438931, 'name': 'Ghost Ogre & Snow Rabbit', 'type': 'MAIN'}
    ,{'id': 62015409, 'name': 'Ghost Reaper & Winter Cherries', 'type': 'MAIN'}
    ,{'id': 62015409, 'name': 'Ghost Reaper & Winter Cherries', 'type': 'MAIN'}
    ,{'id': 60643553, 'name': 'Ghost Sister & Spooky Dogwood', 'type': 'MAIN'}
    ,{'id': 60643553, 'name': 'Ghost Sister & Spooky Dogwood', 'type': 'MAIN'}
    ,{'id': 54490275, 'name': 'Ghostrick Yuki-onna', 'type': 'MAIN'}
    ,{'id': 61318483, 'name': 'Ghostrick Jackfrost', 'type': 'MAIN'}
    ]
    assert translate.decode_omega(omega_code) == expected
