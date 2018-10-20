import requests, fnmatch


class Api:
    def __init__(self, token, state, base):
        self.session = requests.Session()
        self.token = token
        self.session.auth = self.token_auth
        self.state = state
        self.base = base

    def token_auth(self, req):
        req.headers['Authorization'] = f'token {self.token}'
        return req

    def test_api(self):
        print(self.session.get('https://api.github.com/user'))

    def get_prs(self, reposlug):
        payload = {'state': self.state, 'per_page': 100}
        result = {'PR': []}
        if self.base:
            payload['base'] = self.base
        response = self.session.get(f'https://api.github.com/repos/{reposlug}/pulls', params=payload)
        result['status_code'] = response.status_code
        if response.status_code == 200:
            for pr in response.json():
                result['PR'].append(pr['number'])
            while 'next' in response.links.keys():
                response = self.session.get(response.links['next']['url'], params=payload)
                for pr in response.json():
                    result['PR'].append(pr['number'])
        # print(result)
        return result

    def get_files(self, slug, pr):
        result = []
        payload = {'per_page': 100}
        response = self.session.get(f'https://api.github.com/repos/{slug}/pulls/{pr}/files', params=payload)
        if response.status_code == 200:
            for file in response.json():
                result.append(file['filename'])
            while 'next' in response.links.keys():
                response = self.session.get(response.links['next']['url'], params=payload)
                for file in response.json():
                    result.append(file['filename'])
        # print(result)
        return result

    def get_labels(self, slug, pr):
        return self.session.get(f'https://api.github.com/repos/{slug}/issues/{pr}/labels')

    def create_labels(self, slug, labels):
        for label in labels:
            payload = {'name': label, 'color': 'f29513'}
            # print(payload)
            self.session.post(f'https://api.github.com/repos/{slug}/labels', json=payload)
            # print(r.json())

    def post_labels(self, slug, pr, labels):
        payload = {"labels": list(labels)}
        # print(payload)
        return self.session.put(f'https://api.github.com/repos/{slug}/issues/{pr}/labels', json=payload)

    def label_pr(self, slug, pr, label_conf, delete):
        files = self.get_files(slug, pr)
        ret = {}
        new_labels = set()
        old_labels = set()

        response = self.get_labels(slug, pr)
        for label in response.json():
            old_labels.add(label['name'])
        known_labels = set(label_conf.keys())
        self.create_labels(slug, known_labels)

        for file in files:
            for label in label_conf.keys():
                for expr in label_conf[label].splitlines():
                    if fnmatch.fnmatch(file, expr):
                        new_labels.add(label)

        ret['url'] = f'https://github.com/{slug}/pull/{str(pr)}'
        ret['labels'] = []
        for label in new_labels - old_labels:
            ret['labels'].append((label, '+'))
        if delete:
            for label in (old_labels & known_labels) - new_labels:
                ret['labels'].append((label, '-'))
            final_labels = new_labels.union(old_labels - known_labels)
        else:
            final_labels = old_labels.union(new_labels)
        for label in old_labels & new_labels:
            ret['labels'].append((label, '='))
        response = self.post_labels(slug, pr, sorted(final_labels))
        # print(response.json())
        ret['status'] = 'OK' if response.status_code == 200 else 'FAIL'
        return ret
