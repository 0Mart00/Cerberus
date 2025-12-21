from direct.gui.DirectGui import DirectFrame, DirectWaitBar, OnscreenText
from panda3d.core import TextNode

class HUD:
    def __init__(self, base):
        self.base = base
        
        # Fő konténer az UI elemeknek
        self.container = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-1, 1, -1, 1),
            parent=self.base.aspect2d
        )
        
        # --- Játékos Statisztikák (Bal alul) ---
        self.stats_frame = DirectFrame(
            parent=self.container,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(0, 0.6, 0, 0.25),
            pos=(-1.3, 0, -0.95)
        )
        
        # Biztonságos ID lekérés (ha a base.my_id még nem létezne)
        player_id = getattr(self.base, 'my_id', "Ismeretlen")
        self.player_name = OnscreenText(
            text=f"PILÓTA: {player_id}",
            parent=self.stats_frame,
            scale=0.05,
            pos=(0.05, 0.18),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )

        # Pajzs csík
        self.shield_bar = DirectWaitBar(
            text="PAJZS",
            value=100,
            range=100,
            parent=self.stats_frame,
            pos=(0.3, 0, 0.12),
            scale=0.4,
            barColor=(0.2, 0.5, 1, 0.8),
            frameColor=(0.1, 0.1, 0.1, 1)
        )

        # Hajótest csík
        self.hull_bar = DirectWaitBar(
            text="HAJÓTEST",
            value=100,
            range=100,
            parent=self.stats_frame,
            pos=(0.3, 0, 0.05),
            scale=0.4,
            barColor=(0.8, 0.2, 0.2, 0.8),
            frameColor=(0.1, 0.1, 0.1, 1)
        )

        # --- Célpont infó (Fent középen) ---
        self.target_frame = DirectFrame(
            parent=self.container,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-0.3, 0.3, -0.1, 0.1),
            pos=(0, 0, 0.85)
        )
        self.target_frame.hide()

        self.target_name = OnscreenText(
            text="NINCS CÉLPONT",
            parent=self.target_frame,
            scale=0.05,
            pos=(0, 0.02),
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter
        )
        
        self.target_dist = OnscreenText(
            text="0 m",
            parent=self.target_frame,
            scale=0.04,
            pos=(0, -0.05),
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )

        # FONTOS: Nem adunk hozzá saját task-ot (taskMgr.add), 
        # mert a main.py update hívja meg kézzel!

    def update(self, dt):
        """
        Frissíti a HUD-ot. A dt a main.py-ból érkező delta time (float).
        """
        # Biztonságos ellenőrzés, hogy létezik-e a hajó
        ship = getattr(self.base, 'local_ship', None)
        
        if not ship or ship.isEmpty():
            return

        # Életerő és Pajzs frissítése (ha az objektumon vannak ilyen változók)
        if hasattr(ship, 'current_hull') and hasattr(ship, 'max_hull'):
            self.hull_bar['range'] = ship.max_hull
            self.hull_bar['value'] = ship.current_hull
        
        if hasattr(ship, 'current_shield') and hasattr(ship, 'max_shield'):
            self.shield_bar['range'] = max(1, ship.max_shield)
            self.shield_bar['value'] = ship.current_shield
            
        # Célpont infó frissítése
        target = getattr(ship, 'target', None)
        if target and not target.isEmpty():
            self.target_frame.show()
            # Ha van a célpontnak neve, azt írjuk ki, egyébként a NodePath nevét
            name = getattr(target, 'name', target.getName())
            self.target_name.setText(name)
            
            dist = (target.getPos(self.base.render) - ship.getPos(self.base.render)).length()
            self.target_dist.setText(f"{dist:.1f} m")
        else:
            self.target_frame.hide()

    def destroy(self):
        self.container.destroy()