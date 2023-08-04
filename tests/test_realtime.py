import asyncio
from pubq.realtime import RealTime


def onCreate():
    print("Creating socket instance...")


def onConnect(socket):
    print("Connected to PUBQ! " + str(socket))


def onDisconnect(socket):
    print("Disonnected from PUBQ! " + str(socket))


async def main():

    rt = RealTime("rgaNOj", "k_be5cb4cbe6ba4bf891349af1d6b26bbf")

    rt.emitter.add_listener("create", onCreate)
    rt.emitter.add_listener("connect", onConnect)
    rt.emitter.add_listener("disconnect", onDisconnect)

    def onAuthenticate(event):
        print("Authenticated " + str(event))
        rt.emitter.add_listener("emitAck", onEmitAck)
        rt.emitter.add_listener("subscribeAck", onSubscribeAck)
        rt.subscribe('test', onChannelMessage)

    def onEmitAck(event):
        print("Acked emit " + str(event))

    def onSubscribeAck(event):
        print("Acked emit " + str(event))

    def onChannelMessage(channel, data):
        print("Received new data from channel '" +
              str(channel) + "': " + str(data))

    rt.emitter.add_listener("authenticate", onAuthenticate)

asyncio.run(main())
