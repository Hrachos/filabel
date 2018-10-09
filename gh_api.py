import requests


class Api:
    def __init__(self, token):
        self.session = requests.Session()
        self.token = token
        self.session.auth = self.token_auth

    def token_auth(self, req):
        req.headers['Authorization'] = f'token {self.token}'
        return req

    def test_api(self):
        print(self.session.get('https://api.github.com/user/'))
