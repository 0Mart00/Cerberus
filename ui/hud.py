from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3

class TargetListUI:
    def __init__(self, game):
        self.game = game
        self.items = {} # {ship_id: (button, label)}
        
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-0.4, 0.4, -0.6, 0.6),
            pos=(1.3, 0, 0)
        )
        
        self.title = DirectLabel(
            text="CÉLPONTOK",
            scale=0.05,
            pos=(0, 0, 0.5),
            parent=self.frame,
            text_fg=(1, 1, 1, 1),
            frameColor=(0,0,0,0)
        )

        self.context_menu = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.9),
            frameSize=(-0.2, 0.2, -0.2, 0.2),
            pos=(0, 0, 0),
            parent=aspect2d
        )
        self.context_menu.hide()
        
        self.btn_follow = DirectButton(
            text="Követés", scale=0.04, pos=(0, 0, 0.05),
            command=self.on_context_action, extraArgs=["follow"],
            parent=self.context_menu
        )
        self.btn_orbit = DirectButton(
            text="Keringés", scale=0.04, pos=(0, 0, -0.05),
            command=self.on_context_action, extraArgs=["orbit"],
            parent=self.context_menu
        )
        
        self.selected_target_id = None
        self.active_context_target = None
        self.hide()

    def show(self):
        self.frame.show()

    def hide(self):
        self.frame.hide()
        self.context_menu.hide()

    def update_list(self, local_ship, remote_ships):
        if self.frame.isHidden(): return
        if not local_ship: return

        my_pos = local_ship.get_pos()
        y_pos = 0.4
        active_ids = []
        
        for ship_id, ship in remote_ships.items():
            active_ids.append(ship_id)
            dist = (ship.get_pos() - my_pos).length()
            text_str = f"{ship.ship_type} | {ship.name}\n{dist:.1f}m"
            
            if ship_id in self.items:
                btn = self.items[ship_id]
                btn['text'] = text_str
                if self.selected_target_id == ship_id:
                    btn['frameColor'] = (0.5, 0.5, 0, 1) # Highlight
                else:
                    btn['frameColor'] = (0.3, 0.3, 0.3, 1)
            else:
                btn = DirectButton(
                    text=text_str, scale=0.04, pos=(0, 0, y_pos),
                    parent=self.frame, frameSize=(-8, 8, -1.5, 1.5),
                    command=self.select_target, extraArgs=[ship_id]
                )
                btn.bind(DGG.B3CLICK, self.open_context_menu, [ship_id])
                self.items[ship_id] = btn
                y_pos -= 0.15

        for existing_id in list(self.items.keys()):
            if existing_id not in active_ids:
                self.items[existing_id].destroy()
                del self.items[existing_id]

    def select_target(self, ship_id):
        self.selected_target_id = ship_id
        # HÍVJUK A GAME LOGIKÁT: Ez állítja be a hajó célpontját (Lock)
        self.game.select_target(ship_id) 

    def open_context_menu(self, ship_id, event):
        self.active_context_target = ship_id
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.context_menu.setPos(mpos.x, 0, mpos.y)
            self.context_menu.show()

    def on_context_action(self, action):
        if self.active_context_target is not None:
            self.game.set_autopilot(self.active_context_target, action)
            # Autopilot parancsnál automatikusan ki is jelöljük
            self.select_target(self.active_context_target)
        self.context_menu.hide()