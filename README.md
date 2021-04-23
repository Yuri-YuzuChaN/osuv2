# osuv2

基于HoshinoBot v2的osu api v2版本的查询模块

项目地址：https://github.com/Yuri-YuzuChaN/osuv2

## 使用方法

1. 将该项目放在HoshinoBot插件目录 `modules` 下，或者clone本项目 `git clone https://github.com/Yuri-YuzuChaN/osuv2`
2. 在`token.json`填入申请的`client_id`，`client_secret`，`access_token`，`refresh_token`，[如何申请token](#如何申请token)
3. pip以下依赖：`pillow`，`oppai`，`pyttanko`，`matplotlib`，`traceback`
4. 在`config/__bot__.py`模块列表中添加`osuv2`
5. 重启HoshinoBot

**注：`pillow`需要高于等于8.0.0版本，Windows环境下`oppai`模块已自带，`oppai`目前必须在`py38 64bit`环境下才可运行**

**如果环境为Linux，请`pip install oppai`，并将`osu_pp.py`中`.oppai.oppai`改为`oppai`**

**现版本pp计算模块更换为`pyttanko`，基本脱离`oppai`模块，现仅用于时长计算**

## 如何申请token

1. 打开osu个人设置页面：https://osu.ppy.sh/home/account/edit，拉到最下面开放授权页面

2. 点击`新的 OAuth 应用`，在弹出的窗口填入`应用名称`（随意），`应用回调链接`（第三方网站或自己的网站），点击`注册应用程序`，此时你已经拥有了`OAuth客户端`，包括`token.json`需要的`client_id`（客户端ID）、`client_secret`（客户端密钥）、以及申请token使用的`应用回调链接`

3. 在浏览器地址栏输入`https://osu.ppy.sh/oauth/authorize?response_type=code&client_id=(客户端ID)&redirect_uri=(应用回调链接)&scope=public`（不需要括号），在跳转的页面点击授权（该步骤可能没有），授权后将会回调到你申请时填入的`应用回调链接`，地址栏会出现该链接：`https://xxx.com/?code=code`，保存`code`，`code`为一串非常长的代码

4. 编辑`osuv2`目录下的`get_token.py`文件，填入`code`、`client_id`、`client_secret`、`redirect_uri`，保存并执行该脚本，目录下会出现`cache.json`文件，如果按照上面的步骤一步步完成，`cache.json`的内容为：

   ```json
   {
       "token_type": "Bearer",
       "expires_in": 86400,
       "access_token": "verylongstring",
       "refresh_token": "anotherlongstring",
   }
   ```

   如果内容不是如上内容，请重新进行第三步

5. 申请完成后在`token.json`填入申请的`client_id`，`client_secret`，`access_token`，`refresh_token`，由于`access_toekn`的有效期仅有24小时，在运行bot后，每天23时自动更新`access_toekn`，如需更改更新时间，修改`__init__.py`第295行`hour`参数

6. 如果实在申请不到，可以联系我进行一对一教学（  QQ：806235364

## 指令说明

- `[info]`查询自己的信息
- `[info :mode]`查询自己在 mode 模式的信息
- `[info user]`查询 user 的信息
- `[info user :mode]`查询 user 在 mode 模式的信息
- `[bind user]`绑定用户名 user
- `[unbind]`解绑
- `[update mode mode]`更改默认查询的模式
- `[update icon]`更新自己头像和头图
- `[recent]`查询自己最近游玩的成绩
- `[recent :mode]`查询自己最近游玩 mode 模式的成绩
- `[recent user]`查询 user 最近游玩的成绩
- `[recent user :mode]`查询 user 最近游玩 mode 模式的成绩
- `[score mapid]`查询自己在 mapid 的成绩
- `[score mapid :mode]`查询自己在 mapid  mode 模式的成绩
- `[score user mapid]`查询 user 在 mapid 的成绩
- `[score user mapid :mode]`查询 user 在 mapid  mode 模式的成绩
- `[map mapid]`查询 mapid 地图的信息
- `[getbg mapid]`提取 mapid 地图的BG
- `[bp num]`查询自己bp榜第 num 的成绩
- `[bp user num]`查询 user bp榜第 num 的成绩
- `[bp min-max]`查询自己bp榜第 min 到 max 的成绩
- `[bp user min-max]`查询 user bp榜第 min 到 max 的成绩
- `[bp num +DT,HD]`查询自己bp榜加`DT,HD`后的第 num 的成绩
- `[bp user num +DT,HD]`查询 user bp榜加`DT,HD`后的第 num 的成绩
- `[bp min-max +DT,HD]`查询自己bp榜加`DT,HD`后的第 min 到 max 的成绩
- `[bp user min-max +DT,HD]`查询 user bp榜加`DT,HD`后的第 min 到 max 的成绩
- `mode` : `0 `std, `1` taiko, `2` ctb, `3` mania
- bp扩展 `bp`: std, `bp1`: taiko, `bp2`: ctb, `bp3`: mania

**除`std`模式外，查询其它模式需带上`mode`**
**`bp`指令加多mod的必须使用半角逗号**

## 即将实现

1. ~~pp+数据~~

## 更新说明

1. 2021-04-23
   船新版本的osu插件
