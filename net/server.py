from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, ConnectionWriter, QueuedConnectionReader, PointerToConnection, NetAddress, NetDatagram
from direct.task import Task
from direct.distributed.PyDatagram import PyDatagram
import json
import sys
import os
from pathlib import Path

# Path fix az importokhoz
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from globals import PORT

class GameServer:
    def __init__(self, manager=None):
        self.manager = manager
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0) # Ez olvassa az adatokat
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.clients = []
        self.active = False

    def start(self):
        self.tcpSocket = self.cManager.openTCPServerRendezvous(PORT, 1000)
        if self.tcpSocket:
            self.cListener.addConnection(self.tcpSocket)
            self.active = True
            # Két task kell: egyik az új kapcsolatoknak, másik az adatoknak
            taskMgr.add(self.listen_task, "ServerListenTask")
            taskMgr.add(self.data_reader_task, "ServerDataReaderTask")
            print(f"[SERVER] Szerver elindítva a {PORT}-es porton.")
            return True
        return False

    def listen_task(self, task):
        """Új kliensek figyelése"""
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
            
            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.clients.append(newConnection)
                self.cReader.addConnection(newConnection) # Hozzáadjuk a readerhez!
                print(f"[SERVER] Új kliens csatlakozott: {netAddress.getIpString()}")
        return Task.cont

    def data_reader_task(self, task):
        """Beérkező adatok olvasása és továbbítása (Broadcast/Relay)"""
        while self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                # A szerver itt csak egy "Postás": amit kap, továbbküldi mindenkinek
                # Kivéve annak, akitől kapta (exclude_conn)
                self.broadcast(datagram, exclude_conn=datagram.getConnection())
        return Task.cont

    def broadcast(self, datagram, exclude_conn=None):
        """Adat küldése minden kliensnek"""
        for client in self.clients:
            if client != exclude_conn:
                self.cWriter.send(datagram, client, True)

# Ez a rész csak akkor fut le, ha közvetlenül indítod a fájlt
if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase
    base = ShowBase()
    server = GameServer()
    server.start()
    base.run()