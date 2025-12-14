from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3, Vec4
from globals import ENTITIES, LOCAL_SHIP, MAX_RENDER_DISTANCE # JAVÍTVA: MAX_LATHATOSAG -> MAX_RENDER_DISTANCE
from ui.overview_panel import OverviewPanel
# A Manager-nek a Panda3D Base objektumot kellene átadni, de most lokálisan importáljuk a kódstruktúra miatt
from data.overview_item import OverviewManager 

class HUD:
    """
    A Cerberus játék interfésze. Ide integráljuk az Overview Panelt.
    """
    def __init__(self, base):
        self.base = base
        
        # 1. Initialize the Overview Data Manager
        self.overview_manager = OverviewManager(num_entities=30) 
        
        # 2. Initialize the EVE-like Overview Panel
        self.overview_panel = OverviewPanel(base, self.overview_manager)

        # Hozzáadhatunk egy kapcsolót (például F11) a HUD elrejtésére/megjelenítésére
        self.base.accept('f11', self.toggle_visibility)
        
        # Kezdetben elrejti a HUD-ot, hogy a menü látható legyen
        self.hide()
        
    def toggle_visibility(self):
        """Toggles the visibility of the HUD elements."""
        if self.overview_panel.main_frame.isHidden():
            self.overview_panel.main_frame.show()
        else:
            self.overview_panel.main_frame.hide()

    def show(self):
        """Shows the HUD components."""
        self.overview_panel.main_frame.show()

    def hide(self):
        """Hides the HUD components."""
        self.overview_panel.main_frame.hide()

    def destroy(self):
        """Clean up all HUD elements."""
        self.overview_panel.destroy()
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
        
        # --- DRAGGING VÁLTOZÓK ---
        self.dragging_ui = False
        self.drag_start_pos = (0, 0)
        self.is_mouse_over_scroll_frame = False # FLAG: Ezt használjuk a húzás tiltásához
        
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

        # --- EREDETI TARGET LIST (SCROLL MENU) ---
        
        # 1. Külső konténer frame (tartja a címet és a scrollozható listát)
        self.outer_frame = DirectFrame(
            frameColor=self.theme['bg_color'],
            frameSize=(-0.4, 0.4, -0.6, 0.6),
            pos=(1.3, 0, 0),
            relief=DGG.FLAT,
            borderWidth=self.theme['border_width'],
            state=DGG.NORMAL 
        )

        # DRAGGING BEKÖTÉSE a külső frame-re
        self.outer_frame.bind(DGG.B1PRESS, self.start_drag)
        self.outer_frame.bind(DGG.B1RELEASE, self.end_drag)
        self.game.taskMgr.add(self.drag_update_task, "DragTargetUI")
        
        # Cím a külső frame tetején
        self.title = DirectLabel(
            text="TARGETS",
            scale=0.06,
            pos=(0, 0, 0.52),
            parent=self.outer_frame,
            text_fg=self.theme['text_accent'],
            frameColor=(0,0,0,0),
            text_font=loader.loadFont("cmtt12")
        )

        # 2. Scrollozható Target lista
        self.target_scroll_frame = DirectScrolledFrame(
            parent=self.outer_frame,
            canvasSize=(-0.38, 0.38, -2, 0), 
            frameSize=(-0.38, 0.38, -0.52, 0.45), 
            pos=(0, 0, -0.05),
            frameColor=(0.1, 0.12, 0.15, 0.5),
            relief=DGG.FLAT,
            borderWidth=(0, 0),
            
            # SCROLLBAR BEÁLLÍTÁSA (Funkcionális és látható, de Sci-Fi stílusú)
            verticalScroll_frameSize=(0, 0.03, -0.52, 0.45), 
            horizontalScroll_frameSize=(-0.38, 0.38, 0, 0.03), # Vízszintes sáv mérete
            manageScrollBars=True, 
            autoHideScrollBars=True,
            state=DGG.NORMAL 
        )

        # Scrollbar STYLING (Sci-Fi Look - Látható sávok)
        scroll_color = (0.2, 0.25, 0.3, 1)  # Sötét sáv szín
        thumb_color = (0.0, 0.6, 0.8, 1)    # Neon szín a húzókához

        # Függőleges sáv
        self.target_scroll_frame.verticalScroll['frameColor'] = scroll_color 
        self.target_scroll_frame.verticalScroll.incButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.target_scroll_frame.verticalScroll.decButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.target_scroll_frame.verticalScroll.thumb['frameColor'] = thumb_color
        
        # Vízszintes sáv
        self.target_scroll_frame.horizontalScroll['frameColor'] = scroll_color
        self.target_scroll_frame.horizontalScroll.incButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.target_scroll_frame.horizontalScroll.decButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.target_scroll_frame.horizontalScroll.thumb['frameColor'] = thumb_color
        
        # ÚJ: Mouse Over események a scroll frame-re a húzás blokkolásához
        self.target_scroll_frame.bind(DGG.ENTER, self._scroll_frame_enter)
        self.target_scroll_frame.bind(DGG.EXIT, self._scroll_frame_exit)
        
        # Redefine self.frame to be the canvas for easy access in update_list
        self.frame = self.target_scroll_frame.getCanvas()


        # Műveleti menü (Context Menu) - Sötét üveg hatás
        self.context_menu = DirectFrame(
            frameColor=(0.05, 0.05, 0.05, 0.98),
            # MEGNÖVELT KERET MÉRET
            frameSize=(-0.3, 0.3, -0.4, 0.4), 
            pos=(0, 0, 0),
            parent=aspect2d,
            relief=DGG.RIDGE,
            borderWidth=(0.005, 0.005),
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
            'text_align': TextNode.ACenter,
            'borderWidth': (0,0),
            'state': DGG.NORMAL # Fontos a kattinthatósághoz
        }

        # Növelt távolság: 0.25 -> 0.05 -> -0.15 -> -0.35 (0.2-es lépések)
        self.btn_lock = DirectButton(
            text="LOCK TARGET", pos=(0, 0, 0.3), # Magasabbra kezd
            command=self.on_context_action, extraArgs=["lock"],
            text_fg=self.theme['text_accent'], # Kiemelt szín
            **btn_props
        )
        self.btn_follow = DirectButton(
            text="APPROACH", pos=(0, 0, 0.1), # Távolság 0.2
            command=self.on_context_action, extraArgs=["follow"],
            text_fg=self.theme['text_main'],
            **btn_props
        )
        self.btn_orbit = DirectButton(
            text="ORBIT", pos=(0, 0, -0.1), # Távolság 0.2
            command=self.on_context_action, extraArgs=["orbit"],
            text_fg=self.theme['text_main'],
            **btn_props
        )
        self.btn_cancel = DirectButton(
            text="CANCEL", pos=(0, 0, -0.3), # Távolság 0.2
            command=self.hide_context_menu,
            text_fg=(1, 0.3, 0.3, 1), # Pirosas a Mégse gombnak
            **btn_props
        )
        
        self.selected_target_id = None
        self.active_context_target = None

        # Alapból elrejtjük a HUD-ot
        self.hide()

    # --- Scroll Frame Mouse Tracking ---
    def _scroll_frame_enter(self, event):
        self.is_mouse_over_scroll_frame = True
        
        # HAJÓ KAMERA ESEMÉNYEK LETILTÁSA
        if self.game.local_ship:
            self.game.local_ship.ignore("wheel_up")
            self.game.local_ship.ignore("wheel_down")
        
        # Görgetés fókuszálása az ablakra 
        self.game.accept("wheel_up", self.scroll_up)
        self.game.accept("wheel_down", self.scroll_down)

    def _scroll_frame_exit(self, event):
        self.is_mouse_over_scroll_frame = False
        
        # Görgetés események feloldása
        self.game.ignore("wheel_up")
        self.game.ignore("wheel_down")

        # HAJÓ KAMERA ESEMÉNYEK VISSZAÁLLÍTÁSA
        if self.game.local_ship:
            # Feltételezve, hogy a Ship.adjust_zoom létezik
            self.game.local_ship.accept("wheel_up", self.game.local_ship.adjust_zoom, [-5.0])
            self.game.local_ship.accept("wheel_down", self.game.local_ship.adjust_zoom, [5.0])


    def scroll_up(self):
        """Görgetés fel (csökkenti a függőleges görgetési értéket)."""
        if 'verticalScroll' in self.target_scroll_frame:
            current_value = self.target_scroll_frame['verticalScroll']['value']
            # Lépésméret: 10% a gyorsabb görgetéshez
            new_value = max(0.0, current_value - 0.10)
            self.target_scroll_frame['verticalScroll']['value'] = new_value

    def scroll_down(self):
        """Görgetés le (növeli a függőleges görgetési értéket)."""
        if 'verticalScroll' in self.target_scroll_frame:
            current_value = self.target_scroll_frame['verticalScroll']['value']
            # Lépésméret: 10% a gyorsabb görgetéshez
            new_value = min(1.0, current_value + 0.10)
            self.target_scroll_frame['verticalScroll']['value'] = new_value

    # --- DRAG LOGIKA ---
    def start_drag(self, event):
        # A húzást csak akkor engedélyezzük, ha az egér NEM a görgethető keret felett van.
        if self.is_mouse_over_scroll_frame:
            return

        self.dragging_ui = True
        m = base.mouseWatcherNode.getMouse()
        current_pos = self.outer_frame.getPos(aspect2d)
        
        # Különbség a kurzor és az ablak középpontja között
        self.drag_start_pos = (m.getX() - current_pos.getX(), m.getY() - current_pos.getZ())
        
    def end_drag(self, event):
        self.dragging_ui = False

    def drag_update_task(self, task):
        if self.dragging_ui and base.mouseWatcherNode.hasMouse():
            m = base.mouseWatcherNode.getMouse()
            
            new_x = m.getX() - self.drag_start_pos[0]
            new_z = m.getY() - self.drag_start_pos[1]
            
            # Határok ellenőrzése
            frame_size = self.outer_frame['frameSize'] 
            frame_w = frame_size[1] - frame_size[0]
            frame_h = frame_size[3] - frame_size[2]
            
            new_x = max(new_x, -1.0 + frame_w / 2.0)
            new_x = min(new_x, 1.0 - frame_w / 2.0)
            new_z = max(new_z, -1.0 + frame_h / 2.0)
            new_z = min(new_z, 1.0 - frame_h / 2.0)

            self.outer_frame.setPos(new_x, 0, new_z)
        return task.cont

    # --- Hover effektek a modern UI-hoz ---
    def on_hover_enter(self, btn, tooltip, event):
        btn['frameColor'] = self.theme['btn_hover']
        if tooltip: tooltip.show()

    def on_hover_exit(self, btn, tooltip, event):
        btn['frameColor'] = self.theme['btn_normal']
        if tooltip: tooltip.hide()

    def show(self):
        self.outer_frame.show() # Fő frame mutatása
        self.neocom_frame.show()

    def hide(self):
        self.outer_frame.hide() # Fő frame elrejtése
        self.neocom_frame.hide()
        self.hide_context_menu()

    def hide_context_menu(self):
        self.context_menu.hide()

    def update_list(self, local_ship, remote_ships): # Ezt a metódust frissíti a CerberusGame (a régi metódus hívása)
        """A Target listát frissíti azokkal a hajókkal, amelyek nincsenek az Overview-ban."""
        
        if self.outer_frame.isHidden():
            return

        if not local_ship:
            return

        # Töröljük a régi elemeket a canvasról és nullázzuk a referenciákat
        for child in self.frame.getChildren():
            child.removeNode()
        self.items = {}
            
        my_pos = local_ship.get_pos()
        y_pos = 0.0 # Kezdő pozíció a scroll frame canvas tetején (0)

        active_ids = []
        item_height = 0.1 # Kisebb magasság (0.15 helyett)
        btn_scale = 0.03 # Kisebb gombméret

        # Iteráció a globális entitásokon
        for ship_id, ship in ENTITIES.items():
            # Csak hajókat listázunk, és kihagyjuk a saját hajót
            if ship.entity_type != 'Ship' or ship.uid == local_ship.uid:
                continue

            active_ids.append(ship_id)
            dist = (ship.get_pos() - my_pos).length()
            
            # Formázott szöveg: Típus (kicsi) | Név (Nagy) | Távolság
            text_str = f"{ship.ship_type.upper()}\n{ship.name}\n{dist:.0f} M"
            
            # Új sor létrehozása - Listaelem stílus
            btn = DirectButton(
                text=text_str,
                scale=btn_scale, # Kisebb gombméret
                pos=(0, 0, y_pos),
                parent=self.frame, # Canvashoz csatolva
                frameSize=(-10, 10, -1.8, 1.8),
                frameColor=(0.1, 0.12, 0.15, 0.8),
                relief=DGG.FLAT,
                text_align=TextNode.ACenter,
                text_fg=self.theme['text_main'],
                command=self.open_target_menu,
                extraArgs=[ship_id],
                state=DGG.NORMAL # Explicit beállítás a kattinthatóság érdekében
            )
            self.items[ship_id] = btn
            
            # Highlight ha kijelölt
            if self.selected_target_id == ship_id:
                btn['frameColor'] = (0.0, 0.4, 0.6, 0.8) # Aktív kék
                btn['borderWidth'] = (0.05, 0.05)
            else:
                btn['frameColor'] = (0.1, 0.12, 0.15, 0.8) # Passzív sötét
                btn['borderWidth'] = (0, 0)
                
            y_pos -= item_height

        # Eltűnt hajók törlése (bár a fenti loop elején töröltük a node-okat)
        for existing_id in list(self.items.keys()):
            if existing_id not in active_ids:
                # Ezt a részt elvileg a fenti törlés már megoldja
                pass
        
        # Canvas méretének beállítása
        canvas_height = max(0.9, abs(y_pos)) # Minimum magasság, hogy ne tűnjön el a lista
        self.target_scroll_frame['canvasSize'] = (-0.38, 0.38, -canvas_height, 0)
        self.target_scroll_frame.setCanvasSize()

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