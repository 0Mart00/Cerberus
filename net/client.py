from panda3d.core import QueuedConnectionManager, QueuedConnectionReader, ConnectionWriter, NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.task import Task
from .protocol import PORT, MSG_POSITION

class GameClient:
    def __init__(self, game_core):
        self.game = game_core
        self.cManager = QueuedConnectionManager()
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.connection = None

    def connect(self, ip):
        self.connection = self.cManager.openTCPClientConnection(ip, PORT, 3000)
        if self.connection:
            self.cReader.addConnection(self.connection)
            taskMgr.add(self.network_task, "ClientNetworkTask")
            print(f"[CLIENT] Sikeres csatlakozás: {ip}")
            return True
        return False

    def send(self, datagram):
        if self.connection:
            self.cWriter.send(datagram, self.connection, True)

    def network_task(self, task):
        while self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                self.process_msg(datagram)
        return Task.cont

    def process_msg(self, datagram):
        iterator = PyDatagramIterator(datagram)
        msg_type = iterator.getUint8()

        if msg_type == MSG_POSITION:
            sender_id = iterator.getUint16()
            x = iterator.getFloat64()
            y = iterator.getFloat64()
            z = iterator.getFloat64()
            
            # Kliens oldali logika: frissítjük a távoli hajót
            self.game.update_remote_ship(sender_id, x, y, z)

            # Ha mi vagyunk a Host, továbbítanunk kell (Relay)
            if self.game.server and self.game.server.active:
                # A Datagram már tartalmazza a nyers adatot, továbbküldjük
                self.game.server.broadcast(datagram, exclude_conn=datagram.getConnection())