import base64
import urllib.request
import ssl
import json

class Mixpanel(object):

    ENDPOINT = 'https://data.mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, api_secret):
        self.api_secret = api_secret

    def request(self, methods, params, http_method='GET', format='json'):
        """
            methods - List of methods to be joined, e.g. ['events', 'properties', 'values']
                      will give us http://mixpanel.com/api/2.0/events/properties/values/
            params - Extra parameters associated with method
        """
        params['format'] = format
        # print(base64.b64encode(self.api_secret).decode("ascii"))

        request_url = '/'.join([self.ENDPOINT, str(self.VERSION)] + methods)
        if http_method == 'GET':
            data = None
            request_url = request_url + '/?' + self.unicode_urlencode(params)
        else:
            data = self.unicode_urlencode(params)

        auth = base64.b64encode(self.api_secret).decode("ascii")
        headers = {'Authorization': 'Basic {encoded_secret}'.format(encoded_secret=auth)}

        request = urllib.request.Request(request_url, data, headers)
        # print(request)
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(request, context=context, timeout=120)
        str_response = response.read().decode('utf8')
        lines = str_response.splitlines(True)
        records = []
        for line in lines:
            obj = json.loads(line)
            records.append(obj)
        return records

    def unicode_urlencode(self, params):
        """
            Convert lists to JSON encoded strings, and correctly handle any
            unicode URL parameters.
        """
        if isinstance(params, dict):
            params = list(params.items())
        for i,param in enumerate(params):
            if isinstance(param[1], list):
                params.remove(param)
                params.append ((param[0], json.dumps(param[1]),))

        return urllib.parse.urlencode(
            [(k, v) for k, v in params]
        )
