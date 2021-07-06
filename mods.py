mods = {
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

def resolve(value):
    mod_list = [1073741824, 536870912, 268435456, 134217728, 67108864, 33554432, 16777216, 8388608, 4194304, 2097152, 1048576, 524288, 262144, 131072, 65536, 32768, 16384, 8192, 4096, 2048, 1024, 576, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0]
    result = []
    # 如果一开始就为0那么直接返回
    if value == 0:
        return []

    # 如果不是则进行运算
    while len(mod_list) != 0:
        if mod_list[0] < value:
            new_value = mod_list.pop(0)
            result.append(new_value)
            value = value - new_value
        elif mod_list[0] == value:
            new_value = mod_list.pop(0)
            result.append(new_value)
            break
        else:
            mod_list.pop(0)

        if value == 0:
            break

    return modsname(result)

def modsname(result):
    mods_name = []
    for i in result:
        mods_name.append(mods[f'{i}'])
    return mods_name

def modsnum(mod):
    newmod = {value: key for key, value in mods.items()}
    num = 0
    for i in mod:
        mn = int(newmod[str(i.upper())])
        num += mn
    return num

def setmodslist(json, mods):
    vnum =[]
    for index, v in enumerate(json):
        if v['mods']:
            num = modsnum(v['mods'])
            if num == mods:
                vnum.append(index)
    return vnum
