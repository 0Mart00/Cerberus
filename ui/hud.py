from direct.gui.DirectGui import DirectFrame, DirectWaitBar, OnscreenText
from panda3d.core import TextNode, Vec4

class HUD:
    def __init__(self, base):
        self.base = base
        
        # Main container for HUD elements
        self.container = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-1, 1, -1, 1),
            parent=self.base.aspect2d
        )
        
        # --- Player Stats (Bottom Left) ---
        self.stats_frame = DirectFrame(
            parent=self.container,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(0, 0.6, 0, 0.25),
            pos=(-1.3, 0, -0.95)
        )
        
        self.player_name = OnscreenText(
            text=f"PILÓTA: {self.base.my_id}",
            parent=self.stats_frame,
            scale=0.05,
            pos=(0.05, 0.18),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )

        # Shield Bar
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

        # Hull Bar
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

        # --- Target Info (Top Center) ---
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

        # Start update task
        self.base.taskMgr.add(self.update, "HUDUpdateTask")

    def update(self, task):
        if not self.base.local_ship:
            return task.cont

        # Update Player Bars
        ship = self.base.local_ship
        
        # Hull
        if hasattr(ship, 'current_hull') and hasattr(ship, 'max_hull'):
            self.hull_bar['range'] = ship.max_hull
            self.hull_bar['value'] = ship.current_hull
        
        # Shield
        if hasattr(ship, 'current_shield') and hasattr(ship, 'max_shield'):
            self.shield_bar['range'] = max(1, ship.max_shield) # Prevent div by zero
            self.shield_bar['value'] = ship.current_shield
            
        # Update Target Info
        target = getattr(ship, 'target', None)
        if target:
            self.target_frame.show()
            self.target_name.setText(target.name)
            
            dist = (target.get_pos() - ship.get_pos()).length()
            self.target_dist.setText(f"{dist:.1f} m")
        else:
            self.target_frame.hide()

        return task.cont

    def destroy(self):
        self.base.taskMgr.remove("HUDUpdateTask")
        self.container.destroy()