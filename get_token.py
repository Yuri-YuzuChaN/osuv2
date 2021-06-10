import requests, json

code = ''
client_id = 0
client_secret = ''
redirect_uri = ""

def get_access_token():
    api = 'https://osu.ppy.sh/oauth/token'
    data = {
        'grant_type' : 'authorization_code',
        'client_id' : client_id,
        'client_secret' : client_secret,
        "redirect_uri": redirect_uri,
        'code' : code
    }
    res = requests.post(api, data=data)
    if res.status_code == 200:
        OAuth = res.json()
        token = {
            'client_id' : client_id,
            'client_secret' : client_secret,
            'access_token' : OAuth['access_token'],
            'refresh_token' : OAuth['refresh_token']
        }
        return token
    else:
        return False

if __name__ == '__main__' :
    token = get_access_token()
    if isinstance(token, dict):
        name = 'token.json'
    else:
        name = '请重新进行第三步.json'
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(token, f, ensure_ascii=False, indent=2)
