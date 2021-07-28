# osuv2

基于HoshinoBot v2的osu api v2版本的查询模块

项目地址：https://github.com/Yuri-YuzuChaN/osuv2

## 使用方法

1. 将该项目放在HoshinoBot插件目录 `modules` 下，或者clone本项目 `git clone https://github.com/Yuri-YuzuChaN/osuv2`
2. 在`token.json`填入申请的`client_id`，`client_secret`，`access_token`，`refresh_token`，[如何申请token](#如何申请token)
3. 修改`http.py`文件中的`FILEHTTP`字符串，将地址改为自己的服务器IP或域名，`:{PORT}/map`请勿删除
4. pip以下依赖：`pillow`，`pyttanko`，`matplotlib`，`traceback`, `Maniera`，`filetype`
5. 在`config/__bot__.py`模块列表中添加`osuv2`
6. 重启HoshinoBot

**注：`pillow`需要高于等于8.0.0版本**

**注：`Maniera`依赖需自行修改文件第51行，添加`encoding='utf-8'`**

```python
{
    with open(self.osupath, encoding='utf-8') as bmap:
        textContent = bmap.read()
        lines = textContent.splitlines()
}
```

## 如何申请token

1. 打开osu个人设置页面：https://osu.ppy.sh/home/account/edit ，拉到最下面开放授权页面。

2. 点击`新的 OAuth 应用`，在弹出的窗口填入`应用名称`（随意），`应用回调链接`（第三方网站或自己的网站），点击`注册应用程序`，此时你已经拥有了`OAuth客户端`，包括`token.json`需要的`client_id`（客户端ID）、`client_secret`（客户端密钥）、以及申请token使用的`应用回调链接`。

3. 在浏览器地址栏输入`https://osu.ppy.sh/oauth/authorize?response_type=code&client_id=(客户端ID)&redirect_uri=(应用回调链接)&scope=public`（不需要括号）

4. 在跳转的页面点击授权（该步骤可能没有），授权后将会回调到你申请时填入的`应用回调链接`，地址栏会出现该链接：`https://xxx.com/?code=code`，保存`code`，`code`为一串非常长的代码，`code`只能使用一次，使用过后需要重新申请。

5. 编辑`osuv2`目录下的`get_token.py`文件，填入`code`、`client_id`、`client_secret`、`redirect_uri`，保存并执行该脚本，执行成功后目录下会出现`token.json`文件，否则为`请重新进行第三步.json`文件，`token.json`的内容为：

   ```json
   {
       "client_id": 0000, //客户端ID
       "client_secret": "string", //客户端密钥
       "access_token": "verylongstring", //访问令牌
       "refresh_token": "anotherlongstring", //刷新令牌
   }
   ```

   如果内容不是如上内容，请重新进行第三步

6. 由于`access_toekn`的有效期仅有24小时，在运行bot后，每天23时自动更新`access_toekn`，如需更改更新时间，修改`__init__.py`第464行`hour`参数

7. 如果实在申请不到，可以联系我进行一对一教学（  QQ：806235364

## 指令说明
| 指令    | 功能             | 可选参数                        | 说明                                                         |
| :------ | :--------------- | :------------------------------ | :----------------------------------------------------------- |
| osuhelp | 查看指令大全     |                                 |                                                              |
| 更新OAuth | 手动更新OAuth令牌     |                                 | 用于OAuth令牌自动更新失败时，使用指令手动更新令牌  |
| info    | 查询信息         | 无                              | 查询自己                                                     |
|         |                  | [user]                          | 查询TA人                                                     |
|         |                  | :[mode]                         | 查询自己其它模式，`:`为触发词                                |
|         |                  | [user] :[mode]                  | 查询TA人其它模式                                             |
| bind    | 绑定             | [user]                          | 绑定用户名                                                   |
| unbind  | 解绑             | 无                              |                                                              |
| update  | 更改或更新       | mode [mode]                     | 更改模式                                                     |
|         |                  | [icon]                          | 更新自己的头像和头图                                         |
| recent  | 查询最近游玩记录 | 无                              | 查询自己最近的游玩记录                                       |
|         |                  | [user]                          | 查询TA人最近的游玩记录                                       |
|         |                  | :[mode]                         | 查询自己最近游玩其它模式记录，`:`为触发词                    |
|         |                  | [user] :[mode]                  | 查询TA人最近游玩其它模式记录                                 |
| score   | 查询成绩         | [mapid]                         | 查询地图成绩                                                 |
|         |                  | [mapid] :[mode]                 | 查询地图其它模式成绩，`:`为触发词                            |
|         |                  | [user] [mapid]                  | 查询TA人地图成绩                                             |
|         |                  | [user] [mapid] :[mode]          | 查询TA人地图其它模式成绩                                     |
| bp      | 查询bp榜成绩     | [num]                           | 查询bp成绩                                                   |
|         |                  | [num] [+mods]                   | 查询bp附加mods成绩，`+`为mods触发词，多mods之间使用半角逗号  |
|         |                  | [mode] [num]                    | 查询其他模式的bp成绩                                         |
|         |                  | [user] [num]                    | 查询TA人bp成绩                                               |
|         |                  | [user] [num] +[mods]            | 查询TA人bp附加mods成绩                                       |
|         |                  | [mode] [user] [num]             | 查询TA人其他模式bp成绩                                       |
|         |                  | [mode] [user] [num] +[mods]     | 查询TA人其他模式加mods的bp成绩                               |
|         |                  | [min-max]                       | 查询bp范围内成绩，最多10个                                   |
|         |                  | [mode] [min-max]                | 查询其它模式bp范围内成绩                                     |
|         |                  | [min-max] +[mods]               | 查询bp范围内加mods的成绩，`+`为mods触发词，多mods之间使用半角逗号 |
|         |                  | [mode] [min-max] +[mods]        | 查询其它模式bp范围内加mods的成绩                             |
|         |                  | [user] [min-max]                | 查询TA人bp，`-`为范围触发词，最多10个                        |
|         |                  | [mode] [user] [min-max]         | 查询TA人其它模式bp                                           |
|         |                  | [user] [min-max] +[mods]        | 查询TA人bp，`+`为mods触发词，多mods之间使用半角逗号          |
|         |                  | [mode] [user] [min-max] +[mods] | 查询TA人其它模式bp范围内加mods的成绩                         |
| map     | 查询地图信息     | [mapid]                         | 查询地图信息                                                 |
|         |                  | [mapid] +[mods]                 | 查询地图加mod的信息，仅计算PP                                |
| getbg   | 提取背景         | [mapid]                         | 提取地图背景                                                 |
| smap    | 查询地图         | [keyword]                       | 查询关键词的地图，默认搜索std模式ranked状态                  |
|         |                  | -c [keyword]                    | 同上，使用血猫搜索，`-s`为使用sayobot搜索                    |
|         |                  | [mode] [keyword]                | 查询其它模式ranked状态的关键词地图                           |
|         |                  | [keyword] rs=[status]           | 查询关键词的地图，`rs=`为状态触发词，`status`为数字          |
|         |                  | [mode] [keyword] rs=[status]    | 查询其它模式和状态的关键词地图                               |
| bmap    | 查询图组信息     | [setid]                         | 查询图组信息                                                 |
|         |                  | -b [mapid]                      | 使用地图id查询图组信息                                       |
| osudl   | 下载地图上传到群 | [setid]                         | 下载地图                                                     |

`status`：0-5分别为Ranked，Qualified，Loved，Pending，WIP，Graveyard

`mode`：0-3分别为std，taiko，ctb，mania

## 即将实现

1. ~~pp+数据~~

## 更新说明

**2021-07-29**

1. 更新新版渐变色难度模式图标

**2021-07-09**

1. 修复ctb和taiko模式`pp`变量错误

**2021-07-08**

1. 修复无法自动更新个人信息的问题

**2021-07-06**

1. 数据处理移动到`data.py`
2. 修改部分函数名称
3. 不再保存cover及badges图片
4. 修改所有成绩图

**2021-06-11**

1. 为区分图组与单图，已将图组`bmapid`修改为`setid`
2. 修复地图在没有背景制图错误的问题
3. 修复`get_token.py`无法申请token的问题
4. 修改报错提示
5. 将`draw.py`文件的`FILEHTTP`字符串移至`http.py`

**2021-05-29**

1. 新增查询图组功能，指令：`bmap [bmapid]`，`bmapid`为图组id，或者使用地图id`mapid`查询图组，在指令加`-b`，例：`bmap -b [mapid]`
2. 修改`map`指令，并增加音乐分享，音乐分享需使用`http`服务，请自行修改`draw.py`文件中的`FILEHTTP`字符串，将地址改为自己的服务器IP或域名，`:{PORT}/map`请勿删除
3. 完善api请求，准确返回无法查询的错误
4. 修复所有指令无法查询TA人的问题
5. 修复指令@人无法查询的问题

**2021-05-23**

1. 修改`bp`指令，改用图片的形式发送
2. `info`，`recent`，`score`指令可使用@方式查询群友的成绩或信息

**2021-05-16**

1. 修改`map`指令，改用图片的形式发送
2. 修复`smap`指令搜索个别ranked地图没有背景的问题

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
