import threading
import base64
import jwt
from pyee.base import EventEmitter as EventHandler
from socketclusterclient import Socketcluster


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class RealTime:
    def __init__(self, applicationKey, options=None):
        self.applicationKey = applicationKey
        self.options = options or {}

        self.socket = None

        self.CONNECTING = "connecting"
        self.OPEN = "open"
        self.CLOSED = "closed"

        self.AUTHENTICATED = "authenticated"
        self.UNAUTHENTICATED = "unauthenticated"

        self.SUBSCRIBED = "subscribed"
        self.PENDING = "pending"
        self.UNSUBSCRIBED = "unsubscribed"

        self.connectionState = None
        self.authenticationState = None

        defaultOptions = {
            "autoConnect": True,
            "autoReconnect": True,
            "autoSubscribe_onConnect": True,
            "connectTimeout": 20000,
            "ackTimeout": 10000,
            "timestampRequests": False,
            "timestampParam": "t",
            "authTokenName": "pubq.authToken",
            "binaryType": "arraybuffer",
            "batchOnHandshake": False,
            "batchOnHandshakeDuration": 100,
            "batchInterval": 50,
            "protocolVersion": 2,
            "wsOptions": {},
            "cloneData": False,
            "logger": False,
        }

        privateOptions = {
            "hostname": "rt.pubq.io",
            "secure": True,
            "port": 443,
            "path": "/",
        }

        self.options = {**defaultOptions, **self.options, **privateOptions}

        self.emitter = EventHandler()

        self._create()

    @threaded
    def _create(self):
        self.emitter.emit("create")

        self.socket = Socketcluster.socket(
            "wss://" + self.options["hostname"] + self.options["path"])

        self.socket.setBasicListener(
            self._onConnect, self._onDisconnect, self._onConnectError)

        self.socket.setAuthenticationListener(
            self._onSetAuthentication, self._onAuthentication)

        if self.options["logger"]:
            self.socket.enablelogger(True)

        if not self.options["autoReconnect"]:
            self.socket.setreconnection(False)

        if self.options["autoConnect"]:
            self.connect()

    def _onConnect(self, socket):
        self.connectionState = self.OPEN
        self.emitter.emit("connect", socket)

    def _onDisconnect(self, socket):
        self.connectionState = self.CLOSED
        self.emitter.emit("disconnect", socket)

    def _onConnectError(self, socket, error):
        self.emitter.emit(
            "error", {"socket": socket, "error": error})

    def _onSetAuthentication(self, socket, token):
        socket.setAuthtoken(token)
        self.connectionState = self.AUTHENTICATED

        decodedToken = self._jwtDecode(token)
        appId = decodedToken["public_key"].split(".")[0]
        self.applicationId = appId

        self.emitter.emit(
            "authenticate", {"socket": socket, "token": token})

    def _jwtDecode(self, token):
        try:
            # Get the algorithm from the token header
            header = jwt.get_unverified_header(token)
            algorithm = header.get('alg')

            # Decode the JWT token and get the payload
            decodedToken = jwt.decode(
                token, algorithms=[algorithm], options={"verify_signature": False})

            return decodedToken

        except jwt.ExpiredSignatureError:
            print("Token has expired.")
        except jwt.DecodeError:
            print("Invalid token.")
        except jwt.InvalidTokenError:
            print("Token is invalid.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _onAuthentication(self, socket, isAuthenticated):
        # Base64 encode key
        encodedKey = base64.b64encode(self.applicationKey.encode('utf-8'))
        stringifiedKey = encodedKey.decode('utf-8')

        if not isAuthenticated:
            self.authenticationState = self.UNAUTHENTICATED
            socket.emitack("#login", {
                "authorization": "Basic " + stringifiedKey,
            }, self._emitAck)
        else:
            self.authenticationState = self.AUTHENTICATED

    def _emitAck(self, key, error, object):
        self.emitter.emit(
            "emitAck", {"key": key, "object": object, "error": error})

    def connect(self):
        self.socket.connect()
        self.connectionState = self.CONNECTING

    def disconnect(self):
        self.socket.disconnect()
        self.connectionState = self.CLOSED

    def getState(self):
        return self.connectionState

    def isAuthenticated(self):
        if self.AUTHENTICATED == self.authenticationState:
            return True
        return False

    def deauthenticate(self):
        self.socket.setAuthtoken('')
        self.authenticationState = self.UNAUTHENTICATED

    def subscribe(self, channelName, channelMessageHandler):
        self.socket.subscribeack(
            f"{self.applicationId}/{channelName}", self._subscribeAck)
        self.socket.onchannel(
            f"{self.applicationId}/{channelName}", channelMessageHandler)

    def _subscribeAck(self, channel, error, object):
        if error == '':
            self.emitter.emit(
                "subscribeAck", {"channel": channel, "error": error, "object": object})

    def unsubscribe(self, channelName):
        self.socket.unsubscribeack(
            f"{self.applicationId}/{channelName}", self._unsubscribeAck)

    def _unsubscribeAck(self, channel, error, object):
        if error == '':
            self.emitter.emit("unsubscribeAck", {
                              "channel": channel, "error": error, "object": object})

    def subscriptions(self, includePending=False):
        return self.socket.getsubscribedchannels()

    def isSubscribed(self, channelName, includePending=False):
        return f"{self.applicationId}/{channelName}" in self.subscriptions(includePending)
