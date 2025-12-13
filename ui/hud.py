from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3, Vec4

class TargetListUI:
    def __init__(self, game):
        self.game = game
        self.items = {} # {ship_id: (button, label)}
        
        # --- STÍLUS DEFINÍCIÓK (Sci-Fi / EVE Theme) ---
        self.theme = {
            'bg_color': (0.05, 0.08, 0.1, 0.9),      # Sötét grafit/kék háttér
            'btn_normal': (0.1, 0.15, 0.2, 0.8),     # Gomb alapállapot
            'btn_hover': (0.0, 0.6, 0.8, 0.4),       # Gomb rámutatás (Neon cián áttetsző)
            'btn_click': (0.0, 0.8, 1.0, 0.6),       # Gomb kattintás
            'text_main': (0.8, 0.9, 1.0, 1),         # Fehér/kékes szöveg
            'text_accent': (0.0, 0.9, 1.0, 1),       # Neon cián szöveg
            'border_width': (0.002, 0.002),          # Vékony, finom keret
            'border_color': (0.3, 0.5, 0.6, 0.5),    # Halvány keret szín
            'font_scale': 0.04
        }
        
        # --- NEOCOM (Bal felső menü) ---
        self.neocom_frame = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(0, 0.5, -1, 0),
            pos=(-1.7, 0, 0.9) # Bal felső sarok (aspect2d)
        )

        # Inventory Gomb - Modern Sci-Fi Orb stílus
        self.btn_inventory = DirectButton(
            text="I", 
            text_scale=0.1,
            text_fg=self.theme['text_accent'],
            scale=0.18, 
            pos=(0.18, 0, 0),
            parent=self.neocom_frame,
            frameColor=self.theme['btn_normal'],
            relief=DGG.FLAT, # Letisztult, lapos dizájn
            borderWidth=self.theme['border_width'],
            frameSize=(-0.5, 0.5, -0.5, 0.5), # Négyzetesebb/Techno alak
            command=self.game.window_manager.toggle_inventory,
        )

        # Tooltip (Előbb hozzuk létre, mint ahogy bindoljuk!)
        self.lbl_inv_tooltip = DirectLabel(
            parent=self.btn_inventory, 
            text="INVENTORY [I]", 
            text_scale=0.25, 
            text_font=loader.loadFont("cmtt12"), # Írógép/Tech font ha van (default fallback)
            pos=(0.8, 0, -0.1), # Jobbra a gombtól
            text_fg=self.theme['text_main'],
            frameColor=self.theme['bg_color'],
            frameSize=(-0.1, 1.5, -0.3, 0.4),
            relief=DGG.FLAT
        )
        self.lbl_inv_tooltip.hide()

        # Hover effekt hozzáadása (színváltás) - Most már létezik a lbl_inv_tooltip
        self.btn_inventory.bind(DGG.ENTER, self.on_hover_enter, [self.btn_inventory, self.lbl_inv_tooltip])
        self.btn_inventory.bind(DGG.EXIT, self.on_hover_exit, [self.btn_inventory, self.lbl_inv_tooltip])


        # Market Gomb - Modern Sci-Fi Orb stílus
        self.btn_market = DirectButton(
            text="M", 
            text_scale=0.1,
            text_fg=(1, 0.8, 0.2, 1), # Arany/Borostyán akcentus a piachoz
            scale=0.18, 
            pos=(0.18, 0, -0.4),
            parent=self.neocom_frame,
            frameColor=self.theme['btn_normal'],
            relief=DGG.FLAT,
            borderWidth=self.theme['border_width'],
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            command=self.game.window_manager.toggle_market,
        )

        # Tooltip (Előbb létrehozva)
        self.lbl_market_tooltip = DirectLabel(
            parent=self.btn_market, 
            text="MARKET [M]", 
            text_scale=0.25, 
            pos=(0.8, 0, -0.1), 
            text_fg=self.theme['text_main'], 
            frameColor=self.theme['bg_color'],
            frameSize=(-0.1, 1.5, -0.3, 0.4),
            relief=DGG.FLAT
        )
        self.lbl_market_tooltip.hide()

        # Hover effekt hozzáadása
        self.btn_market.bind(DGG.ENTER, self.on_hover_enter, [self.btn_market, self.lbl_market_tooltip])
        self.btn_market.bind(DGG.EXIT, self.on_hover_exit, [self.btn_market, self.lbl_market_tooltip])

        # --- EREDETI TARGET LIST ---
        # Fő konténer (Jobb oldalt) - Áttetszőbb, high-tech panel
        self.frame = DirectFrame(
            frameColor=self.theme['bg_color'],
            frameSize=(-0.4, 0.4, -0.6, 0.6),
            pos=(1.3, 0, 0),
            relief=DGG.FLAT,
            borderWidth=self.theme['border_width'],
        )
        
        self.title = DirectLabel(
            text="TARGETS",
            scale=0.06,
            pos=(0, 0, 0.52),
            parent=self.frame,
            text_fg=self.theme['text_accent'],
            frameColor=(0,0,0,0),
            text_font=loader.loadFont("cmtt12") # Tech stílusú betűtípus
        )

        # Műveleti menü (Context Menu) - Sötét üveg hatás
        self.context_menu = DirectFrame(
            frameColor=(0.05, 0.05, 0.05, 0.98),
            frameSize=(-0.3, 0.3, -0.35, 0.35),
            pos=(0, 0, 0),
            parent=aspect2d,
            relief=DGG.RIDGE,
            borderWidth=(0.005, 0.005),
            # borderColor paraméter eltávolítva, mivel a DirectFrame nem támogatja közvetlenül
        )
        self.context_menu.hide()
        
        # --- MENÜ GOMBOK ---
        # Közös stílus a menü gomboknak
        btn_props = {
            'scale': 0.05, 
            'frameSize': (-5, 5, -0.8, 0.8), 
            'parent': self.context_menu,
            'relief': DGG.FLAT,
            'frameColor': (0.2, 0.2, 0.2, 0.0), # Átlátszó háttér alapból
            # 'text_fg': self.theme['text_main'], # ELTÁVOLÍTVA: Egyedi gomboknál adjuk meg
            'text_align': TextNode.ACenter,
            'borderWidth': (0,0)
        }

        self.btn_lock = DirectButton(
            text="LOCK TARGET", pos=(0, 0, 0.2),
            command=self.on_context_action, extraArgs=["lock"],
            text_fg=self.theme['text_accent'], # Kiemelt szín
            **btn_props
        )
        self.btn_follow = DirectButton(
            text="APPROACH", pos=(0, 0, 0.05),
            command=self.on_context_action, extraArgs=["follow"],
            text_fg=self.theme['text_main'],
            **btn_props
        )
        self.btn_orbit = DirectButton(
            text="ORBIT", pos=(0, 0, -0.1),
            command=self.on_context_action, extraArgs=["orbit"],
            text_fg=self.theme['text_main'],
            **btn_props
        )
        self.btn_cancel = DirectButton(
            text="CANCEL", pos=(0, 0, -0.25),
            command=self.hide_context_menu,
            text_fg=(1, 0.3, 0.3, 1), # Pirosas a Mégse gombnak
            **btn_props
        )
        
        self.selected_target_id = None
        self.active_context_target = None

        # Alapból elrejtjük a HUD-ot
        self.hide()

    # --- Hover effektek a modern UI-hoz ---
    def on_hover_enter(self, btn, tooltip, event):
        btn['frameColor'] = self.theme['btn_hover']
        if tooltip: tooltip.show()

    def on_hover_exit(self, btn, tooltip, event):
        btn['frameColor'] = self.theme['btn_normal']
        if tooltip: tooltip.hide()

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
            
            # Formázott szöveg: Típus (kicsi) | Név (Nagy) | Távolság
            text_str = f"{ship.ship_type.upper()}\n{ship.name}\n{dist:.0f} M"
            
            if ship_id in self.items:
                btn = self.items[ship_id]
                btn['text'] = text_str
                # Highlight ha kijelölt
                if self.selected_target_id == ship_id:
                    btn['frameColor'] = (0.0, 0.4, 0.6, 0.8) # Aktív kék
                    btn['borderWidth'] = (0.05, 0.05)
                else:
                    btn['frameColor'] = (0.1, 0.12, 0.15, 0.8) # Passzív sötét
                    btn['borderWidth'] = (0, 0)
            else:
                # Új sor létrehozása - Listaelem stílus
                btn = DirectButton(
                    text=text_str,
                    scale=0.035,
                    pos=(0, 0, y_pos),
                    parent=self.frame,
                    frameSize=(-10, 10, -1.8, 1.8),
                    frameColor=(0.1, 0.12, 0.15, 0.8),
                    relief=DGG.FLAT,
                    text_align=TextNode.ACenter,
                    text_fg=self.theme['text_main'],
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
                self.select_target(self.active_context_target)
            else:
                self.select_target(self.active_context_target)
                self.game.set_autopilot(self.active_context_target, action)
        
        self.hide_context_menu()