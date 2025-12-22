from direct.gui.DirectGui import DirectFrame, DirectWaitBar, DirectLabel, DGG
from panda3d.core import TextNode
from .UITheme.Theme import UITheme

class ShipHUD:
    def __init__(self, base, ship_data):
        self.base = base
        self.ship = ship_data
        
        self.container = DirectFrame(
            frameColor=(0, 0, 0, 0),
            pos=(0.1, 0, 0.15),
            parent=self.base.a2dBottomLeft
        )

        self.shield_bar = self._create_bar("SHIELD", UITheme.HUD_SHIELD, 0.15)
        self.armor_bar = self._create_bar("ARMOR", UITheme.HUD_ARMOR, 0.10)
        self.hull_bar = self._create_bar("HULL", UITheme.HUD_HULL, 0.05)

    def _create_bar(self, label, color, z):
        bar = DirectWaitBar(
            parent=self.container, range=100, value=100,
            pos=(UITheme.BAR_WIDTH/2, 0, z),
            frameSize=(-UITheme.BAR_WIDTH/2, UITheme.BAR_WIDTH/2, -UITheme.BAR_HEIGHT/2, UITheme.BAR_HEIGHT/2),
            barColor=color, frameColor=UITheme.HUD_BG, relief=DGG.FLAT
        )
        DirectLabel(parent=bar, text=label, text_scale=0.02, pos=(-UITheme.BAR_WIDTH/2 + 0.01, 0, -0.005), 
                    text_fg=(1,1,1,1), frameColor=(0,0,0,0), text_align=TextNode.ALeft)
        return bar

    def update(self):
        if not self.ship: return
        self.shield_bar['value'] = getattr(self.ship, 'current_shield', 100)
        self.armor_bar['value'] = getattr(self.ship, 'current_armor', 100)
        self.hull_bar['value'] = getattr(self.ship, 'current_hull', 100)