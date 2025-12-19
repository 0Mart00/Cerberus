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

    def send_ship_setup(self, ship_id, core_obj, support_obj, system_obj):
        """Elküldi a teljes felszerelést a szervernek"""
        # 1. Core küldése
        dg = PyDatagram()
        dg.addUint8(MSG_SYNC_CORE)
        dg.addUint16(ship_id)
        core_obj.pack(dg)
        self.send(dg)

        # 2. Support küldése
        dg = PyDatagram()
        dg.addUint8(MSG_SYNC_SUPPORT)
        dg.addUint16(ship_id)
        support_obj.pack(dg)
        self.send(dg)

    def process_msg(self, datagram):
        iterator = PyDatagramIterator(datagram)
        msg_type = iterator.getUint8()

        if msg_type == MSG_SYNC_CORE:
            target_ship_id = iterator.getUint16()
            received_core = Core.unpack(iterator)
            print(f"Szerver küldte: {target_ship_id} hajó új Core-t kapott: {received_core.name}")
            self.game.update_remote_equipment(target_ship_id, "core", received_core)
            
            # Host/Relay logika
            if self.game.server and self.game.server.active:
                self.game.server.broadcast(datagram, exclude_conn=datagram.getConnection())