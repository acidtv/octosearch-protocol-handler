import json
import base64
import hmac

data = {
    'url': 'smb://ariad/software/alextest/test.txt'
}

payload = json.dumps(data).encode()
base64_payload = base64.b64encode(payload)

secret = b'fdhjs89fdhs8'
h = hmac.new(secret, base64_payload, digestmod='sha256')

url = r"octosearch://v1/open/" + base64_payload.decode() + "/" + h.hexdigest()

print(url)
