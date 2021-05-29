from maniera.calculator import Maniera
import pyttanko as osu

def calc_acc_pp(osufile, mods_num):
    acc_pp = []
    p = osu.parser()
    with open(osufile, 'r', encoding='utf-8') as f:
        bmap = p.map(f)

    stars = osu.diff_calc().calc(bmap, mods_num)
    for acc in range(95, 101):
        c300, c100, c50 = osu.acc_round(acc, len(bmap.hitobjects), 0)

        pp, _, _, _, _ = osu.ppv2(
            stars.aim, stars.speed, mods=mods_num,
            n300=c300, n100=c100, n50=c50, bmap=bmap
        )

        acc_pp.append(int(pp))
        
    return acc_pp
    
def calc_pp(osufile, mods_num, maxcb, c50, c100, c300, miss):
    p = osu.parser()
    with open(osufile, 'r', encoding='utf-8') as f:
        bmap = p.map(f)

    stars = osu.diff_calc().calc(bmap, mods_num)

    pp, aim, speed, acc, accuracy = osu.ppv2(
        stars.aim, stars.speed, mods=mods_num,
        combo=maxcb, n300=c300, n100=c100, n50=c50, nmiss=miss, bmap=bmap
    )

    play_pp = int(pp)
    aim_pp = int(aim)
    speed_pp = int(speed)
    acc_pp = int(acc)
    return play_pp, aim_pp, speed_pp, acc_pp
   
def calc_if(osufile, mods_num, c50, c100, mapcb):
    p = osu.parser()
    with open(osufile, 'r', encoding='utf-8') as f:
        bmap = p.map(f)

    stars = osu.diff_calc().calc(bmap, mods_num)

    pp = osu.ppv2(
        stars.aim, stars.speed, mods=mods_num,
        n100=c100, n50=c50, nmiss=0, max_combo=mapcb, bmap=bmap
    )

    return int(pp[0])

def calc_mania_pp(osufile, mods_num, score):
    calc = Maniera(osufile, mods_num, score)
    calc.calculate()
    return int(calc.pp)

def calc_acc(mode, c50, c100, c300, cmiss, ckatu, cgeki):
    if mode == 0:
        h1 = c50 * 50.0 + c100 * 100.0 + c300 * 300.0
        h2 = (c50 + c100 + c300 + cmiss) * 300.0
    elif mode == 1:
        h1 = (c100 + ckatu) * 0.5 + c300 + cgeki
        h2 = cmiss + c100 + ckatu + c300 + cgeki
    elif mode == 2:
        h1 = c50 + c100 + c300
        h2 = ckatu + cmiss + c50 + c100 + c300
    elif mode == 3:
        h1 = (c50 * 50.0 + c100 * 100.0 + ckatu * 200.0 + (c300 + cgeki) * 300.0)
        h2 = (c50 + c100 + ckatu + cgeki + c300 + cmiss) * 300.0

    return h1 / h2 * 100.0
