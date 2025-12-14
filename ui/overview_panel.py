from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3, Vec4, NodePath

class OverviewPanel:
    def __init__(self, game, overview_manager=None): # Hozzáadva az overview_manager argumentum
        self.game = game
        self.overview_manager = overview_manager # Eltároljuk, ha szükséges
        self.items = {} # Entitás ID -> OverviewRow
        
        # --- STÍLUS DEFINÍCIÓK ---
        self.theme = {
            'bg_color': (0.05, 0.05, 0.08, 0.9),      # Sötét háttér
            'border_color': (0.3, 0.5, 0.6, 0.5),    # Halvány keret szín
        }
        
        # --- Fő panel konténer ---
        self.main_frame = DirectFrame(
            frameColor=self.theme['bg_color'],
            frameSize=(-0.7, 0.7, -0.65, 0.8),
            pos=(-0.8, 0, 0), # Bal középen (aspect2d)
            relief=DGG.FLAT,
            borderWidth=(0.002, 0.002),
            state=DGG.NORMAL,
            text="Overview",
            text_pos=(0, 0.75),
            text_scale=0.07,
            text_fg=(0.0, 0.8, 1.0, 1),
        )

        # Fül konténer (ahol az aktív fül neve látszik)
        self.tab_container = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.1, 0.1, 0.15, 1),
            frameSize=(-0.7, 0.7, 0.65, 0.75),
            pos=(0, 0, 0),
            relief=DGG.FLAT
        )

        self.lbl_active_tab = DirectLabel(
            parent=self.tab_container,
            text="Default Tab (All Entities)",
            text_scale=0.05,
            pos=(0, 0, -0.05),
            text_fg=(0.8, 0.9, 1.0, 1),
            frameColor=(0,0,0,0)
        )
        
        # --- GÖRGETHETŐ TÁBLÁZAT (Scroll Frame) ---
        self.scroll_frame = DirectScrolledFrame(
            parent=self.main_frame,
            canvasSize=(-0.68, 0.68, -2, 0), # Nagyobb canvas a tartalomhoz
            frameSize=(-0.68, 0.68, -0.6, 0.63), # Látható keret mérete (fejléc alatt)
            pos=(0, 0, 0),
            frameColor=(0.1, 0.1, 0.15, 0.5),
            relief=DGG.FLAT,
            borderWidth=(0, 0),
            verticalScroll_frameSize=(0, 0.03, -0.6, 0.63),
            horizontalScroll_frameSize=(-0.68, 0.68, 0, 0.03),
            manageScrollBars=True,
            autoHideScrollBars=True,
            state=DGG.NORMAL 
        )
        self.canvas = self.scroll_frame.getCanvas() # Rövidebb hivatkozás
        
        # Scrollbar STYLING (Sci-Fi Look) - Látható sávok
        scroll_color = (0.2, 0.25, 0.3, 1)  # Sötét sáv szín
        thumb_color = (0.0, 0.6, 0.8, 1)    # Neon szín a húzókához

        # Függőleges sáv
        self.scroll_frame.verticalScroll['frameColor'] = scroll_color 
        self.scroll_frame.verticalScroll.incButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.scroll_frame.verticalScroll.decButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.scroll_frame.verticalScroll.thumb['frameColor'] = thumb_color
        
        # Vízszintes sáv
        self.scroll_frame.horizontalScroll['frameColor'] = scroll_color
        self.scroll_frame.horizontalScroll.incButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.scroll_frame.horizontalScroll.decButton['frameColor'] = (0.1, 0.1, 0.1, 1)
        self.scroll_frame.horizontalScroll.thumb['frameColor'] = thumb_color

        # Mouse Wheel Görgetés Engedélyezése
        self.scroll_frame.bind(DGG.ENTER, self._scroll_frame_enter)
        self.scroll_frame.bind(DGG.EXIT, self._scroll_frame_exit)
        self.is_mouse_over_scroll_frame = False

        # --- TÁBLÁZAT FEJLÉC ---
        self.create_header()

        # --- TESZT GOMB ELTÁVOLÍTVA ---
        # A hatalmas, barna gomb (create_default_group_button) eltávolítva a felhasználói kérésnek megfelelően.
        
        self.hide() # Alapból elrejtjük

    def create_header(self):
        """Létrehozza a táblázat fejlécét az OverviewPanel tetején."""
        
        header = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.15, 0.15, 0.2, 1),
            frameSize=(-0.68, 0.68, 0.55, 0.65),
            pos=(0, 0, 0),
            relief=DGG.FLAT
        )
        
        header_scale = 0.035
        header_fg = (0.6, 0.8, 1.0, 1) # Világoskék
        
        # Oszlopfejlécek
        DirectLabel(parent=header, text="Icon", scale=header_scale, pos=(-0.6, 0, 0.05), frameColor=(0,0,0,0), text_fg=header_fg)
        DirectLabel(parent=header, text="Name", scale=header_scale, pos=(-0.35, 0, 0.05), frameColor=(0,0,0,0), text_fg=header_fg)
        DirectLabel(parent=header, text="Type", scale=header_scale, pos=(0.0, 0, 0.05), frameColor=(0,0,0,0), text_fg=header_fg)
        DirectLabel(parent=header, text="Distance", scale=header_scale, pos=(0.3, 0, 0.05), frameColor=(0,0,0,0), text_fg=header_fg)
        DirectLabel(parent=header, text="HP %", scale=header_scale, pos=(0.6, 0, 0.05), frameColor=(0,0,0,0), text_fg=header_fg)

        # Húzható sáv (Drag bar)
        drag_bar = DirectFrame(
            parent=header,
            frameColor=(0.1, 0.1, 0.1, 0.0), # Láthatatlan a húzáshoz
            frameSize=(-0.68, 0.68, 0, 0.1),
            pos=(0, 0, 0),
            state=DGG.NORMAL
        )
        # BINDELÉS: Ezt a részt mozgathatjuk
        drag_bar.bind(DGG.B1PRESS, self.start_drag)
        drag_bar.bind(DGG.B1RELEASE, self.end_drag)

    # --- Görgetés fókusz kezelése ---
    def _scroll_frame_enter(self, event):
        self.is_mouse_over_scroll_frame = True
        if self.game.local_ship:
            self.game.local_ship.ignore("wheel_up")
            self.game.local_ship.ignore("wheel_down")
        
        self.game.accept("wheel_up", self.scroll_up)
        self.game.accept("wheel_down", self.scroll_down)

    def _scroll_frame_exit(self, event):
        self.is_mouse_over_scroll_frame = False
        
        self.game.ignore("wheel_up")
        self.game.ignore("wheel_down")

        if self.game.local_ship:
            self.game.local_ship.accept("wheel_up", self.game.local_ship.adjust_zoom, [-5.0])
            self.game.local_ship.accept("wheel_down", self.game.local_ship.adjust_zoom, [5.0])

    def scroll_up(self):
        if 'verticalScroll' in self.scroll_frame:
            current_value = self.scroll_frame['verticalScroll']['value']
            new_value = max(0.0, current_value - 0.10)
            self.scroll_frame['verticalScroll']['value'] = new_value

    def scroll_down(self):
        if 'verticalScroll' in self.scroll_frame:
            current_value = self.scroll_frame['verticalScroll']['value']
            new_value = min(1.0, current_value + 0.10)
            self.scroll_frame['verticalScroll']['value'] = new_value

    # --- Húzás logika (Drag Logic) ---
    def start_drag(self, event):
        self.dragging_ui = True
        m = base.mouseWatcherNode.getMouse()
        current_pos = self.main_frame.getPos(aspect2d)
        
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
            frame_size = self.main_frame['frameSize']
            frame_w = frame_size[1] - frame_size[0]
            frame_h = frame_size[3] - frame_size[2]
            
            new_x = max(new_x, -1.0 + frame_w / 2.0)
            new_x = min(new_x, 1.0 - frame_w / 2.0)
            new_z = max(new_z, -1.0 + frame_h / 2.0)
            new_z = min(new_z, 1.0 - frame_h / 2.0)

            self.main_frame.setPos(new_x, 0, new_z)
        return task.cont

    # --------------------------------------------------------------------------
    # FRISSÍTÉS ÉS MUTATÁS/REJTÉS
    # --------------------------------------------------------------------------
    def update_list(self, local_ship, remote_ships, overview_rows):
        """Frissíti a táblázat tartalmát a kapott OverviewRow objektumokkal."""
        if self.main_frame.isHidden():
            return
            
        # Töröljük a régi elemeket a canvasról
        for child in self.canvas.getChildren():
            child.removeNode()
        self.items = {}

        y_pos = 0.0 # Kezdő pozíció a canvas tetején
        row_height = 0.07

        # Tényleges tartalom hozzáadása
        for row_data in overview_rows:
            # Feltételezzük, hogy az OverviewRow osztály rendelkezik create_ui() metódussal
            row_ui = row_data.create_ui(self.canvas, y_pos)
            self.items[row_data.entity_id] = row_ui
            y_pos -= row_height

        # Canvas méretének beállítása
        canvas_height = max(0.65, abs(y_pos)) # Minimum magasság, hogy ne legyen túl kicsi a canvas
        self.scroll_frame['canvasSize'] = (-0.68, 0.68, -canvas_height, 0)
        self.scroll_frame.setCanvasSize()


    def show(self):
        self.main_frame.show()

    def hide(self):
        self.main_frame.hide()