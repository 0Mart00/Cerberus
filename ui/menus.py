from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from .UITheme.Theme import UITheme  # Importáljuk az új témát

class MainMenu:
    def __init__(self, base):
        self.base = base
        self.host_window = None
        self.frame = None
        self.setup_main_menu()

    def setup_main_menu(self):
        """Főmenü létrehozása a téma alapján."""
        self.frame = DirectFrame(
            frameColor=UITheme.MENU_BG_COLOR,
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        
        DirectLabel(
            parent=self.frame,
            text="CERBERUS ONLINE",
            text_scale=UITheme.TITLE_SCALE,
            text_fg=UITheme.TEXT_COLOR,
            pos=(0, 0, 0.5),
            frameColor=(0,0,0,0) # Átlátszó háttér a szövegnek
        )
        
        # Gombok létrehozása a téma stílusával
        btn_style = UITheme.get_button_style()
        y_offset = 0.2
        
        DirectButton(parent=self.frame,
            text="Játék Hosztolása",
            command=self.show_host_window,
            pos=(0, 0, y_offset),
            frameSize=(-0.4, 0.4, -0.1, 0.1),
            **btn_style # Kicsomagoljuk a stílus szótárt
        )
        
        DirectButton(
            parent=self.frame,
            text="Csatlakozás",
            command=self.show_join_window,
            pos=(0, 0, y_offset - 0.25),
            frameSize=(-0.4, 0.4, -0.1, 0.1),
            **btn_style
        )
        
        DirectButton(
            parent=self.frame,
            text="Kilépés",
            command=self.base.userExit,
            pos=(0, 0, y_offset - 0.5),
            frameSize=(-0.4, 0.4, -0.1, 0.1),
            **btn_style
        )

    def show_host_window(self):
        """Host ablak megjelenítése a téma színeivel."""
        if self.host_window:
            self.host_window.destroy()
            
        self.host_window = DirectFrame(
            frameColor=UITheme.WINDOW_BG_COLOR,
            frameSize=(-0.4, 0.4, -0.2, 0.2),
            pos=(0, 0, 0),
            parent=self.base.aspect2d,
            relief=DGG.FLAT
        )
        
        DirectLabel(
            parent=self.host_window,
            text="Szerver indítása?",
            text_scale=UITheme.LABEL_SCALE,
            text_fg=UITheme.TEXT_COLOR,
            pos=(0, 0, 0.1),
            frameColor=(0,0,0,0)
        )
        
        btn_style = UITheme.get_button_style()
        # Kisebb szöveg a felugró ablakhoz
        btn_style["text_scale"] = UITheme.SMALL_BUTTON_SCALE

        DirectButton(
            parent=self.host_window,
            text="Start Host",
            command=self.start_host_and_close_window,
            pos=(-0.15, 0, -0.1),
            frameSize=(-0.15, 0.15, -0.05, 0.05),
            **btn_style
        )
        
        DirectButton(
            parent=self.host_window,
            text="Mégse",
            command=self.host_window.destroy,
            pos=(0.15, 0, -0.1),
            frameSize=(-0.15, 0.15, -0.05, 0.05),
            **btn_style
        )

    def start_host_and_close_window(self):
        if hasattr(self.base, 'start_host') and self.base.start_host():
            if self.host_window:
                self.host_window.destroy()
                self.host_window = None

    def show_join_window(self):
        pass

    def hide(self):
        if self.frame: self.frame.hide()

    def show(self):
        if self.frame: self.frame.show()