from panda3d.core import LVector4 as LColor
from panda3d.core import TextNode, Point3
from direct.task import Task

# DirectGUI importok
from direct.gui.DirectGui import *
from direct.gui.DirectGuiGlobals import *

# Feltételezzük, hogy ezek a modulok elérhetőek (a te struktúrád alapján)
from .overview_row import OverviewRow, ROW_HEIGHT, COLUMN_WIDTHS, OVERVIEW_BG, OVERVIEW_LINE, OVERVIEW_TEXT_COLOR

# Update cycle
UPDATE_INTERVAL = 0.35

# Állítható UI méretek
PANEL_WIDTH_ABS = 0.75
PANEL_HEIGHT_ABS = 1.7
BUTTON_SCALE = 0.02
# FIX: A CHECKBOX_SCALE csökkentése, hogy vizuálisan kisebbek legyenek
CHECKBOX_SCALE = 0.012 # Eredeti: 0.015

class OverviewPanel:
    def __init__(self, base, overview_manager):
        self.base = base
        self.manager = overview_manager
        
        self.all_items_data = []
        self.visible_items_data = []

        self.sort_key = 'distance' 
        self.sort_order = 'ASC' 
        
        # Initial filter settings
        self.type_filters = {
            "Ship": True, "Drone": True, "Structure": True, 
            "Wreck": True, "Asteroid": True, "Missile": True
        }
        self.state_filters = {
            "Targeted": False, "Attacking": False, "WithinRange": False
        }
        self.selected_item_id = None
        self.context_menu = None
        
        # UI setup
        self.setup_ui()
        
        # Initial data load
        self.all_items_data = self.manager.get_all_items_data()
        self.rebuild_list()
        
        # Start update task
        self.base.taskMgr.doMethodLater(UPDATE_INTERVAL, self.update_overview_task, "OverviewUpdateTask")
        
    def setup_ui(self):
        """UI felépítése: Keret, szűrők, lista."""
        
        # --- 1. Main Panel Frame ---
        self.main_frame = DirectFrame(
            frameColor=OVERVIEW_BG,
            frameSize=(0, PANEL_WIDTH_ABS, -PANEL_HEIGHT_ABS, 0), 
            pos=(0.02, 0, -0.02),
            parent=self.base.a2dTopLeft, 
            relief=DGG.FLAT
        )

        # --- Top Header & Filter Tab ---
        header_height = 0.05
        filter_area_height = 0.25
        
        # Title
        DirectLabel(
            parent=self.main_frame,
            text="Overview",
            text_fg=OVERVIEW_TEXT_COLOR,
            text_scale=0.035,
            frameColor=OVERVIEW_LINE * 0.5,
            frameSize=(0, PANEL_WIDTH_ABS, -header_height, 0),
            pos=(0, 0, 0),
            text_align=TextNode.ACenter,
            text_pos=(PANEL_WIDTH_ABS / 2, -0.035) # Középre igazítás
        )

        # Filter Frame
        self.filter_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=OVERVIEW_BG * 0.8,
            frameSize=(0, PANEL_WIDTH_ABS, -filter_area_height, 0),
            pos=(0, 0, -header_height),
            relief=DGG.FLAT
        )
        
        # --- Type Filters (Checkboxes) ---
        x_offset = 0.01
        y_start = -0.01
        
        DirectLabel(
            parent=self.filter_frame, 
            text="TÍPUS SZŰRŐ:", 
            text_scale=0.02, 
            text_fg=OVERVIEW_TEXT_COLOR, 
            frameColor=(0,0,0,0), 
            pos=(x_offset, 0, y_start), 
            text_align=TextNode.ALeft
        )
        
        type_keys = list(self.type_filters.keys())
        for i, f_type in enumerate(type_keys):
            # Checkbox létrehozása
            checkbox = DirectCheckButton(
                parent=self.filter_frame,
                text=f_type,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=CHECKBOX_SCALE,
                # FIX: boxScale explicit beállítása a jelző méretének csökkentéséhez
                scale=CHECKBOX_SCALE * 0.8, 
                boxRelief=DGG.FLAT,
                indicatorValue=self.type_filters[f_type], # Helyes inicializálás
                command=self.toggle_type_filter,
                extraArgs=[f_type],
                pos=(x_offset + 0.05 + (i % 3) * 0.23, 0, y_start - 0.04 - (i // 3) * 0.04),
                text_align=TextNode.ALeft
            )


        # --- State Filters ---
        state_y_start = y_start - 0.04 - (len(type_keys)//3 + 1) * 0.04 - 0.01
        
        DirectLabel(
            parent=self.filter_frame, 
            text="ÁLLAPOT SZŰRŐ:", 
            text_scale=0.02, 
            text_fg=OVERVIEW_TEXT_COLOR, 
            frameColor=(0,0,0,0), 
            pos=(x_offset, 0, state_y_start), 
            text_align=TextNode.ALeft
        )
        
        for i, f_state in enumerate(self.state_filters.keys()):
            checkbox = DirectCheckButton(
                parent=self.filter_frame,
                text=f_state,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=CHECKBOX_SCALE,
                # FIX: boxScale explicit beállítása a jelző méretének csökkentéséhez
                scale=CHECKBOX_SCALE * 0.8, 
                boxRelief=DGG.FLAT,
                indicatorValue=self.state_filters[f_state], # Helyes inicializálás
                command=self.toggle_state_filter,
                extraArgs=[f_state],
                pos=(x_offset + 0.05 + i * 0.25, 0, state_y_start - 0.04),
                text_align=TextNode.ALeft
            )

        # --- Column Headers ---
        header_y_list = -header_height - filter_area_height 
        self.column_headers = []
        col_titles = ['Ikon', 'Név', 'Távolság', 'Sebesség', 'Szögseb.', 'Veszély'] 
        col_keys = ['icon', 'name', 'distance', 'velocity', 'angular', 'threat'] 
        x_offset = 0
        
        # Separator line top
        DirectFrame(parent=self.main_frame, frameColor=OVERVIEW_LINE, frameSize=(0, PANEL_WIDTH_ABS, 0, 0.001), pos=(0, 0, header_y_list + ROW_HEIGHT/2))
        
        total_relative_width = sum(COLUMN_WIDTHS)
        
        for i, (relative_width, title, key) in enumerate(zip(COLUMN_WIDTHS, col_titles, col_keys)):
            width = PANEL_WIDTH_ABS * (relative_width / total_relative_width)
            
            # Igazítás beállítása
            align = TextNode.ALeft
            text_x = 0.005
            if title in ('Ikon', 'Veszély'):
                align = TextNode.ACenter
                text_x = width / 2
            
            btn = DirectButton(
                parent=self.main_frame,
                text=title,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=BUTTON_SCALE,
                text_align=align,
                text_pos=(text_x, -ROW_HEIGHT/4),
                frameColor=OVERVIEW_BG * 1.5,
                relief=DGG.FLAT,
                frameSize=(0, width, -ROW_HEIGHT/2, ROW_HEIGHT/2),
                pos=(x_offset, 0, header_y_list),
                command=self.sort_by_column,
                extraArgs=[key]
            )
            self.column_headers.append(btn)
            x_offset += width

        # Separator line bottom
        DirectFrame(parent=self.main_frame, frameColor=OVERVIEW_LINE, frameSize=(0, PANEL_WIDTH_ABS, -0.001, 0), pos=(0, 0, header_y_list - ROW_HEIGHT/2))

        # --- Scrollable List Area ---
        list_top_z = header_y_list - ROW_HEIGHT/2
        list_bottom_z = -PANEL_HEIGHT_ABS + 0.02
        list_height = list_top_z - list_bottom_z
        
        # FIX: Létrehozzuk a dedikált keretet a görgethető listának (tisztább elrendezés)
        self.list_area_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0, 0, 0, 0), # Átlátszó keret
            frameSize=(0, PANEL_WIDTH_ABS, -list_height, 0), # Méret megegyezik a görgethető területtel
            pos=(0, 0, list_top_z), # Pozíció a fejléc alatt
            relief=DGG.FLAT
        )
        
        self.scroll_list = DirectScrolledList(
            parent=self.list_area_frame, # FIX: Új szülő a lista keret
            numItemsVisible=int(list_height / ROW_HEIGHT),
            # A frame mérete az új szülő (list_area_frame) méretéhez igazodik
            frameSize=(0, PANEL_WIDTH_ABS, -list_height, 0),
            frameColor=OVERVIEW_BG * 0.9,
            pos=(0, 0, 0), # A szülő keret tetejére pozícionálva (0, 0)
            relief=DGG.FLAT,
            # FIX: forceHeight visszaállítása kritikus az "elcsúszás" megakadályozására.
            forceHeight=ROW_HEIGHT, 
            # Scrollbar stílus javítás
            incButton_frameSize=(0, 0, 0, 0), 
            decButton_frameSize=(0, 0, 0, 0)
        )
        
    def row_command(self, action, item_id, event=None):
        """Sor kattintás/jobbklikk kezelő."""
        item_data = next((item for item in self.all_items_data if item['id'] == item_id), None)
        if not item_data: return

        if action == 'select':
            self.set_selected(item_id)
        elif action == 'context_menu':
            self.set_selected(item_id) # Jobbklikk is jelölje ki
            self.show_context_menu(item_data)
        
    def make_row_item(self, item_data, command_callback):
        """Létrehoz egy OverviewRow UI elemet."""
        # FIX: parent=None beállítása, hagyva, hogy az addItem() kezelje a szülőhöz rendelést.
        row = OverviewRow(
            parent=None,
            item_data=item_data,
            command_callback=command_callback
        )
        return row

    def update_overview_task(self, task):
        """Az időzített frissítési feladat (0.35s)."""
        # 1. Adatok frissítése
        self.all_items_data = self.manager.get_all_items_data()
        
        # 2. Szűrés és rendezés
        new_visible_data = self._filter_and_sort(self.all_items_data)
        
        current_data_ids = [item['id'] for item in self.visible_items_data]
        new_data_ids = [item['id'] for item in new_visible_data]
        
        # 3. Optimalizáció: Csak akkor építjük újra, ha a lista hossza vagy sorrendje változott
        if current_data_ids != new_data_ids:
            self.rebuild_list(new_visible_data)
        else:
            # Egyébként csak a tartalmat frissítjük (pl. távolság változása)
            self.visible_items_data = new_visible_data
            self.update_row_contents(new_visible_data)
            
        return task.again

    def update_row_contents(self, new_data):
        """Csak a meglévő sorok szöveges tartalmát frissíti (teljesítmény javítás)."""
        data_map = {item['id']: item for item in new_data}
        
        for row in self.scroll_list['items']:
            item_id = row.item_data['id']
            if item_id in data_map:
                row.update_content(data_map[item_id])

    def sort_by_column(self, column_key):
        """Oszlop szerinti rendezés beállítása."""
        if self.sort_key == column_key:
            self.sort_order = 'DESC' if self.sort_order == 'ASC' else 'ASC'
        else:
            self.sort_key = column_key
            self.sort_order = 'ASC'

        self.rebuild_list()

    def _filter_and_sort(self, data):
        """Szűrők és rendezés alkalmazása."""
        
        # --- Filtering ---
        filtered = []
        for item in data:
            # Type Filter
            if not self.type_filters.get(item['type'], True):
                continue

            # State Filter
            state_active = any(self.state_filters.values())
            if not state_active:
                filtered.append(item)
            else:
                # OR logika: ha bármelyik aktív filter illeszkedik az item flagjére
                match = False
                for state, is_active in self.state_filters.items():
                    if is_active and state in item['flags']:
                        match = True
                        break
                if match:
                    filtered.append(item)
                
        # --- Sorting ---
        reverse = (self.sort_order == 'DESC')
        key = self.sort_key
        
        # Biztonságos rendezés (ha hiányzik a kulcs, ne crasheljen)
        def sort_helper(x):
            val = x.get(key)
            if val is None:
                return 0 if key in ('distance', 'velocity', 'angular', 'threat') else ""
            return val

        sorted_data = sorted(filtered, key=sort_helper, reverse=reverse)
        return sorted_data

    def rebuild_list(self, new_data=None):
        """Teljes lista újraépítése."""
        if new_data is None:
            new_data = self._filter_and_sort(self.all_items_data)
            
        self.visible_items_data = new_data
        
        # Eltávolítjuk a régi elemeket
        self.scroll_list.removeAndDestroyAllItems()
        
        # Új elemek hozzáadása
        for item_data in self.visible_items_data:
            row = self.make_row_item(item_data, self.row_command)
            if self.selected_item_id == item_data['id']:
                row.set_selected(True)
            self.scroll_list.addItem(row)
            
        self.scroll_list.refresh()

    def set_selected(self, item_id):
        """Kiválasztott elem beállítása."""
        # Régi kijelölés törlése
        if self.selected_item_id is not None:
            for row in self.scroll_list['items']:
                if row.item_data['id'] == self.selected_item_id:
                    row.set_selected(False)
                    break
        
        # JAVÍTVA: Az indentálási hiba korrigálva. A változó beállítása a loopon kívül történik.
        self.selected_item_id = item_id

        # Új kijelölés megjelenítése
        if self.selected_item_id is not None:
            for row in self.scroll_list['items']:
                if row.item_data['id'] == self.selected_item_id:
                    row.set_selected(True)
                    break

    def toggle_type_filter(self, state, f_type): # DirectCheckButton sorrend: status, extraArgs
        """Típus szűrő kapcsolása."""
        self.type_filters[f_type] = bool(state)
        self.rebuild_list()
        
    def toggle_state_filter(self, state, f_state):
        """Állapot szűrő kapcsolása."""
        self.state_filters[f_state] = bool(state)
        self.rebuild_list()
        
    def show_context_menu(self, item_data):
        """Jobbklikk menü megjelenítése."""
        if self.context_menu:
            self.context_menu.destroy()
        
        options = [
            ("Célzárolás", lambda: print(f"-> Lock Target: {item_data['name']}")),
            ("Megközelítés", lambda: print(f"-> Approach: {item_data['name']}")),
            ("Keringés", lambda: print(f"-> Orbit: {item_data['name']}")),
            ("Távolmaradás (10km)", lambda: print(f"-> Keep Range: {item_data['name']}")),
            ("Ugrás ide", lambda: print(f"-> Warp To: {item_data['name']}")),
        ]
        
        menu_width = 0.35
        menu_item_height = 0.05
        menu_height = len(options) * menu_item_height
        
        # Mouse pozíció pontos lekérése a render2d térben, majd konvertálás az a2dTopLeft-hez
        if self.base.mouseWatcherNode.hasMouse():
            mpos = self.base.mouseWatcherNode.getMouse() # (-1, 1) tartomány
            
            # A képernyő koordinátát (render2d) át kell számolni az a2dTopLeft (bal felső sarok relatív) rendszerbe.
            # Létrehozunk egy pontot a render2d síkon (Z=0, mivel 2D)
            p3_render2d = Point3(mpos.getX(), 0, mpos.getY())
            
            # Átkonvertáljuk az a2dTopLeft node koordináta rendszerébe
            rel_pos = self.base.a2dTopLeft.getRelativePoint(self.base.render2d, p3_render2d)
            
            # Offset, hogy a kurzor hegyénél nyíljon, ne közepén
            final_pos = (rel_pos.getX() + 0.01, 0, rel_pos.getZ() - 0.01)
        else:
            final_pos = (0.5, 0, -0.5) # Fallback

        self.context_menu = DirectFrame(
            parent=self.base.a2dTopLeft,
            frameColor=OVERVIEW_BG * 1.5,
            frameSize=(0, menu_width, -menu_height, 0),
            pos=final_pos,
            relief=DGG.RAISED,
            borderWidth=(0.005, 0.005),
            sortOrder=1000 # Mindig felül legyen
        )

        for i, (text, cmd) in enumerate(options):
            DirectButton(
                parent=self.context_menu,
                text=text,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=0.03,
                text_align=TextNode.ALeft,
                text_pos=(0.02, -0.015),
                frameColor=(0,0,0,0), # Átlátszó háttér, csak hover effekt kellene (alap DirectGui-ban nincs hover color prop, de így is jó)
                relief=DGG.FLAT,
                frameSize=(0, menu_width, -menu_item_height, 0),
                pos=(0, 0, -i * menu_item_height),
                command=lambda c=cmd: [c(), self.destroy_context_menu()]
            )
            
        # Globális kattintás figyelő a menü bezárásához
        self.base.acceptOnce('mouse1', self.destroy_context_menu)
        self.base.acceptOnce('mouse3', self.destroy_context_menu) # Jobb klikk máshova is bezárja
        
    def destroy_context_menu(self, event=None):
        """Context menü megsemmisítése."""
        # Ha a gombra kattintunk, az eseményt el kell dobni, nehogy azonnal újra megnyíljon (ha az 'event' paramétert használjuk)
        if self.context_menu:
            self.context_menu.destroy()
            self.context_menu = None
            
    def destroy(self):
        """Takarítás."""
        self.base.taskMgr.remove("OverviewUpdateTask")
        self.base.ignore('mouse1')
        self.base.ignore('mouse3')
        if self.context_menu:
            self.context_menu.destroy()
        if self.main_frame:
            self.main_frame.destroy()