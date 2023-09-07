import asyncio
from pubq.realtime import RealTime
from pubq.rest import REST
import time


def onCreate():
    print("Creating socket instance...")


def onConnect(socket):
    print("Connected to PUBQ! " + str(socket))


def onDisconnect(socket):
    print("Disonnected from PUBQ! " + str(socket))


async def main():
    application_key = "YOUR_API_KEY"

    realtime = RealTime(application_key)

    rest = REST(application_key)

    channel = "test_channel"
    data = "Hello!"

    realtime.emitter.add_listener("create", onCreate)
    realtime.emitter.add_listener("connect", onConnect)
    realtime.emitter.add_listener("disconnect", onDisconnect)

    def onAuthenticate(event):
        print("Authenticated " + str(event))
        realtime.emitter.add_listener("emitAck", onEmitAck)
        realtime.emitter.add_listener("subscribeAck", onSubscribeAck)
        realtime.subscribe(channel, onChannelMessage)
        time.sleep(5)
        rest.publish(channel, data)

    def onEmitAck(event):
        print("Acked emit " + str(event))

    def onSubscribeAck(event):
        print("Acked emit " + str(event))

    def onChannelMessage(channel, data):
        print("Received new data from channel '" +
              str(channel) + "': " + str(data))

    realtime.emitter.add_listener("authenticate", onAuthenticate)

asyncio.run(main())
