from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3, Vec4
from direct.task import Task # Needed for event handling related to ShowBase (game.accept/ignore)

# ==============================================================================
# INVENTORY ITEM DATA
# ==============================================================================
class InventoryItem:
    def __init__(self, name, category, quantity=1, base_price=0):
        self.name = name
        self.category = category
        self.quantity = quantity
        self.base_price = base_price # Estimated price

# ==============================================================================
# WINDOW MANAGER (Inventory & Market)
# ==============================================================================
class WindowManager:
    def __init__(self, game):
        self.game = game
        self.inventory = {} # {item_name: InventoryItem} - Dict for stacking
        self.credits = 100000.0 # Starting capital (ISK/Credits)
        
        # UI Elements containers
        self.windows = {}
        self.inv_scroll_frame = None
        self.market_scroll_frame = None
        
        # Scrolling management
        self.active_scroll_frame = None # Tracks the currently hovered DirectScrolledFrame
        self.SCROLL_STEP = 0.1 # Scroll amount per wheel click

        # Starting equipment
        self.add_item("Tritanium", "RawMaterial", 5000, 5)
        self.add_item("Pyerite", "RawMaterial", 1200, 12)
        self.add_item("Impulse Laser I", "Module", 2, 45000)
        self.add_item("125mm Railgun", "Module", 1, 32000)
        self.add_item("Iron Charge S", "Ammo", 1000, 2)

        # Styles
        self.win_color = (0.05, 0.05, 0.05, 0.95) # EVE-like dark background
        self.border_color = (0.4, 0.4, 0.4, 1)

    def add_item(self, name, category, qty, price=0):
        """Infinite stacking logic"""
        if name in self.inventory:
            self.inventory[name].quantity += qty
        else:
            self.inventory[name] = InventoryItem(name, category, qty, price)
        
        # If the inventory is open, refresh it
        if "inventory" in self.windows and not self.windows["inventory"].isHidden():
            self.refresh_inventory_ui()

    def remove_item(self, name, qty):
        if name in self.inventory:
            if self.inventory[name].quantity >= qty:
                self.inventory[name].quantity -= qty
                if self.inventory[name].quantity <= 0:
                    del self.inventory[name]
                return True
        return False

    # --------------------------------------------------------------------------
    # SCROLLING IMPLEMENTATION (Fix for mouse wheel hijacking)
    # --------------------------------------------------------------------------
    def _scroll_frame_enter(self, scroll_frame, event):
        """Binds mouse wheel events to the given scroll frame."""
        self.active_scroll_frame = scroll_frame
        
        # Disable game camera zoom controls (must be handled by the game core/ship)
        if self.game.local_ship:
            self.game.local_ship.ignore("wheel_up")
            self.game.local_ship.ignore("wheel_down")
        
        # Bind scrolling to this manager's methods
        self.game.accept("wheel_up", self.scroll_up)
        self.game.accept("wheel_down", self.scroll_down)

    def _scroll_frame_exit(self, scroll_frame, event):
        """Unbinds mouse wheel events."""
        if self.active_scroll_frame == scroll_frame:
            self.active_scroll_frame = None
            
            self.game.ignore("wheel_up")
            self.game.ignore("wheel_down")
            
            # Re-enable game camera zoom controls
            if self.game.local_ship:
                # Assuming Ship class has adjust_zoom defined
                self.game.local_ship.accept("wheel_up", self.game.local_ship.adjust_zoom, [-5.0])
                self.game.local_ship.accept("wheel_down", self.game.local_ship.adjust_zoom, [5.0])

    def scroll_up(self):
        """Scrolls the active frame up."""
        if self.active_scroll_frame and 'verticalScroll' in self.active_scroll_frame:
            current_value = self.active_scroll_frame['verticalScroll']['value']
            new_value = max(0.0, current_value - self.SCROLL_STEP)
            self.active_scroll_frame['verticalScroll']['value'] = new_value

    def scroll_down(self):
        """Scrolls the active frame down."""
        if self.active_scroll_frame and 'verticalScroll' in self.active_scroll_frame:
            current_value = self.active_scroll_frame['verticalScroll']['value']
            new_value = min(1.0, current_value + self.SCROLL_STEP)
            self.active_scroll_frame['verticalScroll']['value'] = new_value

    # --------------------------------------------------------------------------
    # UI CREATION - INVENTORY
    # --------------------------------------------------------------------------
    def toggle_inventory(self):
        if "inventory" not in self.windows:
            self.create_inventory_window()
        
        if self.windows["inventory"].isHidden():
            self.windows["inventory"].show()
            self.refresh_inventory_ui()
        else:
            self.windows["inventory"].hide()

    def create_inventory_window(self):
        # Main window frame
        frame = DirectFrame(
            frameColor=self.win_color,
            frameSize=(-0.5, 0.5, -0.6, 0.6),
            pos=(-0.8, 0, 0.2), # Shifted to the left side
            state=DGG.NORMAL # To make it clickable and prevent mouse pass-through
        )
        self.windows["inventory"] = frame
        
        # Header
        DirectLabel(
            parent=frame, text="CARGO (Inventory)", text_scale=0.06, 
            pos=(0, 0, 0.52), text_fg=(1, 1, 1, 1), frameColor=(0,0,0,0)
        )
        DirectButton(
            parent=frame, text="X", scale=0.05, pos=(0.45, 0, 0.53),
            command=frame.hide, frameColor=(0.5, 0, 0, 1)
        )
        
        # Column names
        DirectLabel(parent=frame, text="Type", scale=0.04, pos=(-0.35, 0, 0.45), text_fg=(0.7,0.7,0.7,1), frameColor=(0,0,0,0))
        DirectLabel(parent=frame, text="Quantity", scale=0.04, pos=(0.3, 0, 0.45), text_fg=(0.7,0.7,0.7,1), frameColor=(0,0,0,0))

        # Scrollable list
        self.inv_scroll_frame = DirectScrolledFrame(
            parent=frame,
            canvasSize=(-0.4, 0.4, -2, 0), # Dynamically adjusted below
            frameSize=(-0.45, 0.45, -0.55, 0.4),
            frameColor=(0, 0, 0, 0.3),
            verticalScroll_frameSize=(0, 0.02, -0.55, 0.4),
            manageScrollBars=True,
            autoHideScrollBars=True
        )
        
        # Make scrollbar invisible
        self.inv_scroll_frame.verticalScroll['frameColor'] = (0, 0, 0, 0)
        self.inv_scroll_frame.verticalScroll.incButton['frameColor'] = (0, 0, 0, 0)
        self.inv_scroll_frame.verticalScroll.decButton['frameColor'] = (0, 0, 0, 0)
        self.inv_scroll_frame.verticalScroll.thumb['frameColor'] = (0, 0, 0, 0)

        # BIND SCROLLING EVENTS
        self.inv_scroll_frame.bind(DGG.ENTER, self._scroll_frame_enter, [self.inv_scroll_frame])
        self.inv_scroll_frame.bind(DGG.EXIT, self._scroll_frame_exit, [self.inv_scroll_frame])


    def refresh_inventory_ui(self):
        # Clear old items from the canvas
        for child in self.inv_scroll_frame.getCanvas().getChildren():
            child.removeNode()
            
        y_pos = 0
        item_height = 0.08
        
        # Sort list by category
        sorted_items = sorted(self.inventory.values(), key=lambda x: x.category)
        
        for item in sorted_items:
            # Row background
            row = DirectFrame(
                parent=self.inv_scroll_frame.getCanvas(),
                frameColor=(0.1, 0.1, 0.1, 0.5),
                frameSize=(-0.38, 0.38, -0.06, 0.01),
                pos=(0, 0, y_pos),
                state=DGG.NORMAL
            )
            
            # Icon replaced by color-coded text
            cat_color = (0.5, 0.5, 1, 1) if item.category == "Module" else (0.8, 0.8, 0.8, 1)
            
            # Name and Category
            DirectLabel(
                parent=row, text=f"{item.name}", text_scale=0.04, 
                text_align=TextNode.ALeft, pos=(-0.36, 0, -0.04), 
                text_fg=(1,1,1,1), frameColor=(0,0,0,0)
            )
            DirectLabel(
                parent=row, text=f"[{item.category}]", text_scale=0.03, 
                text_align=TextNode.ALeft, pos=(0.0, 0, -0.04), 
                text_fg=cat_color, frameColor=(0,0,0,0)
            )
            
            # Quantity (with thousand separator)
            qty_str = "{:,}".format(item.quantity).replace(",", " ")
            DirectLabel(
                parent=row, text=qty_str, text_scale=0.04, 
                text_align=TextNode.ARight, pos=(0.36, 0, -0.04), 
                text_fg=(1, 0.8, 0, 1), frameColor=(0,0,0,0)
            )
            
            y_pos -= item_height

        # Adjust Canvas size
        # Ensure minimum height is maintained if list is short
        canvas_height = max(self.inv_scroll_frame['frameSize'][3] - self.inv_scroll_frame['frameSize'][2], abs(y_pos))
        self.inv_scroll_frame['canvasSize'] = (-0.4, 0.4, -canvas_height, 0)
        self.inv_scroll_frame.setCanvasSize()

    # --------------------------------------------------------------------------
    # UI CREATION - MARKET
    # --------------------------------------------------------------------------
    def toggle_market(self):
        if "market" not in self.windows:
            self.create_market_window()
        
        if self.windows["market"].isHidden():
            self.windows["market"].show()
            self.refresh_market_ui()
        else:
            self.windows["market"].hide()

    def create_market_window(self):
        frame = DirectFrame(
            frameColor=self.win_color,
            frameSize=(-0.6, 0.6, -0.7, 0.7),
            pos=(0, 0, 0), # Centered
            state=DGG.NORMAL
        )
        self.windows["market"] = frame
        
        # Header
        self.lbl_wallet = DirectLabel(
            parent=frame, text=f"Wallet: {self.credits:,.0f} ISK", 
            scale=0.05, pos=(-0.5, 0, 0.62), 
            text_align=TextNode.ALeft, text_fg=(0, 1, 1, 1), frameColor=(0,0,0,0)
        )
        
        DirectLabel(
            parent=frame, text="REGIONAL MARKET", scale=0.07, 
            pos=(0, 0, 0.62), text_fg=(1, 1, 1, 1), frameColor=(0,0,0,0)
        )
        DirectButton(
            parent=frame, text="Close", scale=0.05, pos=(0.5, 0, 0.63),
            command=frame.hide
        )

        # Scrollable market list
        self.market_scroll_frame = DirectScrolledFrame(
            parent=frame,
            canvasSize=(-0.5, 0.5, -2, 0),
            frameSize=(-0.55, 0.55, -0.6, 0.5),
            frameColor=(0, 0, 0, 0.3),
            verticalScroll_frameSize=(0, 0.02, -0.6, 0.5),
            manageScrollBars=True,
            autoHideScrollBars=True
        )

        # Make scrollbar invisible
        self.market_scroll_frame.verticalScroll['frameColor'] = (0, 0, 0, 0)
        self.market_scroll_frame.verticalScroll.incButton['frameColor'] = (0, 0, 0, 0)
        self.market_scroll_frame.verticalScroll.decButton['frameColor'] = (0, 0, 0, 0)
        self.market_scroll_frame.verticalScroll.thumb['frameColor'] = (0, 0, 0, 0)
        
        # BIND SCROLLING EVENTS
        self.market_scroll_frame.bind(DGG.ENTER, self._scroll_frame_enter, [self.market_scroll_frame])
        self.market_scroll_frame.bind(DGG.EXIT, self._scroll_frame_exit, [self.market_scroll_frame])
        
        # Dummy Market Data (Items for Sale)
        self.market_data = [
            InventoryItem("Civillian Gatling Laser", "Weapon", 999, 1200),
            InventoryItem("Small Shield Booster", "Module", 50, 45000),
            InventoryItem("Micro Warp Drive", "Module", 20, 120000),
            InventoryItem("Veldspar", "RawMaterial", 100000, 15),
            InventoryItem("Scordite", "RawMaterial", 50000, 22),
            InventoryItem("Antimatter Charge S", "Ammo", 20000, 50),
            InventoryItem("Standard Missile", "Ammo", 5000, 120),
            InventoryItem("Damage Control I", "Module", 10, 85000),
            InventoryItem("Large Armor Repairer", "Module", 5, 250000),
            InventoryItem("Expanded Cargo Hold I", "Module", 15, 60000),
            InventoryItem("Gunnery Upgrade Chip", "Upgrade", 2, 500000),
            InventoryItem("Mining Laser I", "Tool", 10, 20000),
            InventoryItem("Survey Scanner", "Tool", 1, 35000),
        ]

    def buy_item(self, item):
        if self.credits >= item.base_price:
            self.credits -= item.base_price
            self.add_item(item.name, item.category, 1, item.base_price)
            self.refresh_market_ui() # Refresh wallet
            print(f"Bought: {item.name}")
        else:
            print("Insufficient funds!")

    def refresh_market_ui(self):
        # Refresh wallet text (using dot separator for thousands)
        self.lbl_wallet['text'] = f"Wallet: {self.credits:,.0f} ISK".replace(",", " ")

        # Clear list
        for child in self.market_scroll_frame.getCanvas().getChildren():
            child.removeNode()

        y_pos = 0
        item_height = 0.1
        
        for item in self.market_data:
            row = DirectFrame(
                parent=self.market_scroll_frame.getCanvas(),
                frameColor=(0.15, 0.15, 0.15, 0.8),
                frameSize=(-0.5, 0.5, -0.08, 0.01),
                pos=(0, 0, y_pos),
            )
            
            # Item name
            DirectLabel(
                parent=row, text=item.name, scale=0.045,
                pos=(-0.48, 0, -0.05), text_align=TextNode.ALeft,
                text_fg=(1,1,1,1), frameColor=(0,0,0,0)
            )
            
            # Price
            price_str = f"{item.base_price:,.0f} ISK".replace(",", " ")
            DirectLabel(
                parent=row, text=price_str, scale=0.045,
                pos=(0.2, 0, -0.05), text_align=TextNode.ARight,
                text_fg=(0, 1, 0, 1), frameColor=(0,0,0,0)
            )
            
            # Buy Button
            DirectButton(
                parent=row, text="Buy", scale=0.04,
                pos=(0.35, 0, -0.05),
                command=self.buy_item, extraArgs=[item],
                frameColor=(0.2, 0.4, 0.2, 1)
            )

            y_pos -= item_height

        # Adjust Canvas size
        canvas_height = max(self.market_scroll_frame['frameSize'][3] - self.market_scroll_frame['frameSize'][2], abs(y_pos))
        self.market_scroll_frame['canvasSize'] = (-0.5, 0.5, -canvas_height, 0)
        self.market_scroll_frame.setCanvasSize()