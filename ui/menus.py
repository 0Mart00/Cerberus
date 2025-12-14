from direct.gui.DirectGui import DirectFrame, DirectButton, DirectEntry, DirectLabel, DGG
from panda3d.core import LVector4 as LColor

# UI Style Constants
MENU_BG_COLOR = LColor(0.1, 0.1, 0.2, 0.8)
BUTTON_COLOR = LColor(0.2, 0.4, 0.6, 1.0)
TEXT_COLOR = LColor(0.8, 0.9, 1.0, 1.0)
HIGHLIGHT_COLOR = LColor(0.4, 0.6, 0.8, 1.0)

class MainMenu:
    def __init__(self, base):
        self.base = base
        self.host_window = None
        self.setup_main_menu()

    def setup_main_menu(self):
        """Főmenü létrehozása."""
        self.frame = DirectFrame(
            frameColor=MENU_BG_COLOR,
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        
        DirectLabel(
            parent=self.frame,
            text="CERBERUS ONLINE",
            text_scale=0.15,
            text_fg=TEXT_COLOR,
            pos=(0, 0, 0.5)
        )
        
        y_offset = 0.2
        button_width = 0.4
        button_height = 0.1
        
        # Host Game Button
        DirectButton(
            parent=self.frame,
            text="Játék Hosztolása",
            text_scale=0.07,
            text_fg=TEXT_COLOR,
            frameColor=BUTTON_COLOR,
            relief=DGG.FLAT,
            frameSize=(-button_width, button_width, -button_height, button_height),
            command=self.show_host_window,
            pos=(0, 0, y_offset)
        )
        
        # Join Game Button
        DirectButton(
            parent=self.frame,
            text="Csatlakozás",
            text_scale=0.07,
            text_fg=TEXT_COLOR,
            frameColor=BUTTON_COLOR,
            relief=DGG.FLAT,
            frameSize=(-button_width, button_width, -button_height, button_height),
            command=self.show_join_window,
            pos=(0, 0, y_offset - 0.25)
        )
        
        # Exit Button
        DirectButton(
            parent=self.frame,
            text="Kilépés",
            text_scale=0.07,
            text_fg=TEXT_COLOR,
            frameColor=BUTTON_COLOR,
            relief=DGG.FLAT,
            frameSize=(-button_width, button_width, -button_height, button_height),
            command=self.base.userExit,
            pos=(0, 0, y_offset - 0.5)
        )

    def show_host_window(self):
        """Host ablak megjelenítése."""
        if self.host_window:
            self.host_window.destroy()
            
        self.host_window = DirectFrame(
            frameColor=MENU_BG_COLOR * 1.2,
            frameSize=(-0.4, 0.4, -0.2, 0.2),
            pos=(0, 0, 0),
            parent=self.base.aspect2d,
            relief=DGG.FLAT
        )
        
        DirectLabel(
            parent=self.host_window,
            text="Szerver indítása?",
            text_scale=0.08,
            text_fg=TEXT_COLOR,
            pos=(0, 0, 0.1)
        )
        
        # Start Host Button
        DirectButton(
            parent=self.host_window,
            text="Start Host",
            text_scale=0.06,
            text_fg=TEXT_COLOR,
            frameColor=BUTTON_COLOR,
            relief=DGG.FLAT,
            frameSize=(-0.15, 0.15, -0.05, 0.05),
            command=self.start_host_and_close_window, # ÚJ PARANCS
            pos=(-0.15, 0, -0.1)
        )
        
        # Cancel Button
        DirectButton(
            parent=self.host_window,
            text="Mégse",
            text_scale=0.06,
            text_fg=TEXT_COLOR,
            frameColor=BUTTON_COLOR,
            relief=DGG.FLAT,
            frameSize=(-0.15, 0.15, -0.05, 0.05),
            command=self.host_window.destroy,
            pos=(0.15, 0, -0.1)
        )

    def start_host_and_close_window(self):
        """Szerver indítása és Host ablak bezárása."""
        # A start_host metódus a CerberusGame-ben van.
        if self.base.start_host():
            # Ha a hosztolás sikeresen elindult, bezárjuk az ablakot.
            if self.host_window:
                self.host_window.destroy()
                self.host_window = None


    def show_join_window(self):
        """Csatlakozás ablak megjelenítése."""
        # Meglévő join_window logikája...
        pass # A többi logika megtartva

    def hide(self):
        self.frame.hide()

    def show(self):
        self.frame.show()