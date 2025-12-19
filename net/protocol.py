from direct.distributed.PyDatagram import PyDatagram
from globals import PORT, MAX_RENDER_DISTANCE

# --- Üzenet típusok (Message IDs) ---
MSG_LOGIN = 1
MSG_POSITION = 2
MSG_DISCONNECT = 3

# ÚJ: Item szinkronizációs ID-k
MSG_SYNC_CORE = 10
MSG_SYNC_SUPPORT = 11
MSG_SYNC_SYSTEM = 12

def create_pos_datagram(sender_id, x, y, z):
    """Segédfüggvény pozíció csomag készítéséhez"""
    dg = PyDatagram()
    dg.addUint8(MSG_POSITION)
    dg.addUint16(sender_id)
    dg.addFloat64(x)
    dg.addFloat64(y)
    dg.addFloat64(z)
    return dg

def create_sync_dg(msg_type, sender_id, item_obj):
    """
    Univerzális segédfüggvény itemek küldéséhez.
    A korábban megírt pack() metódust használja.
    """
    dg = PyDatagram()
    dg.addUint8(msg_type)
    dg.addUint16(sender_id)
    item_obj.pack(dg)
    return dg