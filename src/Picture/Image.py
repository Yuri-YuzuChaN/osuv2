import base64
import math
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from time import localtime, strftime
from typing import Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from ... import CropSize, GameModeNum, WorkDir


class DrawText:

    def __init__(self, image: ImageDraw.ImageDraw, font: Path) -> None:
        self._img = image
        self._font = str(font)

    def get_box(self, text: str, size: int):
        return ImageFont.truetype(self._font, size).getbbox(text)

    def draw(self,
            pos_x: int,
            pos_y: int,
            size: int,
            text: str,
            color: Tuple[int, int, int, int] = (255, 255, 255, 255),
            anchor: str = 'lt',
            stroke_width: int = 0,
            stroke_fill: Tuple[int, int, int, int] = (0, 0, 0, 0),
            multiline: bool = False):

        font = ImageFont.truetype(self._font, size)
        if multiline:
            self._img.multiline_text((pos_x, pos_y), str(text), color, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
        else:
            self._img.text((pos_x, pos_y), str(text), color, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
    
    def draw_partial_opacity(self,
            pos_x: int,
            pos_y: int,
            size: int,
            text: str,
            po: int = 2,
            color: Tuple[int, int, int, int] = (255, 255, 255, 255),
            anchor: str = 'lt',
            stroke_width: int = 0,
            stroke_fill: Tuple[int, int, int, int] = (0, 0, 0, 0)):

        font = ImageFont.truetype(self._font, size)
        self._img.text((pos_x + po, pos_y + po), str(text), (0, 0, 0, 128), font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
        self._img.text((pos_x, pos_y), str(text), color, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)


def draw_filler(img: Image.Image, radii: int) -> Image.Image:
    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形
    # 原图
    img = img.convert("RGBA")
    w, h = img.size
    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # 白色区域透明可见，黑色区域不可见
    img.putalpha(alpha)
    return img


def cropBG(size: str, path: Union[str, BytesIO]) -> Image.Image:
    bg = Image.open(path).convert('RGBA')
    bg_w, bg_h = bg.size[0], bg.size[1]
    fix_w, fix_h = CropSize[size]
    fix_scale = fix_h / fix_w
    bg_scale = bg_h / bg_w

    if bg_scale > fix_scale:
        scale_width = fix_w / bg_w
        width = int(scale_width * bg_w)
        height = int(scale_width * bg_h)
        sf = bg.resize((width, height))
        crop_height = (height - fix_h) / 2
        x1, y1, x2, y2 = 0, crop_height, width, height - crop_height
        crop_img = sf.crop((x1, y1, x2, y2))
        
    elif bg_scale < fix_scale:
        scale_height = fix_h / bg_h
        width = int(scale_height * bg_w)
        height = int(scale_height * bg_h)
        sf = bg.resize((width, height))
        crop_width = (width - fix_w) / 2
        x1, y1, x2, y2 = crop_width, 0, width - crop_width, height
        crop_img = sf.crop((x1, y1, x2, y2))
        
    else:
        crop_img = bg.resize((fix_w, fix_h))
        
    return crop_img


def starsDiff(mode: Union[int, str], stars: float) -> Image.Image:
        if mode in GameModeNum:
            mode = GameModeNum[mode].lower()
        else:
            mode = 'stars'
        default = 115
        if stars < 1:
            xp = 0
            default = 120
        elif stars < 2:
            xp = 120
            default = 120
        elif stars < 3:
            xp = 240
        elif stars < 4:
            xp = 355
        elif stars < 5:
            xp = 470
        elif stars < 6:
            xp = 585
        elif stars < 7:
            xp = 700
        elif stars < 8:
            xp = 815
        else:
            return Image.open(WorkDir / f'{mode}_expertplus.png').convert('RGBA')
        # 取色
        x = (stars - math.floor(stars)) * default + xp
        color = Image.open(WorkDir / 'color.png').load()
        r, g, b = color[x, 1]
        # 打开底图
        im = Image.open(WorkDir / f'{mode}.png').convert('RGBA')
        xx, yy = im.size
        # 填充背景
        sm = Image.new('RGBA', im.size, (r, g, b))
        sm.paste(im, (0, 0, xx, yy), im)
        # 把白色变透明
        for i in range(xx):
            for z in range(yy):
                data = sm.getpixel((i, z))
                if (data.count(255) == 4):
                    sm.putpixel((i, z), (255, 255, 255, 0))
        return sm


def strtime(time: str) -> str:
    old_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
    new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    return new_time


def playtime(date: int) -> str:
    return strftime('%Y-%m-%d %H:%M:%S', localtime(date / 1000))


def calc_songlen(len: int) -> str:
    map_len = list(divmod(int(len), 60))
    map_len[1] = map_len[1] if map_len[1] >= 10 else f'0{map_len[1]}'
    music_len = f'{map_len[0]}:{map_len[1]}'
    return music_len


def img2b64(img: Image.Image) -> str:
    bytes = BytesIO()
    img.save(bytes, 'PNG')
    base64_str = base64.b64encode(bytes.getvalue()).decode()
    return 'base64://' + base64_str
