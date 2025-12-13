from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3

class TargetListUI:
    def __init__(self, game):
        self.game = game
        self.items = {} # {ship_id: (button, label)}
        
        # --- NEOCOM (Bal felső menü) ---
        self.neocom_frame = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(0, 0.5, -1, 0),
            pos=(-1.7, 0, 0.9) # Bal felső sarok (aspect2d)
        )

        # Inventory Gomb - MÉG NAGYOBB
        self.btn_inventory = DirectButton(
            text="I", text_scale=0.1, # Nagy betű
            scale=0.18, pos=(0.18, 0, 0), # Nagyobb méret (0.15 -> 0.18)
            parent=self.neocom_frame,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            command=self.game.window_manager.toggle_inventory,
            text_fg=(1, 1, 1, 1)
        )
        # Tooltip-szerű felirat (alapból rejtve)
        self.lbl_inv_tooltip = DirectLabel(
            parent=self.btn_inventory, 
            text="Inventory [I]", # Gomb neve + Gyorsgomb
            scale=0.2, pos=(0,0,-0.8), 
            text_fg=(1,1,1,1), frameColor=(0,0,0,0.8),
            text_bg=(0,0,0,1)
        )
        self.lbl_inv_tooltip.hide()
        # Események kötése (Hover)
        self.btn_inventory.bind(DGG.ENTER, self.show_tooltip, [self.lbl_inv_tooltip])
        self.btn_inventory.bind(DGG.EXIT, self.hide_tooltip, [self.lbl_inv_tooltip])


        # Market Gomb - MÉG NAGYOBB
        self.btn_market = DirectButton(
            text="M", text_scale=0.1,
            scale=0.18, pos=(0.18, 0, -0.4), # Nagyobb méret és térköz
            parent=self.neocom_frame,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            command=self.game.window_manager.toggle_market,
            text_fg=(1, 1, 0.8, 1)
        )
        self.lbl_market_tooltip = DirectLabel(
            parent=self.btn_market, 
            text="Market [M]", # Gomb neve + Gyorsgomb
            scale=0.2, pos=(0,0,-0.8), 
            text_fg=(1,1,1,1), frameColor=(0,0,0,0.8),
            text_bg=(0,0,0,1)
        )
        self.lbl_market_tooltip.hide()
        # Események kötése (Hover)
        self.btn_market.bind(DGG.ENTER, self.show_tooltip, [self.lbl_market_tooltip])
        self.btn_market.bind(DGG.EXIT, self.hide_tooltip, [self.lbl_market_tooltip])

        # --- EREDETI TARGET LIST ---
        # Fő konténer (Jobb oldalt)
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-0.4, 0.4, -0.6, 0.6),
            pos=(1.3, 0, 0) # Jobb szélre tolva
        )
        
        self.title = DirectLabel(
            text="CÉLPONTOK",
            scale=0.05,
            pos=(0, 0, 0.5),
            parent=self.frame,
            text_fg=(1, 1, 1, 1),
            frameColor=(0,0,0,0)
        )

        # Műveleti menü (alapból rejtve)
        self.context_menu = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.95),
            frameSize=(-0.3, 0.3, -0.35, 0.35),
            pos=(0, 0, 0),
            parent=aspect2d
        )
        self.context_menu.hide()
        
        # --- MENÜ GOMBOK ---
        btn_props = {'scale': 0.05, 'frameSize': (-5, 5, -0.8, 0.8), 'parent': self.context_menu}

        self.btn_lock = DirectButton(
            text="Célpont Kijelölése (Lock)", pos=(0, 0, 0.2),
            command=self.on_context_action, extraArgs=["lock"],
            **btn_props
        )
        self.btn_follow = DirectButton(
            text="Megközelítés (Follow)", pos=(0, 0, 0.05),
            command=self.on_context_action, extraArgs=["follow"],
            **btn_props
        )
        self.btn_orbit = DirectButton(
            text="Keringés (Orbit)", pos=(0, 0, -0.1),
            command=self.on_context_action, extraArgs=["orbit"],
            **btn_props
        )
        self.btn_cancel = DirectButton(
            text="Mégse", pos=(0, 0, -0.25),
            command=self.hide_context_menu,
            frameColor=(0.5, 0, 0, 1),
            **btn_props
        )
        
        self.selected_target_id = None
        self.active_context_target = None

        # Alapból elrejtjük a HUD-ot
        self.hide()

    def show_tooltip(self, tooltip, event):
        tooltip.show()

    def hide_tooltip(self, tooltip, event):
        tooltip.hide()

    def show(self):
        self.frame.show()
        self.neocom_frame.show()

    def hide(self):
        self.frame.hide()
        self.neocom_frame.hide()
        self.hide_context_menu()

    def hide_context_menu(self):
        self.context_menu.hide()

    def update_list(self, local_ship, remote_ships):
        if self.frame.isHidden():
            return

        if not local_ship:
            return

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
                # Highlight ha kijelölt
                if self.selected_target_id == ship_id:
                    btn['frameColor'] = (0.5, 0.5, 0, 1) # Arany/Sárgás
                else:
                    btn['frameColor'] = (0.3, 0.3, 0.3, 1) # Szürke
            else:
                # Új sor létrehozása
                btn = DirectButton(
                    text=text_str,
                    scale=0.04,
                    pos=(0, 0, y_pos),
                    parent=self.frame,
                    frameSize=(-8, 8, -1.5, 1.5),
                    # Bal klikkre most már menü nyílik
                    command=self.open_target_menu,
                    extraArgs=[ship_id]
                )
                self.items[ship_id] = btn
                y_pos -= 0.15

        # Eltűnt hajók törlése
        for existing_id in list(self.items.keys()):
            if existing_id not in active_ids:
                self.items[existing_id].destroy()
                del self.items[existing_id]

    def open_target_menu(self, ship_id):
        """Bal klikk a listaelemre: Menü megnyitása"""
        self.active_context_target = ship_id
        
        # Egér pozícióhoz igazítjuk a menüt
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.context_menu.setPos(mpos.x, 0, mpos.y)
        else:
            self.context_menu.setPos(0, 0, 0)
            
        self.context_menu.show()

    def select_target(self, ship_id):
        """Kijelölés (Lock) végrehajtása"""
        self.selected_target_id = ship_id
        self.game.select_target(ship_id) 

    def on_context_action(self, action):
        """Gombnyomás a menüben"""
        if self.active_context_target is not None:
            if action == "lock":
                # Csak kijelölés
                self.select_target(self.active_context_target)
            else:
                # Robotpilóta parancsok (Follow/Orbit)
                # Ezek automatikusan kijelölik a célpontot is
                self.select_target(self.active_context_target)
                self.game.set_autopilot(self.active_context_target, action)
        
        self.hide_context_menu()