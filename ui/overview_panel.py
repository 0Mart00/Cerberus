from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectScrolledFrame, DirectButton, DGG
from panda3d.core import TextNode, Vec3, Vec4
import random

class OverviewPanel:
    """
    EGYEDÜLÁLLÓ, BIZTONSÁGOS OVERVIEW PANEL, amely TextNode igazításokat használ.
    Ezt az osztályt a HUD példányosítja.
    """
    def __init__(self, base):
        self.base = base
        
        # UI Skálázási konstansok (Könnyű skálázhatóság)
        self.PANEL_WIDTH = 1.2
        self.PANEL_HEIGHT = 1.5
        self.ITEM_HEIGHT = 0.08
        self.FONT_SIZE = 0.045
        
        # Színek (R, G, B, A)
        self.COLOR_BG = (0.1, 0.1, 0.2, 0.9)
        self.COLOR_HEADER = (0.2, 0.2, 0.3, 1)
        self.COLOR_ITEM_ODD = (0.15, 0.15, 0.2, 1)
        self.COLOR_ITEM_EVEN = (0.12, 0.12, 0.15, 1)
        self.COLOR_TEXT = (1, 1, 1, 1)

        # Állapotkövetés: Figyeli, hogy az egér a panel felett van-e
        self.is_mouse_over_ui = False 

        # 1. Fő konténer (Main Container)
        self.main_frame = DirectFrame(
            parent=self.base.aspect2d,
            frameColor=self.COLOR_BG,
            frameSize=(-self.PANEL_WIDTH/2, self.PANEL_WIDTH/2, -self.PANEL_HEIGHT/2, self.PANEL_HEIGHT/2),
            pos=(-1.0 + self.PANEL_WIDTH/2, 0, 0), 
            state=DGG.NORMAL
        )

        # 2. Cím (Overview Title)
        self.title = DirectLabel(
            parent=self.main_frame,
            text="ÁTTEKINTÉS (OVERVIEW)",
            scale=0.07,
            pos=(0, 0, self.PANEL_HEIGHT/2 - 0.1),
            text_fg=(1, 0.8, 0.2, 1),
            frameColor=(0, 0, 0, 0)
        )

        # 3. Filter/Menü Konténer (Filter Container)
        self.filter_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.3, 0.3, 0.3, 0.5),
            frameSize=(-self.PANEL_WIDTH/2 + 0.05, self.PANEL_WIDTH/2 - 0.05, -0.06, 0.06),
            pos=(0, 0, self.PANEL_HEIGHT/2 - 0.25)
        )

        self.items = self.generate_dummy_data()
        self.create_filters()

        # Oszlop fejlécek
        header_y = self.PANEL_HEIGHT/2 - 0.38
        cols = ["Név", "Típus", "Táv.", "Seb."]
        self.positions = [-0.4, -0.1, 0.2, 0.4] # X pozíciók
        
        for i, col_name in enumerate(cols):
            DirectLabel(
                parent=self.main_frame,
                text=col_name,
                scale=self.FONT_SIZE,
                # Font betöltése (feltételezve, hogy a 'cmtt12' elérhető)
                pos=(self.positions[i], 0, header_y),
                text_fg=(0.7, 0.7, 0.7, 1),
                frameColor=(0,0,0,0)
            )

        # 4. Item Lista Konténer (Scrollable List Container)
        list_top = header_y - 0.05
        list_bottom = -self.PANEL_HEIGHT/2 + 0.05
        list_height = list_top - list_bottom

        self.scroll_frame = DirectScrolledFrame(
            parent=self.main_frame,
            frameSize=(-self.PANEL_WIDTH/2 + 0.05, self.PANEL_WIDTH/2 - 0.05, list_bottom, list_top),
            canvasSize=(-self.PANEL_WIDTH/2, self.PANEL_WIDTH/2 - 0.2, -2, 0),
            frameColor=(0, 0, 0, 0.3),
            scrollBarWidth=0.04,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=(0.5, 0.5, 0.5, 1)
        )

        self.populate_list(self.items)
        
        # DEBUG CÍMKE:
        self.debug_label = DirectLabel(
            parent=self.main_frame,
            text="EGÉR ÁLLAPOT: NEM A UI FELETT (Zoom aktív)",
            scale=0.03,
            pos=(0, 0, -self.PANEL_HEIGHT/2 + 0.02),
            text_fg=(1, 1, 1, 1), 
            frameColor=(0.5, 0, 0, 1)
        )
        
        # A scrollbar re-parentelése a main_frame-hez (csak vizuális javítás)
        if self.scroll_frame.verticalScroll:
            self.scroll_frame.verticalScroll.reparentTo(self.main_frame)
            self.scroll_frame.verticalScroll.setX(self.PANEL_WIDTH/2 - 0.04)


    def set_mouse_over_ui(self, state):
        """Beállítja az állapotot, hogy az egér a panel felett van-e, és frissíti a debug kijelzőt."""
        if self.is_mouse_over_ui != state:
            self.is_mouse_over_ui = state
            if state:
                self.debug_label['text'] = "EGÉR ÁLLAPOT: A UI FELETT (Görgetés aktív)"
                self.debug_label['frameColor'] = (0, 0.5, 0, 1)
            else:
                self.debug_label['text'] = "EGÉR ÁLLAPOT: NEM A UI FELETT (Zoom aktív)"
                self.debug_label['frameColor'] = (0.5, 0, 0, 1)
        
    def create_filters(self):
        """Létrehozza a szűrő gombokat a filter konténerben."""
        btn_props = {
            'scale': 0.035,
            'frameSize': (-2, 2, -0.5, 0.8),
            'relief': DGG.RAISED,
            'borderWidth': (0.01, 0.01)
        }

        DirectButton(
            parent=self.filter_frame,
            text="Összes",
            command=self.populate_list,
            extraArgs=[self.items],
            pos=(-0.3, 0, -0.01),
            **btn_props
        )

        DirectButton(
            parent=self.filter_frame,
            text="Ellenség",
            command=self.filter_by_type,
            extraArgs=["Ellenség"],
            pos=(0, 0, -0.01),
            **btn_props
        )

        DirectButton(
            parent=self.filter_frame,
            text="Rendez: Táv",
            command=self.sort_by_dist,
            pos=(0.3, 0, -0.01),
            **btn_props
        )

    def generate_dummy_data(self):
        """Dummy objektum adatokat generál."""
        data = []
        types = ["Hajó", "Állomás", "Ellenség", "Aszteroida"]
        names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Omega", "Titan", "Icarus", "Viper"]
        
        for i in range(20):
            item = {
                'name': f"{random.choice(names)}-{random.randint(10, 99)}",
                'type': random.choice(types),
                'distance': round(random.uniform(10.0, 5000.0), 1),
                'speed': round(random.uniform(0.0, 800.0), 1)
            }
            data.append(item)
        return data

    def filter_by_type(self, type_name):
        """Szűrés típus alapján."""
        filtered = [x for x in self.items if x['type'] == type_name]
        self.populate_list(filtered)

    def sort_by_dist(self):
        """Rendezés távolság alapján."""
        sorted_items = sorted(self.items, key=lambda x: x['distance'])
        self.populate_list(sorted_items)

    def populate_list(self, data_list):
        """Kitörli a listát és újraépíti a megadott adatokkal."""
        for child in self.scroll_frame.getCanvas().getChildren():
            child.removeNode()

        start_y = 0.03 # Kis padding a tetején
        for i, item in enumerate(data_list):
            y_pos = start_y - (i * self.ITEM_HEIGHT)
            
            bg_color = self.COLOR_ITEM_ODD if i % 2 == 0 else self.COLOR_ITEM_EVEN
            
            row_width = self.PANEL_WIDTH - 0.25 # A scrollbar helyét kivonva
            
            row = DirectFrame(
                parent=self.scroll_frame.getCanvas(),
                frameColor=bg_color,
                # A row szélessége megegyezik a scroll_frame méretével
                frameSize=(-row_width/2, row_width/2, -self.ITEM_HEIGHT/2, self.ITEM_HEIGHT/2),
                pos=(0, 0, y_pos)
            )

            # Oszlopok pozicionálása (relatív a row közepéhez: 0)
            # Név
            DirectLabel(parent=row, text=item['name'], scale=self.FONT_SIZE, 
                       pos=(self.positions[0], 0, 0), text_align=TextNode.ACenter, text_fg=self.COLOR_TEXT, frameColor=(0,0,0,0))
            # Típus
            DirectLabel(parent=row, text=item['type'], scale=self.FONT_SIZE, 
                       pos=(self.positions[1], 0, 0), text_align=TextNode.ACenter, text_fg=(0.8, 0.8, 0.8, 1), frameColor=(0,0,0,0))
            # Távolság
            DirectLabel(parent=row, text=f"{item['distance']}m", scale=self.FONT_SIZE, 
                       pos=(self.positions[2], 0, 0), text_align=TextNode.ARight, text_fg=(0.5, 1, 0.5, 1), frameColor=(0,0,0,0))
            # Sebesség
            DirectLabel(parent=row, text=f"{item['speed']}km/h", scale=self.FONT_SIZE, 
                       pos=(self.positions[3], 0, 0), text_align=TextNode.ARight, text_fg=(1, 0.5, 0.5, 1), frameColor=(0,0,0,0))

        # 3. Canvas méretének frissítése, hogy a görgetés működjön
        total_height = len(data_list) * self.ITEM_HEIGHT
        
        # A canvas méreteinek beállítása (Left, Right, Bottom, Top)
        self.scroll_frame['canvasSize'] = (
            -self.PANEL_WIDTH/2, 
            self.PANEL_WIDTH/2, 
            -total_height - 0.05, 
            0.05
        )
        self.scroll_frame.setCanvasSize()
        
    def destroy(self):
        """Panel elemek megsemmisítése."""
        self.main_frame.destroy()