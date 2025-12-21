import time
from direct.showbase.DirectObject import DirectObject

class GameStats(DirectObject):
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.last_activity = time.time()
        self.idle_threshold = 30.0 # 30 másodperc inaktivitás után számoljuk az idle-t
        
        self.is_idle = False
        self.accumulated_idle_time = 0.0
        
        # Bármilyen gombnyomás reseteli az időzítőt
        base.buttonThrowers[0].node().setButtonDownEvent('input-event')
        self.accept('input-event', self.reset_idle)

    def reset_idle(self, key=None):
        now = time.time()
        if self.is_idle:
            idle_duration = now - self.last_activity
            # Hozzáadjuk a tiszta idle időt (a threshold feletti részt)
            self.accumulated_idle_time += (idle_duration - self.idle_threshold)
            self.is_idle = False
            print(f"[Stats] Aktív állapot. Inaktív idő volt: {int(idle_duration)}s")
        self.last_activity = now

    def update(self):
        now = time.time()
        if not self.is_idle and (now - self.last_activity) > self.idle_threshold:
            self.is_idle = True
            print("[Stats] Inaktív állapot (Idle).")

    def get_active_playtime(self):
        """Visszaadja a tényleges játékidőt (Összes - Idle)."""
        total = time.time() - self.start_time
        current_idle = 0
        if self.is_idle:
            current_idle = (time.time() - self.last_activity) - self.idle_threshold
        return total - (self.accumulated_idle_time + current_idle)