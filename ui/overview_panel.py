from panda3d.core import LVector4 as LColor, TextNode
from direct.task import Task
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DGG, DirectCheckButton
from direct.gui.DirectScrolledList import DirectScrolledList, DirectScrolledListItem

from .overview_row import OverviewRow, ROW_HEIGHT, COLUMN_WIDTHS, OVERVIEW_BG, OVERVIEW_LINE, OVERVIEW_TEXT_COLOR

UPDATE_INTERVAL = 0.35 

class OverviewPanel:
    def __init__(self, base, overview_manager):
        self.base = base
        self.manager = overview_manager
        
        self.all_items_data = []
        self.visible_items_data = []

        self.sort_key = 'distance'
        self.sort_order = 'ASC'
        
        self.type_filters = {
            "Ship": True, "Drone": True, "Structure": True, 
            "Wreck": True, "Asteroid": True, "Missile": True
        }
        self.state_filters = {
            "Targeted": False, "Attacking": False, "WithinRange": False
        }
        self.selected_item_id = None
        
        self.setup_ui()
        
        self.all_items_data = self.manager.get_all_items_data()
        self.rebuild_list()
        
        self.base.taskMgr.doMethodLater(UPDATE_INTERVAL, self.update_overview_task, "OverviewUpdateTask")
        
        self.context_menu = None
        
    def setup_ui(self):
        # IDE KELL BEAVATKOZNI A PANEL TELJES MÉRETÉHEZ
        
        # PANEL_WIDTH: Az oszlopok szélességének összege + kis margó
        PANEL_WIDTH = sum(COLUMN_WIDTHS) + 0.02
        
        # PANEL_HEIGHT: A panel magassága. Ezt növelje, ha hosszabb panelt szeretne!
        # Például 1.4 helyett 1.6 vagy 1.8
        PANEL_HEIGHT = 1.4 
        
        # A méretezés további része...
        aspect_ratio = self.base.getAspectRatio()
        safe_x_pos = -aspect_ratio + (PANEL_WIDTH + 0.02) / 2
        
        self.main_frame = DirectFrame(
            frameColor=OVERVIEW_BG,
            # frameSize az aktuális PANEL_WIDTH és PANEL_HEIGHT értékekkel
            frameSize=(-0.01, PANEL_WIDTH + 0.01, -PANEL_HEIGHT/2 - 0.02, PANEL_HEIGHT/2 + 0.02),
            pos=(safe_x_pos, 0, 0),
            parent=self.base.aspect2d,
            relief=DGG.FLAT
        )
        
        # --- Header ---
        header_height = 0.05
        filter_area_height = 0.2
        # list_top_y a PANEL_HEIGHT-hez viszonyítva van kiszámolva
        list_top_y = PANEL_HEIGHT/2 - header_height * 1.5 - filter_area_height/2
        
        DirectLabel(
            parent=self.main_frame,
            text="Overview",
            text_fg=OVERVIEW_TEXT_COLOR,
            text_scale=0.03,
            frameColor=OVERVIEW_LINE * 0.5,
            frameSize=(-PANEL_WIDTH/2, PANEL_WIDTH/2, -header_height, header_height),
            pos=(0, 0, PANEL_HEIGHT/2 - header_height)
        )

        # Filter Frame
        self.filter_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=OVERVIEW_BG * 0.8,
            frameSize=(-PANEL_WIDTH/2, PANEL_WIDTH/2, -filter_area_height/2, filter_area_height/2),
            pos=(0, 0, list_top_y + filter_area_height/2 + 0.01),
            relief=DGG.FLAT
        )
        
        # Type Filters
        x_offset = -PANEL_WIDTH/2 + 0.01
        y_start = filter_area_height/2 - 0.01
        
        DirectLabel(parent=self.filter_frame, text="TÍPUS SZŰRŐ:", text_scale=0.018, text_fg=OVERVIEW_TEXT_COLOR, frameColor=(0,0,0,0), pos=(x_offset, 0, y_start), text_align=TextNode.ALeft)
        
        type_keys = list(self.type_filters.keys())
        for i, f_type in enumerate(type_keys):
            DirectCheckButton(
                parent=self.filter_frame,
                text=f_type,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=0.015,
                boxRelief=DGG.FLAT,
                frameColor=(0.2, 0.4, 0.6, 1),
                indicatorValue=self.type_filters[f_type],
                command=self.toggle_type_filter,
                extraArgs=[f_type],
                pos=(x_offset + 0.05 + (i % 3) * 0.15, 0, y_start - 0.04 - (i // 3) * 0.04)
            )

        # State Filters
        state_y_start = y_start - 0.04 - (len(type_keys)//3 + 1) * 0.04
        DirectLabel(parent=self.filter_frame, text="ÁLLAPOT SZŰRŐ:", text_scale=0.018, text_fg=OVERVIEW_TEXT_COLOR, frameColor=(0,0,0,0), pos=(x_offset, 0, state_y_start), text_align=TextNode.ALeft)
        
        for i, f_state in enumerate(self.state_filters.keys()):
            DirectCheckButton(
                parent=self.filter_frame,
                text=f_state,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=0.015,
                boxRelief=DGG.FLAT,
                frameColor=(0.6, 0.4, 0.2, 1),
                indicatorValue=self.state_filters[f_state],
                command=self.toggle_state_filter,
                extraArgs=[f_state],
                pos=(x_offset + 0.05 + i * 0.2, 0, state_y_start - 0.04)
            )

        # --- Column Headers ---
        header_y_list = list_top_y
        self.column_headers = []
        col_titles = ['Ikon', 'Név', 'Távolság', 'Sebesség', 'Szögseb.', 'Veszély']
        col_keys = ['icon', 'name', 'distance', 'velocity', 'angular', 'threat']
        x_offset = -PANEL_WIDTH/2
        
        DirectFrame(parent=self.main_frame, frameColor=OVERVIEW_LINE, frameSize=(-PANEL_WIDTH/2, PANEL_WIDTH/2, -0.001, 0.001), pos=(0, 0, header_y_list + ROW_HEIGHT/2))
        
        for i, (width, title, key) in enumerate(zip(COLUMN_WIDTHS, col_titles, col_keys)):
            align = TextNode.ALeft if title not in ('Ikon', 'Veszély') else TextNode.ACenter
            
            btn = DirectButton(
                parent=self.main_frame,
                text=title,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=0.02,
                text_align=align,
                frameColor=OVERVIEW_BG * 1.5,
                relief=DGG.FLAT,
                frameSize=(-width/2, width/2, -ROW_HEIGHT/2, ROW_HEIGHT/2),
                pos=(x_offset + width/2, 0, header_y_list),
                command=self.sort_by_column,
                extraArgs=[key]
            )
            text_x = -width/2 + 0.005 if title not in ('Ikon', 'Veszély') else 0
            btn['text_pos'] = (text_x, -ROW_HEIGHT/4)
            self.column_headers.append(btn)
            x_offset += width

        DirectFrame(parent=self.main_frame, frameColor=OVERVIEW_LINE, frameSize=(-PANEL_WIDTH/2, PANEL_WIDTH/2, -0.001, 0.001), pos=(0, 0, header_y_list - ROW_HEIGHT/2))

        # --- List Area ---
        list_bottom = -PANEL_HEIGHT/2 + 0.02
        # list_height automatikusan igazodik a PANEL_HEIGHT-hez
        list_height = header_y_list - ROW_HEIGHT/2 - list_bottom

        # Görgethető Lista inicializálása
        self.scroll_list = DirectScrolledList(
            parent=self.main_frame,
            itemMakeFunction=self.make_row_item,
            itemMakeExtraArgs=[self.row_command],
            # numItemsVisible is a list_height és ROW_HEIGHT arányából van számolva
            numItemsVisible=int(list_height / ROW_HEIGHT),
            itemFrame_frameSize=(-PANEL_WIDTH/2, PANEL_WIDTH/2, -list_height/2, list_height/2),
            itemFrame_pos=(0, 0, 0),
            frameSize=(-PANEL_WIDTH/2, PANEL_WIDTH/2, -list_height/2, list_height/2),
            frameColor=OVERVIEW_BG * 0.9,
            pos=(0, 0, list_bottom + list_height/2),
            relief=DGG.FLAT,
            forceHeight=ROW_HEIGHT
        )
        
    def row_command(self, action, item_id, event=None):
        item_data = next((item for item in self.all_items_data if item['id'] == item_id), None)
        if not item_data: return

        if action == 'select':
            self.set_selected(item_id)
        elif action == 'context_menu':
            self.set_selected(item_id)
            self.show_context_menu(item_data, event)
        
    def make_row_item(self, item_data, command_callback):
        # JAVÍTÁS: A görgethető lista elemeinek szülőjének a lista belső, görgethető keretét (.itemFrame) kell megadni,
        # különben a pozíciók nem a görgethető nézethez viszonyítva lesznek számolva.
        row = OverviewRow(
            parent=self.scroll_list.itemFrame,
            item_data=item_data,
            command_callback=command_callback
        )
        return row

    def update_overview_task(self, task):
        self.all_items_data = self.manager.get_all_items_data()
        new_visible_data = self._filter_and_sort(self.all_items_data)
        
        current_data_ids = [item['id'] for item in self.visible_items_data]
        new_data_ids = [item['id'] for item in new_visible_data]
        
        if current_data_ids != new_data_ids:
            self.rebuild_list(new_visible_data)
        else:
            self.visible_items_data = new_visible_data
            self.update_row_contents(new_visible_data)
            
        return task.again

    def update_row_contents(self, new_data):
        data_map = {item['id']: item for item in new_data}
        for row in self.scroll_list['items']:
            item_id = row.item_data['id']
            if item_id in data_map:
                row.update_content(data_map[item_id])

    def sort_by_column(self, column_key):
        if self.sort_key == column_key:
            self.sort_order = 'DESC' if self.sort_order == 'ASC' else 'ASC'
        else:
            self.sort_key = column_key
            self.sort_order = 'ASC'
        self.rebuild_list()

    def _filter_and_sort(self, data):
        filtered = []
        for item in data:
            if not self.type_filters.get(item['type'], True):
                continue

            state_match = False
            state_active = any(self.state_filters.values())
            
            if not state_active:
                state_match = True
            else:
                for state, is_active in self.state_filters.items():
                    if is_active and state in item['flags']:
                        state_match = True
                        break
            if state_match:
                filtered.append(item)
                
        reverse = self.sort_order == 'DESC'
        key = self.sort_key
        sorted_data = sorted(filtered, key=lambda x: x.get(key, 0) if key in ('distance', 'velocity', 'angular') else str(x.get(key, '')), reverse=reverse)
        return sorted_data

    def rebuild_list(self, new_data=None):
        if new_data is None:
            new_data = self._filter_and_sort(self.all_items_data)
        self.visible_items_data = new_data
        self.scroll_list.removeAndDestroyAllItems()
        for item_data in self.visible_items_data:
            row = self.make_row_item(item_data, self.row_command)
            if self.selected_item_id == item_data['id']:
                row.set_selected(True)
            self.scroll_list.addItem(row)
        self.scroll_list.refresh()

    def set_selected(self, item_id):
        for row in self.scroll_list['items']:
            if row.item_data['id'] == self.selected_item_id and row.item_data['id'] != item_id:
                row.set_selected(False)
                break
        self.selected_item_id = item_id
        for row in self.scroll_list['items']:
            if row.item_data['id'] == self.selected_item_id:
                row.set_selected(True)
                break

    def toggle_type_filter(self, f_type, state):
        self.type_filters[f_type] = state
        self.rebuild_list()
        
    def toggle_state_filter(self, f_state, state):
        self.state_filters[f_state] = state
        self.rebuild_list()
        
    def show_context_menu(self, item_data, event):
        if self.context_menu:
            self.context_menu.destroy()
        
        options = [
            ("Célzárolás", lambda: print(f"-> Command: Lock Target on {item_data['name']}")),
            ("Megközelítés", lambda: print(f"-> Command: Approach {item_data['name']}")),
            ("Keringés", lambda: print(f"-> Command: Orbit {item_data['name']}")),
            ("Távolmaradás (10km)", lambda: print(f"-> Command: Keep at Range on {item_data['name']}")),
            ("Ugrás ide", lambda: print(f"-> Command: Warp To {item_data['name']}"))
        ]
        
        menu_width = 0.35
        menu_item_height = 0.05
        menu_height = len(options) * menu_item_height
        
        self.context_menu = DirectFrame(
            parent=self.base.a2dTopLeft,
            frameColor=OVERVIEW_BG * 1.5,
            frameSize=(0, menu_width, -menu_height, 0),
            relief=DGG.FLAT,
            sortOrder=100
        )
        
        if self.base.mouseWatcherNode.hasMouse():
            x = self.base.mouseWatcherNode.getMouseX()
            y = self.base.mouseWatcherNode.getMouseY()
            self.context_menu.setPos(x - self.base.a2dTopLeft.getX(), 0, y - self.base.a2dTopLeft.getZ()) 

        for i, (text, cmd) in enumerate(options):
            DirectButton(
                parent=self.context_menu,
                text=text,
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=0.03,
                text_align=TextNode.ALeft,
                frameColor=OVERVIEW_BG * 1.5,
                relief=DGG.FLAT,
                rolloverSound=None,
                clickSound=None,
                frameSize=(0, menu_width, -menu_item_height/2, menu_item_height/2),
                pos=(0, 0, -i * menu_item_height - menu_item_height/2),
                command=lambda c=cmd: [c(), self.destroy_context_menu()]
            )
            
        self.base.acceptOnce('mouse1', self.destroy_context_menu)
        
    def destroy_context_menu(self):
        self.base.ignore('mouse1')
        if self.context_menu:
            self.context_menu.destroy()
            self.context_menu = None
            
    def destroy(self):
        self.base.taskMgr.remove("OverviewUpdateTask")
        if self.main_frame:
            self.main_frame.destroy()
        self.destroy_context_menu()