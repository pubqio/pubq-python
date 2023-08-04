import requests


class REST:
    def __init__(self, applicationId, applicationKey, applicationSecret):
        self.applicationId = applicationId
        self.applicationKey = applicationKey
        self.applicationSecret = applicationSecret

        self.baseUrl = "https://rest.pubq.io"
        self.headers = {
            "Id": self.applicationId,
            "Key": self.applicationKey,
            "Secret": self.applicationSecret,
        }

    def publish(self, channel, data):
        endpoint = f"{self.baseUrl}/v1/messages/publish"
        payload = {"channel": channel, "data": data}

        response = requests.post(endpoint, json=payload, headers=self.headers)

        if response.status_code == 204:
            return response.json()
        else:
            raise Exception(f"Failed to publish message: {response.text}")
