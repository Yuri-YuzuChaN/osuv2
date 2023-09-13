import json
from pathlib import Path

from hoshino.service import Service, priv

# 路径
Root = Path(__file__).parent
static = Root / 'static'
OAuthJson = static / 'OAuth.json'
OsuDataBase = static / 'osu.db'
MeiryoR = static / 'fonts' / 'Meiryo Regular.ttf'
MeiryoS = static / 'fonts' / 'Meiryo SemiBold.ttf'
TrFont = static / 'fonts' / 'Torus Regular.otf'
TsFont = static / 'fonts' / 'Torus SemiBold.otf'
Venera = static / 'fonts' / 'Venera.otf'
RankDir = static / 'ranking'
MapDir = static / 'map'
WorkDir = static / 'work'
FlagsDir = static / 'flags'
ModsDir = static / 'mods'
bgImg = [ static / f'pfm_{mode}.png' for mode in ['std', 'taiko', 'ctb', 'mania'] ]
pfmbg = static / 'Best Performance.png'


# OAuth
OAuth = json.load(open(OAuthJson, 'r', encoding='utf-8'))
client_id = OAuth['client_id']
client_secret = OAuth['client_secret']


# 常用变量
GameModeNum = {0 : 'Std', 1 : 'Taiko', 2 : 'Ctb', 3 : 'Mania'}
GameMode = {0 : 'osu', 1 : 'taiko', 2 : 'fruits', 3 : 'mania'}
GameModeName = {'osu' : 'Std', 'taiko' : 'Taiko', 'fruits' : 'Ctb', 'mania' : 'Mania'}
FGameMode = {value: key for key, value in GameMode.items()}
Mod = {
    '0'         :       'NO',
    '1'         :       'NF',
    '2'         :       'EZ',
    '4'         :       'TD',
    '8'         :       'HD',
    '16'        :       'HR',
    '32'        :       'SD',
    '64'        :       'DT',
    '128'       :       'RX',
    '256'       :       'HT',
    '576'       :       'NC',
    '1024'      :       'FL',
    '2048'      :       'AT',
    '4096'      :       'SO',
    '8192'      :       'RX2',
    '16384'     :       'PF',
    '32768'     :       '4K',
    '65536'     :       '5K',
    '131072'    :       '6K',
    '262144'    :       '7K',
    '524288'    :       '8K',
    '1048576'   :       'FI',
    '2097152'   :       'RD',
    '4194304'   :       'CI',
    '8388608'   :       'TG',
    '16777216'  :       '9K',
    '33554432'  :       'KC',
    '67108864'  :       '1K',
    '134217728' :       '3K',
    '268435456' :       '2K',
    '536870912' :       'V2',
    '1073741824':       'MR',
}
NewMod = {value: key for key, value in Mod.items()}
CropSize = {
    'BG': [1500, 360],
    'Header': [1000, 400],
    'MapBG': [1200, 600],
    'BMapBG': [1200, 300]
}

sv = Service('osuv2', manage_priv=priv.ADMIN, enable_on_default=True)