from panda3d.core import LVector4 as LColor
from direct.gui.DirectGui import DGG

class UITheme:
    # --- Ablak és Panelek színei ---
    WINDOW_BG_COLOR = LColor(0.05, 0.05, 0.05, 0.95)
    MENU_BG_COLOR = LColor(0.1, 0.1, 0.2, 0.8)
    ROW_BG_COLOR = LColor(0.12, 0.12, 0.15, 0.8)
    MAP_BG_COLOR = LColor(0.02, 0.02, 0.05, 0.98) # Nagyon sötét űr kék
    
    # --- Gomb alapszínek ---
    BUTTON_NORMAL = LColor(0.2, 0.4, 0.6, 1.0)
    BUTTON_PRESSED = LColor(0.5, 0.7, 1.0, 1.0)
    BUTTON_ROLLOVER = LColor(0.4, 0.6, 0.8, 1.0)
    BUTTON_DISABLED = LColor(0.1, 0.1, 0.1, 1.0)
    
    # Állapot-tuple a DirectGui-nak
    BUTTON_COLORS = (BUTTON_NORMAL, BUTTON_PRESSED, BUTTON_ROLLOVER, BUTTON_DISABLED)
    
    # --- Térkép specifikus csomópont színek ---
    MAP_NODE_CURRENT = LColor(0, 0.8, 0, 1)    # Zöld: Itt vagy
    MAP_NODE_NEIGHBOR = LColor(0, 0.4, 0.8, 1) # Kék: Elérhető (szomszéd)
    MAP_NODE_DISTANT = LColor(0.2, 0.2, 0.2, 1)  # Sötétszürke: Távoli
    
    # --- Szöveg színek ---
    TEXT_COLOR = LColor(0.9, 0.9, 0.9, 1.0)
    ISK_COLOR = LColor(1, 0.8, 0, 1)      
    WALLET_COLOR = LColor(0, 1, 1, 1)    
    CAT_MODULE_COLOR = LColor(0.5, 0.5, 1, 1)
    
    # --- Skálák és méretek ---
    TITLE_SCALE = 0.15
    LABEL_SCALE = 0.08
    BUTTON_TEXT_SCALE = 0.07
    SMALL_BUTTON_SCALE = 0.045
    SCROLL_STEP = 0.1

    @staticmethod
    def get_button_style():
        """Visszaadja az alapértelmezett gomb stílus szótárat."""
        return {
            "frameColor": UITheme.BUTTON_COLORS,
            "relief": DGG.FLAT,
            "text_fg": UITheme.TEXT_COLOR,
            "text_scale": UITheme.BUTTON_TEXT_SCALE,
        }

    @staticmethod
    def get_close_btn_style():
        """Speciális pirosas stílus a bezáró gombokhoz."""
        style = UITheme.get_button_style()
        style["frameColor"] = (
            LColor(0.5, 0, 0, 1), 
            LColor(0.8, 0.2, 0.2, 1), 
            LColor(0.7, 0, 0, 1), 
            UITheme.BUTTON_DISABLED
        )
        return style