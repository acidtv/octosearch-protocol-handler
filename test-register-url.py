import json
import base64
# import hmac

data = {
    'url': 'http://foo',
    'secret': 'fdhjs89fdhs8'
}

payload = json.dumps(data).encode()
base64_payload = base64.b64encode(payload)

url = r"octosearch://v1/register/" + base64_payload.decode()

print(url)
