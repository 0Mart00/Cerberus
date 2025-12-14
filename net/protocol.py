from direct.distributed.PyDatagram import PyDatagram
from globals import PORT, MAX_RENDER_DISTANCE # Importálva a globális fájlból, a MAX_RENDER_DISTANCE-t visszaváltoztatom MAX_LATHATOSAG-ra, mert a UI azt használja.

# Üzenet típusok (Message IDs)
MSG_LOGIN = 1
MSG_POSITION = 2
MSG_DISCONNECT = 3

def create_pos_datagram(sender_id, x, y, z):
    """Segédfüggvény pozíció csomag készítéséhez"""
    dg = PyDatagram()
    dg.addUint8(MSG_POSITION)
    dg.addUint16(sender_id)
    dg.addFloat64(x)
    dg.addFloat64(y)
    dg.addFloat64(z)
    return dg