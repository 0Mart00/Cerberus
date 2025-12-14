from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVector4 as LColor, TextNode

# Feltételezzük, hogy az alábbi modulok elérhetők, és tartalmazzák a szükséges osztályokat/konstansokat
from ui.overview_panel import OverviewPanel
from data.overview_item import OverviewManager 

# UI Konstansok (ezeket valahol globálisan kellene definiálni)
HUD_BG_COLOR = LColor(0.1, 0.1, 0.2, 0.8)
HUD_TEXT_COLOR = LColor(0.8, 0.8, 1.0, 1.0)
BUTTON_BG_COLOR = LColor(0.3, 0.3, 0.4, 1.0)
BUTTON_ACTIVE_COLOR = LColor(0.4, 0.4, 0.6, 1.0)
CLOSE_BTN_COLOR = LColor(0.8, 0.2, 0.2, 1.0) # Piros szín a bezáráshoz
CLOSE_BTN_SIZE = 0.05 # Kicsi gomb méret (a kérésnek megfelelően)


class HUD:
    """
    A Cerberus játék interfésze. Ide integráljuk az Overview Panelt és a navigációs gombokat.
    """
    def __init__(self, base):
        self.base = base
        
        # 1. Initialize the Overview Data Manager
        self.overview_manager = OverviewManager(num_entities=30) 
        
        # 2. Initialize the EVE-like Overview Panel
        # Ezt a panelt balra kell helyezni, a gombok felette lesznek.
        self.overview_panel = OverviewPanel(base, self.overview_manager)
        
        # Játékállapot: Melyik fül van kiválasztva
        self.active_tab = "Overview" 

        self.setup_ui_elements()

        # Hozzáadhatunk egy kapcsolót (például F11) a HUD elrejtésére/megjelenítésére
        self.base.accept('f11', self.toggle_visibility)
        
        # Inicializálás: Alapértelmezetten az OverviewPanel látható
        self.show_tab(self.active_tab) 

    def setup_ui_elements(self):
        """Létrehozza a fő HUD navigációs gombokat, kereteket és a bezáró gombot."""
        
        # A fő gombok helye. Az OverviewPanel a self.base.aspect2d-hez van csatolva, 
        # ezért a gomboknak is oda kell csatlakozniuk, a panel teteje fölé.
        
        # Gombok szélessége és magassága normalizált koordinátákban
        TAB_WIDTH = 0.2
        TAB_HEIGHT = 0.07
        
        # Az Overview Panel pozíciója (bal oldalon)
        # Az overview_panel.py-ban a PANEL_WIDTH = sum(COLUMN_WIDTHS) + 0.02
        panel_width_val = self.overview_panel.main_frame['frameSize'][1] 
        
        # A gombok y pozíciója (a panel teteje fölött)
        # A panel teteje: PANEL_HEIGHT/2 + 0.02 (kb. 0.72)
        panel_top_y = self.overview_panel.main_frame['pos'][2] + self.overview_panel.main_frame['frameSize'][3] 
        tab_y_pos = panel_top_y + TAB_HEIGHT / 2 + 0.01 

        # A gombok x pozíciója (a panel bal széléhez igazítva)
        x_start = self.overview_panel.main_frame['pos'][0] - panel_width_val / 2 + TAB_WIDTH / 2

        self.tab_buttons = {}

        tabs = [
            ("Overview", self.overview_panel.main_frame),
            ("Inventory", None), # Ide fog kerülni a külön ablak
            ("Market", None)     # Ide fog kerülni a külön ablak
        ]
        
        # -----------------------------------------------------
        # Létrehozzuk az Inventory és MARKET kereteket (egyszerű DirectFrame-ek)
        # A valóságban ezek külön DirectWindow objektumok lennének, de most egyszerűsítünk.
        self.inventory_frame = DirectFrame(
            parent=self.base.aspect2d,
            frameColor=HUD_BG_COLOR,
            frameSize=(-panel_width_val/2, panel_width_val/2, -0.6, 0.6),
            pos=self.overview_panel.main_frame['pos'],
            text="Inventory Window Content (WIP)",
            text_fg=HUD_TEXT_COLOR,
            text_scale=0.04,
            text_pos=(0, 0),
            relief=DGG.FLAT
        )
        self.market_frame = DirectFrame(
            parent=self.base.aspect2d,
            frameColor=HUD_BG_COLOR,
            frameSize=(-panel_width_val/2, panel_width_val/2, -0.6, 0.6),
            pos=self.overview_panel.main_frame['pos'],
            text="Marketplace Window Content (WIP)",
            text_fg=HUD_TEXT_COLOR,
            text_scale=0.04,
            text_pos=(0, 0),
            relief=DGG.FLAT
        )
        self.tab_frames = {
            "Overview": self.overview_panel.main_frame,
            "Inventory": self.inventory_frame,
            "MARKET": self.market_frame
        }
        # -----------------------------------------------------

        current_x = x_start
        for name, _ in tabs:
            btn = DirectButton(
                parent=self.base.aspect2d,
                text=name,
                text_fg=HUD_TEXT_COLOR,
                text_scale=0.03,
                frameColor=BUTTON_BG_COLOR,
                relief=DGG.FLAT,
                frameSize=(-TAB_WIDTH/2, TAB_WIDTH/2, -TAB_HEIGHT/2, TAB_HEIGHT/2),
                pos=(current_x, 0, tab_y_pos),
                command=self.show_tab,
                extraArgs=[name]
            )
            self.tab_buttons[name] = btn
            current_x += TAB_WIDTH
            
        # --- BEZÁRÓ GOMB (X) ---
        # A gombot az Overview Panel fő keretére tesszük, a jobb felső sarokba.
        # A frameSize[1] adja meg a keret szélességét (X max).
        # A frameSize[3] adja meg a keret magasságát (Z max).
        frame_x_max = self.overview_panel.main_frame['frameSize'][1]
        frame_z_max = self.overview_panel.main_frame['frameSize'][3]
        
        # Pozíció a main_frame lokális koordinátáiban
        close_x = frame_x_max - CLOSE_BTN_SIZE / 2 - 0.01 
        close_z = frame_z_max - CLOSE_BTN_SIZE / 2 - 0.01

        self.close_button = DirectButton( # <-- A bezáró gomb a 144. sorban kerül definiálásra
            parent=self.overview_panel.main_frame,
            text="X",
            text_fg=HUD_TEXT_COLOR,
            text_scale=0.03,
            frameColor=CLOSE_BTN_COLOR, # Piros háttér
            relief=DGG.FLAT,
            frameSize=(-CLOSE_BTN_SIZE/2, CLOSE_BTN_SIZE/2, -CLOSE_BTN_SIZE/2, CLOSE_BTN_SIZE/2),
            pos=(close_x, 0, close_z),
            command=self.hide # A teljes HUD elrejtése
        )
        # --- BEZÁRÓ GOMB VÉGE ---

    def show_tab(self, tab_name):
        """Vált a navigációs lapok között."""
        self.active_tab = tab_name
        
        # 1. Gombok stílusának frissítése
        for name, button in self.tab_buttons.items():
            if name == tab_name:
                button['frameColor'] = BUTTON_ACTIVE_COLOR
                button['state'] = DGG.DISABLED # Inaktívvá tesszük a gombot
            else:
                button['frameColor'] = BUTTON_BG_COLOR
                button['state'] = DGG.NORMAL
                
        # 2. Keretek láthatóságának frissítése
        for name, frame in self.tab_frames.items():
            if name == tab_name:
                frame.show()
                # A bezáró gombot csak a fő OverviewFrame-en kell mutatni
                self.close_button.show()
            else:
                frame.hide()
        
        # Ha nem az Overview aktív, de az Overview panel láthatósága más,
        # biztosítjuk, hogy a gomb is láthatatlan legyen (csak az OverviewPanel szülője).
        if tab_name != "Overview":
            self.close_button.hide()
            

    def toggle_visibility(self):
        """Toggles the visibility of the HUD elements."""
        is_hidden = self.tab_frames[self.active_tab].isHidden()
        
        if is_hidden:
            self.show()
        else:
            self.hide()

    def show(self):
        """Shows the HUD components."""
        for frame in self.tab_frames.values():
             # Csak az aktív keretet kell megmutatni
             if frame == self.tab_frames[self.active_tab]:
                 frame.show()
             
        for button in self.tab_buttons.values():
            button.show()
            
        # A bezáró gombot is meg kell mutatni, ha az Overview a kiválasztott fül
        if self.active_tab == "Overview":
            self.close_button.show()


    def hide(self):
        """Hides the HUD components."""
        for frame in self.tab_frames.values():
            frame.hide()
        for button in self.tab_buttons.values():
            button.hide()
        
        # A bezáró gombot is el kell rejteni
        self.close_button.hide()


    def destroy(self):
        """Clean up all HUD elements."""
        self.overview_panel.destroy()
        self.inventory_frame.destroy()
        self.market_frame.destroy()
        self.close_button.destroy() # A bezáró gomb tisztítása
        for button in self.tab_buttons.values():
            button.destroy()