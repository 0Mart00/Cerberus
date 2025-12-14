from direct.distributed.PyDatagram import PyDatagram
from globals import PORT, MAX_RENDER_DISTANCE # Importálva a globális fájlból

# Hálózati konstansok
# PORT = 9099 <- Eltávolítva/Globálisban definiálva
# MAX_LATHATOSAG = 5000.0 <- Eltávolítva/Globálisban definiálva <- Elavult, a MAX_RENDER_DISTANCE váltotta fel

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