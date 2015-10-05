
import json

from Qt import QtCore, QtWebSockets

class WebSocketServer(QtWebSockets.QWebSocketServer):

    messageReceived = QtCore.pyqtSignal(dict)

    def __init__(self, name,  parent):
        super().__init__( name, QtWebSockets.QWebSocketServer.NonSecureMode, parent)

        self.clients = []

        self.newConnection.connect(self.onNewConnection)



    def onNewConnection(self):

        sock = self.nextPendingConnection()
        sock.sendTextMessage("Hello")
        #print("onNewCOnn", sock)
        self.clients.append(sock)

        sock.textMessageReceived.connect(self.onMessageReceived)


    def sendMessage(self, xx):

        if isinstance(xx, str):
            xx = dict(message=xx)
        encoded = json.dumps(xx)
        for sock in self.clients:
            sock.sendTextMessage(encoded)

    @QtCore.pyqtSlot(QtCore.QTime)
    def sendTime(self, t):
        self.sendMessage( {"type": "time", "time": t.toString("hh:mm:ss")} )

    def onMessageReceived(self, s):
        #print("onMess", s)
        cmd = json.loads(s)

        self.messageReceived.emit(cmd)
