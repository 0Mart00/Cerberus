from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, ConnectionWriter, PointerToConnection, NetAddress
from direct.task import Task
from .protocol import PORT

class GameServer:
    def __init__(self, manager):
        self.manager = manager
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.clients = [] # Csatlakozott kliensek listája
        self.active = False

    def start(self):
        self.tcpSocket = self.cManager.openTCPServerRendezvous(PORT, 1000)
        if self.tcpSocket:
            self.cListener.addConnection(self.tcpSocket)
            self.active = True
            taskMgr.add(self.listen_task, "ServerListenTask")
            print(f"[SERVER] Szerver elindítva a {PORT}-es porton.")
            return True
        return False

    def listen_task(self, task):
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
            
            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.clients.append(newConnection)
                print(f"[SERVER] Új kliens csatlakozott: {netAddress.getIpString()}")
        return Task.cont

    def broadcast(self, datagram, exclude_conn=None):
        """Adat küldése minden kliensnek (kivéve a feladót)"""
        for client in self.clients:
            if client != exclude_conn:
                self.cWriter.send(datagram, client, True)