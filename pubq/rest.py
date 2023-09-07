import requests
import base64


class REST:
    def __init__(self, applicationKey):
        self.applicationKey = applicationKey

        # Base64 encode key
        encodedKey = base64.b64encode(self.applicationKey.encode('utf-8'))
        stringifiedKey = encodedKey.decode('utf-8')

        self.baseUrl = "https://rest.pubq.io"
        self.headers = {
            "Authorization": "Basic " + stringifiedKey,
        }

    def publish(self, channel, data):
        endpoint = f"{self.baseUrl}/v1/channels/messages"
        payload = {"channel": channel, "data": data}

        response = requests.post(endpoint, json=payload, headers=self.headers)

        if response.status_code == 204:
            return response.json()
        else:
            raise Exception(f"Failed to publish message: {response.text}")
