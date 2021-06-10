import nonebot, os, filetype
from hoshino.config import PORT
from quart import request, make_response

PATH = os.path.join(os.path.dirname(__file__), 'osufile', 'map')
app = nonebot.get_bot().server_app

FILEHTTP = f'http://xxxxxx.com:{PORT}/map'

@app.route('/map/<int:mapid>/<string:filename>')
async def music(mapid, filename):
    if request.method == 'GET':
        if filename and '.osu' not in filename:
            file = os.path.join(PATH, str(mapid), filename)
            content_type = filetype.guess(file).mime
            image = open(file, 'rb').read()
            response = await make_response(image)
            response.headers['Content-Type'] = content_type
            return response
