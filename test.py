from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3, Vec4
import random

# Ablak beállítások (opcionális, csak a tisztább megjelenésért)
from panda3d.core import loadPrcFileData
loadPrcFileData('', 'window-title Panda3D Overview Panel')
loadPrcFileData('', 'win-size 1024 768')

class OverviewPanel:
    def __init__(self):
        # UI Skálázási konstansok (Könnyű skálázhatóság)
        self.PANEL_WIDTH = 1.2
        self.PANEL_HEIGHT = 1.5
        self.ITEM_HEIGHT = 0.08
        self.FONT_SIZE = 0.045
        
        # Színek (R, G, B, A)
        self.COLOR_BG = (0.1, 0.1, 0.1, 0.9)
        self.COLOR_HEADER = (0.2, 0.2, 0.2, 1)
        self.COLOR_ITEM_ODD = (0.15, 0.15, 0.15, 1)
        self.COLOR_ITEM_EVEN = (0.12, 0.12, 0.12, 1)
        self.COLOR_TEXT = (1, 1, 1, 1)

        # Állapotkövetés: Figyeli, hogy az egér a panel felett van-e (True = felette, False = 3D térben)
        self.is_mouse_over_ui = False 

        # 1. Fő konténer (Main Container)
        # aspect2d-t használunk, így a képaránytól függetlenül marad a helyén
        self.main_frame = DirectFrame(
            frameColor=self.COLOR_BG,
            frameSize=(-self.PANEL_WIDTH/2, self.PANEL_WIDTH/2, -self.PANEL_HEIGHT/2, self.PANEL_HEIGHT/2),
            pos=(-0.7, 0, 0),  # Bal oldalra igazítva
            state=DGG.NORMAL # Fontos, hogy fogadja az egéreseményeket a teljes felületén
        )

        # Eseménykötések eltávolítva. A MyApp feladata fogja a pozíciót manuálisan ellenőrizni.

        # 2. Cím (Overview Title)
        self.title = DirectLabel(
            parent=self.main_frame,
            text="ÁTTEKINTÉS (OVERVIEW)",
            scale=0.07,
            pos=(0, 0, self.PANEL_HEIGHT/2 - 0.1),
            text_fg=(1, 0.8, 0.2, 1), # Arany szín
            frameColor=(0, 0, 0, 0)   # Átlátszó háttér
        )

        # 3. Filter/Menü Konténer (Filter Container)
        # Ez a cím alatt helyezkedik el
        self.filter_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.3, 0.3, 0.3, 0.5),
            frameSize=(-self.PANEL_WIDTH/2 + 0.05, self.PANEL_WIDTH/2 - 0.05, -0.06, 0.06),
            pos=(0, 0, self.PANEL_HEIGHT/2 - 0.25)
        )

        # Adatok inicializálása ELŐRE, hogy a filter gombok hivatkozhassanak rá
        self.items = self.generate_dummy_data()

        # Filter Gombok létrehozása
        self.create_filters()

        # Oszlop fejlécek (Labels for Name, Type, Dist, Speed)
        header_y = self.PANEL_HEIGHT/2 - 0.38
        cols = ["Név", "Típus", "Táv.", "Seb."]
        positions = [-0.4, -0.1, 0.2, 0.4] # X pozíciók
        
        for i, col_name in enumerate(cols):
            DirectLabel(
                parent=self.main_frame,
                text=col_name,
                scale=self.FONT_SIZE,
                text_font=loader.loadFont('cmtt12'), # Monospace font a jobb igazításért
                pos=(positions[i], 0, header_y),
                text_fg=(0.7, 0.7, 0.7, 1),
                frameColor=(0,0,0,0)
            )

        # 4. Item Lista Konténer (Scrollable List Container)
        # Ez egy görgethető keret
        list_top = header_y - 0.05
        list_bottom = -self.PANEL_HEIGHT/2 + 0.05
        list_height = list_top - list_bottom

        self.scroll_frame = DirectScrolledFrame(
            parent=self.main_frame,
            frameSize=(-self.PANEL_WIDTH/2 + 0.05, self.PANEL_WIDTH/2 - 0.05, list_bottom, list_top),
            canvasSize=(-self.PANEL_WIDTH/2, self.PANEL_WIDTH/2 - 0.2, -2, 0), # Dinamikusan lesz állítva
            frameColor=(0, 0, 0, 0.3),
            scrollBarWidth=0.04,
            verticalScroll_thumb_relief=DGG.FLAT,
            verticalScroll_thumb_frameColor=(0.5, 0.5, 0.5, 1)
        )

        # Lista feltöltése (Az adatok inicializálva vannak feljebb)
        self.populate_list(self.items)
        
        # DEBUG CÍMKE: Vizuális visszajelzés a 'is_mouse_over_ui' állapotról
        self.debug_label = DirectLabel(
            parent=self.main_frame,
            text="EGÉR ÁLLAPOT: NEM A UI FELETT (Zoom aktív)",
            scale=0.03,
            pos=(0, 0, -self.PANEL_HEIGHT/2 + 0.02), # A panel aljára helyezve
            text_fg=(1, 1, 1, 1), 
            frameColor=(0.5, 0, 0, 1) # Piros háttér
        )


    def set_mouse_over_ui(self, state):
        """Beállítja az állapotot, hogy az egér a panel felett van-e, és frissíti a debug kijelzőt."""
        
        # Csak akkor frissítsük a UI-t, ha az állapot változott
        if self.is_mouse_over_ui != state:
            self.is_mouse_over_ui = state
            
            # Vizuális visszajelzés frissítése
            if state:
                self.debug_label['text'] = "EGÉR ÁLLAPOT: A UI FELETT (Görgetés aktív)"
                self.debug_label['frameColor'] = (0, 0.5, 0, 1) # Zöld
            else:
                self.debug_label['text'] = "EGÉR ÁLLAPOT: NEM A UI FELETT (Zoom aktív)"
                self.debug_label['frameColor'] = (0.5, 0, 0, 1) # Piros
        
    def create_filters(self):
        """Létrehozza a szűrő gombokat a filter konténerben."""
        btn_props = {
            'scale': 0.035,
            'frameSize': (-2, 2, -0.5, 0.8),
            'relief': DGG.RAISED,
            'borderWidth': (0.01, 0.01)
        }

        # Gomb 1: Összes
        DirectButton(
            parent=self.filter_frame,
            text="Összes",
            command=self.populate_list,
            extraArgs=[self.items],
            pos=(-0.3, 0, -0.01),
            **btn_props
        )

        # Gomb 2: Csak Ellenség (Szűrés példa)
        DirectButton(
            parent=self.filter_frame,
            text="Ellenség",
            command=self.filter_by_type,
            extraArgs=["Ellenség"],
            pos=(0, 0, -0.01),
            **btn_props
        )

        # Gomb 3: Rendezés Távolság szerint
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
        
        for i in range(20): # 20 elem generálása
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
        # 1. Törlés: Minden meglévő gyereket törlünk a canvas-ról
        for child in self.scroll_frame.getCanvas().getChildren():
            child.removeNode()

        # 2. Újraépítés
        start_y = 0
        for i, item in enumerate(data_list):
            y_pos = start_y - (i * self.ITEM_HEIGHT)
            
            # Váltakozó háttérszín a soroknak
            bg_color = self.COLOR_ITEM_ODD if i % 2 == 0 else self.COLOR_ITEM_EVEN
            
            # Sor Konténer (Item Row)
            row = DirectFrame(
                parent=self.scroll_frame.getCanvas(),
                frameColor=bg_color,
                frameSize=(-self.PANEL_WIDTH/2 + 0.05, self.PANEL_WIDTH/2 - 0.2, -0.03, 0.04),
                pos=(0, 0, y_pos)
            )

            # Oszlopok pozicionálása (ugyanaz mint a fejléc)
            # Név
            DirectLabel(parent=row, text=item['name'], scale=self.FONT_SIZE, 
                       pos=(-0.4, 0, 0), text_align=TextNode.ACenter, text_fg=self.COLOR_TEXT, frameColor=(0,0,0,0))
            # Típus
            DirectLabel(parent=row, text=item['type'], scale=self.FONT_SIZE, 
                       pos=(-0.1, 0, 0), text_align=TextNode.ACenter, text_fg=(0.8, 0.8, 0.8, 1), frameColor=(0,0,0,0))
            # Távolság
            DirectLabel(parent=row, text=f"{item['distance']}m", scale=self.FONT_SIZE, 
                       pos=(0.2, 0, 0), text_align=TextNode.ARight, text_fg=(0.5, 1, 0.5, 1), frameColor=(0,0,0,0))
            # Sebesség
            DirectLabel(parent=row, text=f"{item['speed']}km/h", scale=self.FONT_SIZE, 
                       pos=(0.4, 0, 0), text_align=TextNode.ARight, text_fg=(1, 0.5, 0.5, 1), frameColor=(0,0,0,0))

        # 3. Canvas méretének frissítése, hogy a görgetés működjön
        # Kiszámoljuk a teljes magasságot
        total_height = len(data_list) * self.ITEM_HEIGHT
        # Beállítjuk a canvas méretét (Left, Right, Bottom, Top)
        # Fontos: A Bottom értéknek negatívnak kell lennie és elég nagynak
        self.scroll_frame['canvasSize'] = (
            -self.PANEL_WIDTH/2 + 0.05, 
            self.PANEL_WIDTH/2 - 0.2, 
            -total_height + 0.05, 
            0.05
        )
        self.scroll_frame.setCanvasSize() # Frissítés kényszerítése

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Kikapcsoljuk az alapértelmezett egér irányítást, hogy használhassuk az egeret a UI-hoz
        self.disableMouse()
        
        # Betöltünk egy egyszerű modellt háttérnek, hogy lássuk a 3D teret
        self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.render)
        self.environ.setScale(0.25, 0.25, 0.25)
        # A modell messze van, hogy legyen mit nézni
        self.environ.setPos(-8, 42, 0) 
        
        # Kamera pozíció
        self.camera.setPos(0, -20, 5)
        # FRISSÍTÉS: A kamera most a modellre néz
        self.camera.lookAt(self.environ) 

        # UI Panel Létrehozása
        self.ui = OverviewPanel()

        # Eseménykezelők, amelyek nem lesznek elnyelve a GUI által, de figyelni kell, hogy az egér gomb megnyomódott-e.
        # A zoom in/out logikát áttesszük a taskba a scroll frame manuális kezelése miatt.
        
        # ÚJ: Task a mouse over állapot manuális frissítésére minden képkockán
        self.taskMgr.add(self.update_mouse_state_task, "UpdateMouseStateTask")

        # ÚJ: Az egérgörgő események regisztrálása, de a kezelést a task végzi.
        # A task csak akkor zoomol, ha az egér NINCS a UI felett.
        self.accept('wheel_up', self.handle_scroll, ['up'])
        self.accept('wheel_down', self.handle_scroll, ['down'])
        
        # Állapot követése, ha a görgő megnyomódott
        self.scroll_direction = None

        # Kilépés ESC gombbal
        self.accept("escape", self.userExit)
        
    def handle_scroll(self, direction):
        """Mentjük a görgetés irányát, amelyet a task fog feldolgozni."""
        # Ezt az eseményt fogja el a Panda3D, ha a görgő elmozdul, függetlenül attól, hogy a GUI felett van-e.
        self.scroll_direction = direction
        
    def update_mouse_state_task(self, task):
        """Manuálisan ellenőrzi, hogy az egér a UI panel felett van-e, és kezeli a görgetést/zoomot."""
        
        is_over = False
        
        if self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_z = self.mouseWatcherNode.getMouseY() 
            
            x_min, x_max, z_min, z_max = self.ui.main_frame.getBounds()
            
            if x_min <= mouse_x <= x_max and z_min <= mouse_z <= z_max:
                is_over = True
        
        # Állapot frissítése a panel osztályban
        self.ui.set_mouse_over_ui(is_over)
        
        # Görgetés/Zoom kezelése
        if self.scroll_direction:
            if self.ui.is_mouse_over_ui:
                # 1. UI FELETT: Görgetés kezelése a DirectScrolledFrame-en
                bar = self.ui.scroll_frame.verticalScroll
                current_value = bar['value']
                
                # Növelt görgetési sebesség, hogy jobban látszódjon (0.1 -> 0.25)
                scroll_amount = 0.25 
                
                if self.scroll_direction == 'up':
                    # Csökkentjük az értéket, ha felfelé görgetünk (0.0 a lista teteje)
                    bar['value'] = max(0.0, current_value - scroll_amount)
                elif self.scroll_direction == 'down':
                    # Növeljük az értéket, ha lefelé görgetünk (1.0 a lista alja)
                    bar['value'] = min(1.0, current_value + scroll_amount)

            else:
                # 2. 3D TÉRBEN: Zoomolás kezelése a kamerán
                if self.scroll_direction == 'up':
                    self.zoom_in()
                elif self.scroll_direction == 'down':
                    self.zoom_out()
                    
            # Reseteljük a görgetési irányt, hogy csak egyszer dolgozzuk fel
            self.scroll_direction = None
        
        return task.cont

    def zoom_in(self):
        """Bezoomolás."""
        current_pos = self.camera.getPos()
        new_y = current_pos.y + 2
        # Limit: maximális bezoomolás (Y=-5-nél áll meg, hogy ne menjünk a modell elé/át)
        self.camera.setY(min(new_y, -5)) 

    def zoom_out(self):
        """Kizoomolás."""
        current_pos = self.camera.getPos()
        new_y = current_pos.y - 2
        # Limit: maximális kizoomolás (Y=-50-nél áll meg)
        self.camera.setY(max(new_y, -50)) 

app = MyApp()
app.run()