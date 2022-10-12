from typing import List, Optional

MODS = {
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
    '4194304'   :       'Cinema',
    '8388608'   :       'TG',
    '16777216'  :       '9K',
    '33554432'  :       'KC',
    '67108864'  :       '1K',
    '134217728' :       '3K',
    '268435456' :       '2K',
    '536870912' :       'V2',
    '1073741824':       'MR',
}

NEWMODS = {value: key for key, value in MODS.items()}

class Mods:

    tempMods: Optional[int]

    def __init__(self, info: dict, mods: List[str]) -> None:
        self.Info = info
        self.Mods = mods
        self.Sum = 0
        for _ in self.Mods:
            ModsSum = int(NEWMODS[str(_.upper())])
            self.Sum += ModsSum

    def GetModsList(self) -> List[int]:
        return self.SetModsList()

    def CalcModsSum(self, mods: List[str]) -> int:
        """计算 `mods` 求合"""
        sum = 0
        for i in mods:
            ModsSum = int(NEWMODS[str(i.upper())])
            sum += ModsSum
        return sum

    def SetModsList(self) -> List[int]:
        vsum: List[int] = []
        for index, v in enumerate(self.Info):
            if v['mods']:
                sum = self.CalcModsSum(v['mods'])
                if sum == self.Sum:
                    vsum.append(index)
        return vsum
