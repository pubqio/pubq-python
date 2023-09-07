# PUBQ Python SDK

[PUBQ](https://pubq.io) is a pub/sub channels cloud and this is the official Python client library including both real-time and REST interfaces.

To meet PUBQ and see more info and examples, please read the [documentation](https://pubq.io/docs).

# Getting Started

Follow these steps to just start building with PUBQ in Python or see the [Quickstart guide](https://pubq.io/docs/getting-started/quickstart) which covers more programming languages.

## Install with package manager

The Python SDK is available as PyPI package:

```bash
pip install pubq
```

## Interacting with PUBQ

Get your application id and key from [PUBQ dashboard](https://dashboard.pubq.io) by [creating a new app](https://dashboard.pubq.io/applications/create) or use existing one.

Connect to PUBQ:

```python
import asyncio
from pubq.realtime import RealTime

def onConnect(socket):
    print("Connected to PUBQ!")

async def main():

    realtime = RealTime("YOUR_API_KEY")
    realtime.emitter.add_listener("connect", onConnect)

asyncio.run(main())
```

Subscribe a channel and listen for any data publish to receive::

```python
realtime.subscribe('my-channel', onChannelMessage)

def onChannelMessage(channel, data):
    print("Received new data: '" + str(data))
```

Publish a message with REST interface:

```python
from pubq.rest import REST

if __name__ == "__main__":
    rest = REST("YOUR_API_KEY");
    rest.publish("my-channel", "Hello!");
```

# Development

Please, read the [contribution guide](https://pubq.io/docs/basics/contribution).

## Setup

```bash
git clone git@github.com:pubqio/pubq-python.git
cd ./pubq-python/
poetry install
```

## Tests

To run tests using pytest:

```bash
poetry run pytest
```
