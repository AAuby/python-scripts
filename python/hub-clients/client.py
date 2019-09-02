from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.python import log
from tools import empty
from handle import Handle, ProtocolTaskMixin, IntervalMixin
import sys
import json
import struct

__version__ = 0

log.startLogging(sys.stdout)


class HubClient(Protocol, ProtocolTaskMixin):
    def __init__(self):
        self._buffer = bytes()
        self._hub = empty
        self._handle = Handle()

    def connectionMade(self):
        print(f"连接到服务器: {self.transport.getPeer()}")
        self._buffer = bytes()
        self.send_verify()

    def dataReceived(self, data):
        print(f"接收数据: {data}")

    def send(self, command_id, content):
        length = 12 + len(content)
        header = [length, __version__, command_id]
        header_pack = struct.pack("!3I", *header)
        self.transport.write(header_pack + content.encode("UTF-8"))

    def send_heartbeat(self):
        header = [12, __version__, 5]
        content = struct.pack("!3I", *header)
        self.transport.write(content)

    def report_status(self):
        if self._hub is not empty:
            body = self._handle.report_status(self._hub)
            content = self._serializer_data(body)
            print(f"上报电能数据: {content}")
            self.send(2, content)

    def report_weather_data(self):
        if self._hub is not empty:
            body = self._handle.report_weather_data()
            content = self._serializer_data(body)
            print(f"上报气象站数据: {content}")
            self.send(2, content)

    def send_verify(self):
        is_empty = self.factory.queue.empty()
        if not is_empty:
            self._hub = self.factory.queue.get()
            body = self._handle.register(self._hub)
            content = self._serializer_data(body)
            print(f"注册: {content}")
            self.send(1, content)

    def _serializer_data(self, body):
        content = {
            "sender": self._hub.hid,
            "receiver": "NS",
            "body": body
        }
        return json.dumps(content)


class HubFactory(ReconnectingClientFactory, IntervalMixin):
    protocol = HubClient

    def __init__(self, queue):
        self.p = self.protocol()
        self.p.factory = self
        self.queue = queue

    def startedConnecting(self, connector):
        print(f"开始连接服务器")

    def buildProtocol(self, addr):
        return self.p

    def clientConnectionFailed(self, connector, reason):
        print("服务器连接错误, 正在重连")
        self.retry(connector)

    def clientConnectionLost(self, connector, unused_reason):
        self.retry(connector)
