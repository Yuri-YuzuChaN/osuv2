# osuv2

基于HoshinoBot v2的osu api v2版本的查询模块

项目地址：https://github.com/Yuri-YuzuChaN/osuv2

## 使用方法

1. 将该项目放在HoshinoBot插件目录 `modules` 下，或者clone本项目 `git clone https://github.com/Yuri-YuzuChaN/osuv2`
2. 在`token.json`填入申请的`client_id`，`client_secret`，`access_token`，`refresh_token`，[如何申请token](#如何申请token)
3. pip以下依赖：`pillow`，`oppai`，`pyttanko`，`matplotlib`，`traceback`, `Maniera`
4. 在`config/__bot__.py`模块列表中添加`osuv2`
5. 重启HoshinoBot

**注：`pillow`需要高于等于8.0.0版本，Windows环境下`oppai`模块已自带，`oppai`目前必须在`py38 64bit`环境下才可运行**

**注：`Maniera`依赖需自行修改文件第51行，添加`encoding='utf-8'`**

```python
{
    with open(self.osupath, encoding='utf-8') as bmap:
        textContent = bmap.read()
        lines = textContent.splitlines()
}
```

**如果环境为Linux，请`pip install oppai`，并将`osu_pp.py`中`.oppai.oppai`改为`oppai`**

**现版本pp计算模块更换为`pyttanko`，基本脱离`oppai`模块，现仅用于时长计算**

## 如何申请token

1. 打开osu个人设置页面：https://osu.ppy.sh/home/account/edit ，拉到最下面开放授权页面

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
| 指令   | 功能                                                         | 可选参数                 | 说明                                                         |
| :----- | :----------------------------------------------------------- | :----------------------- | :----------------------------------------------------------- |
| info   | 查询信息                                                     | 无                       | 查询自己                                                     |
|        |                                                              | [user]                   | 查询TA人                                                     |
|        |                                                              | [:mode]                  | 查询自己其它模式                                             |
|        |                                                              | [user] [:mode]           | 查询TA人其它模式，`:`为触发词                                |
| bind   | 绑定                                                         | [user]                   | 绑定用户名                                                   |
| unbind | 解绑                                                         | 无                       |                                                              |
| update | 更改或更新                                                   | [mode] [:mode]           | 更改模式，`:`为触发词                                        |
|        |                                                              | [icon]                   | 更新自己的头像和头图                                         |
| recent | 查询最近游玩记录                                             | 无                       | 查询自己最近的游玩记录                                       |
|        |                                                              | [user]                   | 查询TA人最近的游玩记录                                       |
|        |                                                              | [:mode]                  | 查询自己最近游玩其它模式记录，`:`为触发词                    |
|        |                                                              | [user] [:mode]           | 查询TA人最近游玩其它模式记录，`:`为触发词                    |
| score  | 查询成绩                                                     | [mapid]                  | 查询地图成绩                                                 |
|        |                                                              | [mapid] [:mode]          | 查询地图其它模式成绩，`:`为触发词                            |
|        |                                                              | [user] [mapid]           | 查询TA人地图成绩                                             |
|        |                                                              | [user] [mapid] [:mode]   | 查询TA人地图其它模式成绩，`:`为触发词                        |
| *bp    | 查询bp榜成绩，可附带模式，1、2、3分别为taiko、ctb、mania，例：`bp3 1` | [num]                    | 查询bp成绩                                                   |
|        |                                                              | [num] [+mods]            | 查询bp附加mods成绩，`+`为mods触发词，多mods之间使用半角逗号  |
|        |                                                              | [user] [num]             | 查询TA人bp成绩                                               |
|        |                                                              | [user] [num] [+mods]     | 查询TA人bp附加mods成绩，`+`为mods触发词，多mods之间使用半角逗号 |
|        |                                                              | [min-max]                | 查询bp范围内成绩，最多10个                                   |
|        |                                                              | [min-max] [+mods]        | 查询bp范围内成绩，最多10个，`+`为mods触发词，多mods之间使用半角逗号 |
|        |                                                              | [user] [min-max]         | 查询TA人bp，`-`为范围触发词，最多10个                        |
|        |                                                              | [user] [min-max] [+mods] | 查询TA人bp，`-`为范围触发词，最多10个，`+`为mods触发词，多mods之间使用半角逗号 |
| map    | 查询地图的信息                                               | [mapid]                  | 查询地图信息                                                 |
| getbg  | 提取背景                                                     | [mapid]                  | 提取地图信息                                                 |
| *smap  | 查询地图，可附带模式，1、2、3分别为taiko、ctb、mania，例：`smap3 GHOST` | [keyword]                | 查询关键词的地图，默认搜索std模式ranked状态                  |
|        |                                                              | [keyword] [rs=status]    | 查询关键词的其它状态地图，`rs=`为状态触发词，1-5分别为ranked，Qualified，Loved，Pending，Graveyard |
| osudl  | 下载地图上传到群                                             | [bmapid]                 | 下载地图，`bmapid`为地图组id，非单图id                       |

## 即将实现

1. ~~pp+数据~~

## 更新说明

**2021-05-06**

1. 新增地图搜索功能，指令：`[smap keyword]`，`keyword`为关键词，可多个，默认搜索std模式ranked状态

2. 新增地图下载功能，指令：`[osudl bmapid]`，`bmapid`为地图组id，非单图id

**2021-05-04**

1. 支持`mania`模式pp计算

**2021-05-02**

1. 修复`map`指令查询非ranked图时出错的问题
2. 修复`map`指令查询mania图时无max combo的问题

**2021-04-27**

1. 修复撒泼特错位
2. 修复info的游玩时间
3. 对比信息无法更新

**2021-04-23**

1. 船新版本的osu插件
