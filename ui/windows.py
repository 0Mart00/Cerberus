from direct.gui.DirectGui import *
from panda3d.core import TextNode, LVector4
from UITheme.Theme import UITheme

# ==============================================================================
# INVENTORY ITEM DATA
# ==============================================================================
class InventoryItem:
    def __init__(self, name, category, quantity=1, base_price=0):
        self.name = name
        self.category = category
        self.quantity = quantity
        self.base_price = base_price

# ==============================================================================
# WINDOW MANAGER (Inventory & Market)
# ==============================================================================
class WindowManager:
    def __init__(self, game):
        self.game = game
        self.inventory = {} 
        self.credits = 100000.0
        
        self.windows = {}
        self.active_scroll_frame = None

        # Alapértelmezett tárgyak feltöltése
        self.add_item("Tritanium", "RawMaterial", 5000, 5)
        self.add_item("Pyerite", "RawMaterial", 1200, 12)
        self.add_item("Impulse Laser I", "Module", 2, 45000)
        self.add_item("125mm Railgun", "Module", 1, 32000)

        # Market adatbázis (Példa adatok)
        self.market_data = [
            InventoryItem("Civillian Gatling Laser", "Weapon", 999, 1200),
            InventoryItem("Small Shield Booster", "Module", 50, 45000),
            InventoryItem("Veldspar", "RawMaterial", 100000, 15),
        ]

    def add_item(self, name, category, qty, price=0):
        if name in self.inventory:
            self.inventory[name].quantity += qty
        else:
            self.inventory[name] = InventoryItem(name, category, qty, price)
        
        if "inventory" in self.windows and not self.windows["inventory"].isHidden():
            self.refresh_inventory_ui()

    # --------------------------------------------------------------------------
    # SCROLL LOGIC
    # --------------------------------------------------------------------------
    def _scroll_frame_enter(self, scroll_frame, event):
        self.active_scroll_frame = scroll_frame
        self.game.accept("wheel_up", self.scroll_up)
        self.game.accept("wheel_down", self.scroll_down)

    def _scroll_frame_exit(self, scroll_frame, event):
        if self.active_scroll_frame == scroll_frame:
            self.active_scroll_frame = None
            self.game.ignore("wheel_up")
            self.game.ignore("wheel_down")

    def scroll_up(self):
        if self.active_scroll_frame:
            val = self.active_scroll_frame['verticalScroll']['value']
            self.active_scroll_frame['verticalScroll']['value'] = max(0, val - UITheme.SCROLL_STEP)

    def scroll_down(self):
        if self.active_scroll_frame:
            val = self.active_scroll_frame['verticalScroll']['value']
            self.active_scroll_frame['verticalScroll']['value'] = min(1, val + UITheme.SCROLL_STEP)

    # --------------------------------------------------------------------------
    # INVENTORY UI
    # --------------------------------------------------------------------------
    def toggle_inventory(self):
        if "inventory" not in self.windows: self.create_inventory_window()
        if self.windows["inventory"].isHidden():
            self.windows["inventory"].show()
            self.refresh_inventory_ui()
        else:
            self.windows["inventory"].hide()

    def create_inventory_window(self):
        frame = DirectFrame(
            frameColor=UITheme.WINDOW_BG_COLOR,
            frameSize=(-0.5, 0.5, -0.6, 0.6),
            pos=(-0.8, 0, 0.2),
            parent=self.game.aspect2d,
            state=DGG.NORMAL
        )
        self.windows["inventory"] = frame
        
        DirectLabel(parent=frame, text="CARGO", text_scale=UITheme.TITLE_SCALE, 
                    pos=(0, 0, 0.52), text_fg=UITheme.TEXT_COLOR, frameColor=(0,0,0,0))
        
        btn_style = UITheme.get_button_style()
        DirectButton(parent=frame, text="X", pos=(0.45, 0, 0.53), scale=0.8,
                    command=frame.hide, **btn_style)

        self.inv_scroll = DirectScrolledFrame(
            parent=frame, frameSize=(-0.45, 0.45, -0.55, 0.45),
            canvasSize=(-0.4, 0.4, -1, 0), frameColor=(0,0,0,0.2),
            manageScrollBars=True, autoHideScrollBars=True
        )
        self.inv_scroll.bind(DGG.ENTER, self._scroll_frame_enter, [self.inv_scroll])
        self.inv_scroll.bind(DGG.EXIT, self._scroll_frame_exit, [self.inv_scroll])

    def refresh_inventory_ui(self):
        canvas = self.inv_scroll.getCanvas()
        for child in canvas.getChildren(): child.removeNode()
            
        y_pos = -0.05
        for item in sorted(self.inventory.values(), key=lambda x: x.category):
            row = DirectFrame(parent=canvas, frameColor=UITheme.ROW_BG_COLOR,
                              frameSize=(-0.4, 0.4, -0.07, 0.01), pos=(0, 0, y_pos))
            
            # Category alapú színezés
            color = UITheme.CAT_MODULE_COLOR if item.category == "Module" else UITheme.TEXT_COLOR
            
            DirectLabel(parent=row, text=item.name, text_scale=UITheme.LABEL_SCALE,
                        text_align=TextNode.ALeft, pos=(-0.38, 0, -0.04), 
                        text_fg=color, frameColor=(0,0,0,0))
            
            qty_str = "{:,}".format(item.quantity).replace(",", " ")
            DirectLabel(parent=row, text=qty_str, text_scale=UITheme.LABEL_SCALE,
                        text_align=TextNode.ARight, pos=(0.38, 0, -0.04), 
                        text_fg=UITheme.ISK_COLOR, frameColor=(0,0,0,0))
            y_pos -= 0.08

        self.inv_scroll['canvasSize'] = (-0.4, 0.4, y_pos, 0)

    # --------------------------------------------------------------------------
    # MARKET UI
    # --------------------------------------------------------------------------
    def toggle_market(self):
        if "market" not in self.windows: self.create_market_window()
        if self.windows["market"].isHidden():
            self.windows["market"].show()
            self.refresh_market_ui()
        else:
            self.windows["market"].hide()

    def create_market_window(self):
        frame = DirectFrame(frameColor=UITheme.WINDOW_BG_COLOR,
                            frameSize=(-0.6, 0.6, -0.7, 0.7),
                            pos=(0, 0, 0), parent=self.game.aspect2d, state=DGG.NORMAL)
        self.windows["market"] = frame
        
        self.lbl_wallet = DirectLabel(parent=frame, text="", scale=UITheme.LABEL_SCALE,
                                      pos=(-0.55, 0, 0.65), text_align=TextNode.ALeft, 
                                      text_fg=UITheme.WALLET_COLOR, frameColor=(0,0,0,0))
        
        btn_style = UITheme.get_button_style()
        DirectButton(parent=frame, text="Close", pos=(0.45, 0, 0.65), 
                     command=frame.hide, **btn_style)

        self.mkt_scroll = DirectScrolledFrame(
            parent=frame, frameSize=(-0.55, 0.55, -0.6, 0.55),
            canvasSize=(-0.5, 0.5, -1, 0), frameColor=(0,0,0,0.2)
        )
        self.mkt_scroll.bind(DGG.ENTER, self._scroll_frame_enter, [self.mkt_scroll])
        self.mkt_scroll.bind(DGG.EXIT, self._scroll_frame_exit, [self.mkt_scroll])

    def buy_item(self, item):
        if self.credits >= item.base_price:
            self.credits -= item.base_price
            self.add_item(item.name, item.category, 1, item.base_price)
            self.refresh_market_ui()
        else:
            print("Nincs elég ISK!")

    def refresh_market_ui(self):
        self.lbl_wallet['text'] = f"Wallet: {self.credits:,.0f} ISK".replace(",", " ")
        canvas = self.mkt_scroll.getCanvas()
        for child in canvas.getChildren(): child.removeNode()

        y_pos = -0.05
        btn_style = UITheme.get_button_style()
        for item in self.market_data:
            row = DirectFrame(parent=canvas, frameColor=UITheme.ROW_BG_COLOR,
                              frameSize=(-0.5, 0.5, -0.09, 0.01), pos=(0, 0, y_pos))
            
            DirectLabel(parent=row, text=item.name, scale=UITheme.LABEL_SCALE,
                        pos=(-0.48, 0, -0.05), text_align=TextNode.ALeft,
                        text_fg=UITheme.TEXT_COLOR, frameColor=(0,0,0,0))
            
            price_str = f"{item.base_price:,.0f}"
            DirectLabel(parent=row, text=price_str, scale=UITheme.LABEL_SCALE,
                        pos=(0.2, 0, -0.05), text_align=TextNode.ARight,
                        text_fg=UITheme.ISK_COLOR, frameColor=(0,0,0,0))
            
            DirectButton(parent=row, text="BUY", pos=(0.38, 0, -0.05),
                         command=self.buy_item, extraArgs=[item], **btn_style)
            y_pos -= 0.1

        self.mkt_scroll['canvasSize'] = (-0.5, 0.5, y_pos, 0)