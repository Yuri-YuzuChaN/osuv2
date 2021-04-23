import requests

code = ''

def get_access_token():
    api = 'https://osu.ppy.sh/oauth/token'
    data = {
        'grant_type' : 'authorization_code',
        'client_id' : 0,
        'client_secret' : '',
        "redirect_uri": "",
        'code' : code
    }
    res = requests.post(api, data=data)
    if res.status_code != 200:
        return
    return res.text

token = open('cache.json', 'w', encoding='utf-8')
print(get_access_token(), file=token)
token.close()