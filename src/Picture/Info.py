import traceback
from time import time
from typing import List

from nonebot import MessageSegment
from PIL import Image, ImageDraw
from pydantic import BaseModel

from ... import *
from ..Api import osuApi
from ..DataBase import get_user_daily_data
from ..Error import DrawImageError
from ..File import getImage
from ..Model import User
from .Image import *


class DrawInfo:
    
    def __init__(self, userInfo: User, day: int = 0) -> None:
        self.user = userInfo
        self.score = userInfo.statistics
        self.day = day

    def scoreCalc(self, value: List[Union[int, float, bool]]) -> Tuple[str, Union[int, float]]:
        num = value[0] - value[1]
        if num < 0:
            if value[2]:
                op, v = '↑', num * -1
            elif value[3]:
                op, v = '↓', num * -1
            else:
                op, v = '-', num * -1
        elif num > 0:
            if value[2]:
                op, v = '↓', num
            elif value[3]:
                op, v = '↑', num
            else:
                op, v = '+', num
        else:
            op, v = '', 0
        return (op, v)
    
    
    class Calc(BaseModel):
        
        op: str
        value: Union[int, float]
 
    
    def _calc(self, value: Union[int, float], localvalue: Union[int, float], set1: bool, set2: bool) -> Calc:
        newvalue = value - localvalue
        if newvalue < 0:
            v = newvalue * -1
            if set1:
                op = '↑'
            elif set2:
                op = '↓'
            else:
                op = '-'
        elif newvalue > 0:
            v = newvalue
            if set1:
                op = '↓'
            elif set2:
                op = '↑'
            else:
                op = '+'
        else:
            op, v = '', newvalue
        return self.Calc(op=op, value=v)
    
    
    async def draw(self):
        try:
            country = FlagsDir / f'{self.user.country_code}.png'
            info_BG = static / 'info.png'
            supporter_BG = WorkDir / 'suppoter.png'
            exp_l = WorkDir / 'left.png'
            exp_c = WorkDir / 'center.png'
            exp_r = WorkDir / 'right.png'

            info_img = Image.open(info_BG).convert('RGBA')
            user_header_img = cropBG('Header', await getImage(self.user.cover_url))
            user_icon_img = Image.open(await getImage(self.user.avatar_url)).convert('RGBA').resize((300, 300))
            country_img = Image.open(country).convert('RGBA').resize((80, 54))
            supporter_img = Image.open(supporter_BG).convert('RGBA').resize((54, 54))
            exp_left_img = Image.open(exp_l).convert('RGBA')
            exp_width = self.user.statistics.level.progress * 7 - 3
            exp_center_img = Image.open(exp_c).convert('RGBA').resize((exp_width, 10))
            exp_right_img = Image.open(exp_r).convert('RGBA')

            userData = get_user_daily_data(self.user.id, self.day, self.user.play_mode)
            if userData:
                crank, grank, _pp, accuracy, playcount, hit_count = userData.CountryRanked, userData.GlobalRanked, userData.Pp, userData.Accuracy, userData.PlayCount, userData.Hit
            else:
                crank, grank, _pp, accuracy, playcount, hit_count = self.score.country_rank, self.score.global_rank, self.score.pp, self.score.accuracy, self.score.play_count, self.score.total_hits

            cr = self._calc(self.score.country_rank, crank, True, False)
            gr = self._calc(self.score.global_rank, grank, True, False)
            pp = self._calc(self.score.pp, _pp, False, True)
            acc = self._calc(self.score.accuracy, accuracy, False, False)
            pc = self._calc(self.score.play_count, playcount, False, False)
            hit = self._calc(self.score.total_hits, hit_count, False, False)

            im = Image.new('RGBA', (1000, 1322))
            text_im = ImageDraw.Draw(im)
            trfont = DrawText(text_im, TrFont)
            mrfont = DrawText(text_im, MeiryoR)
            # 头图
            im.alpha_composite(user_header_img, (0, 100))
            # 底图
            im.alpha_composite(info_img)
            # 头像
            user_icon = draw_filler(user_icon_img, 25)
            im.alpha_composite(user_icon, (50, 148))
            # 地区
            im.alpha_composite(country_img, (400, 394))
            # supporter
            if self.user.is_supporter:
                im.alpha_composite(supporter_img, (400, 280))
            # 经验
            if self.user.statistics.level.progress != 0:
                im.alpha_composite(exp_left_img, (50, 646))
                im.alpha_composite(exp_center_img, (54, 646))
                im.alpha_composite(exp_right_img, (int(54 + exp_width), 646))
            # 模式
            trfont.draw(935, 50, 45, GameModeNum[self.user.play_mode], anchor='rm')
            # 名字
            trfont.draw(400, 205, 50, self.user.username, anchor='lm')
            # 地区排名
            mrfont.draw(495, 448, 30, f'#{self.score.country_rank:,}({cr.op}{cr.value:,})' if cr.value != 0 else f'#{self.score.country_rank:,}', anchor='lb')
            # 等级
            trfont.draw(900, 650, 25, self.score.level.current, anchor='mm')
            # 经验百分比
            trfont.draw(750, 660, 20, f'{self.score.level.progress}%', anchor='rt')
            # 全球排名
            trfont.draw(55, 785, 35, f'#{self.score.global_rank:,}')
            if gr.value != 0:
                mrfont.draw(65, 820, 20, f'{gr.op}{gr.value:,}')
            # pp
            trfont.draw(295, 785, 35, f'{self.score.pp:,}')
            if pp.value != 0:
                mrfont.draw(305, 820, 20, f'{pp.op}{self.score.pp:.2f}')
            # SS - A
            for gc_num, v in enumerate(self.score.grade_counts.dict().values()):
                trfont.draw(493 + 100 * gc_num, 775, 30, f'{v:,}', anchor='mt')
            # ranked总分
            trfont.draw(935, 895, 40, f'{self.score.ranked_score:,}', anchor='rt')
            # acc
            trfont.draw(935, 965, 40, f'{self.score.accuracy:.2f}%({acc.op}{acc.value:.2f}%)' if acc.value != 0 else f'{self.score.accuracy:.2f}%', anchor='rt')
            # 游玩次数
            trfont.draw(935, 1035, 40, f'{self.score.play_count:,}({pc.op}{pc.value:,})' if pc.value != 0 else f'{self.score.play_count:,}', anchor='rt')
            # 总分
            trfont.draw(935, 1105, 40, f'{self.score.total_score:,}', anchor='rt')
            # 总命中
            trfont.draw(935, 1175, 40, f'{self.score.total_hits:,}({hit.op}{hit.value:,})' if hit.value != 0 else f'{self.score.total_hits:,}', anchor='rt')
            # 游玩时间
            trfont.draw(935, 1245, 40, f'{self.score.play_time:,}', anchor='rt')

            return im
        except Exception as e:
            sv.logger.error(f'制图错误：{traceback.format_exc()}')
            raise DrawImageError(type(e))
 
        
async def draw_info(user_id: Union[int, str], mode: str) -> Union[str, MessageSegment]:
    try:
        sv.logger.info(f'Start Request OsuAPI {playtime(time() * 1000)}')
        UserInfo = await osuApi.user(user_id, mode=mode)
        sv.logger.info(f'Ending Request OsuAPI {playtime(time() * 1000)}')
        if not UserInfo:
            return '未查询到该玩家'
        userData = User(**UserInfo)
        
        if not userData.statistics.play_count:
            return f'该玩家尚未游玩过{GameModeName[mode]}模式'

        data = DrawInfo(userData)
        im = await data.draw()
        # 输出
        msg = MessageSegment.image(img2b64(im))
    except DrawImageError as e:
        sv.logger.error(f'制图错误：{traceback.format_exc()}\n类型：{e.value}')
        msg = f'Error: {e.value}'
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.format_exc()}')
        msg = f'Error: {type(e)}'
    return msg