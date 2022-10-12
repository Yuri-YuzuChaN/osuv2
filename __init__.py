from hoshino import Service, priv
import os

PATH = os.path.dirname(__file__)
FILEPATH = os.path.join(PATH, 'osufile')
GAMEMODE = {0 : 'osu', 1 : 'taiko', 2 : 'fruits', 3 : 'mania'}
GAMEMODENAME = {'osu' : 'Std', 'taiko' : 'Taiko', 'fruits' : 'Ctb', 'mania' : 'Mania'}
FGAMEMODE = {value: key for key, value in GAMEMODE.items()}

sv = Service('osuv2', manage_priv=priv.ADMIN, enable_on_default=True)