from direct.gui.DirectGui import *
from panda3d.core import TextNode, Vec3, Vec4

# ==============================================================================
# INVENTORY ITEM DATA
# ==============================================================================
class InventoryItem:
    def __init__(self, name, category, quantity=1, base_price=0):
        self.name = name
        self.category = category
        self.quantity = quantity
        self.base_price = base_price # Becsült ár

# ==============================================================================
# WINDOW MANAGER (Inventory & Market)
# ==============================================================================
class WindowManager:
    def __init__(self, game):
        self.game = game
        self.inventory = {} # {item_name: InventoryItem} - Dict a stackeléshez
        self.credits = 100000.0 # Kezdő tőke (ISK/Credits)
        
        # UI Elemek tárolói
        self.windows = {}
        self.inv_scroll_frame = None
        self.market_scroll_frame = None
        
        # Kezdő felszerelés
        self.add_item("Tritanium", "Nyersanyag", 5000, 5)
        self.add_item("Pyerite", "Nyersanyag", 1200, 12)
        self.add_item("Impulzus Lézer I", "Modul", 2, 45000)
        self.add_item("125mm Railgun", "Modul", 1, 32000)
        self.add_item("Vas Töltet S", "Lőszer", 1000, 2)

        # Stílusok
        self.win_color = (0.05, 0.05, 0.05, 0.95) # EVE-es sötét háttér
        self.border_color = (0.4, 0.4, 0.4, 1)

    def add_item(self, name, category, qty, price=0):
        """Végtelen stackelés logika"""
        if name in self.inventory:
            self.inventory[name].quantity += qty
        else:
            self.inventory[name] = InventoryItem(name, category, qty, price)
        
        # Ha nyitva van az inventory, frissítjük
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
    # UI LÉTREHOZÁS - INVENTORY
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
        # Fő ablak keret
        frame = DirectFrame(
            frameColor=self.win_color,
            frameSize=(-0.5, 0.5, -0.6, 0.6),
            pos=(-0.8, 0, 0.2), # Bal oldalra kicsit eltolva
            state=DGG.NORMAL # Hogy kattintható legyen és ne menjen át az egér
        )
        self.windows["inventory"] = frame
        
        # Fejléc
        DirectLabel(
            parent=frame, text="RAKTÉR (Inventory)", text_scale=0.06, 
            pos=(0, 0, 0.52), text_fg=(1, 1, 1, 1), frameColor=(0,0,0,0)
        )
        DirectButton(
            parent=frame, text="X", scale=0.05, pos=(0.45, 0, 0.53),
            command=frame.hide, frameColor=(0.5, 0, 0, 1)
        )
        
        # Oszlopnevek
        DirectLabel(parent=frame, text="Típus", scale=0.04, pos=(-0.35, 0, 0.45), text_fg=(0.7,0.7,0.7,1), frameColor=(0,0,0,0))
        DirectLabel(parent=frame, text="Mennyiség", scale=0.04, pos=(0.3, 0, 0.45), text_fg=(0.7,0.7,0.7,1), frameColor=(0,0,0,0))

        # Scrollozható lista
        self.inv_scroll_frame = DirectScrolledFrame(
            parent=frame,
            canvasSize=(-0.4, 0.4, -2, 0), # Dinamikusan kellene állítani a tartalomhoz
            frameSize=(-0.45, 0.45, -0.55, 0.4),
            frameColor=(0, 0, 0, 0.3),
            verticalScroll_frameSize=(0, 0.02, -0.55, 0.4),
            manageScrollBars=True,
            autoHideScrollBars=True
        )
        
        # GÖRGETŐSÁV ELREJTÉSE (Átlátszóvá tétel)
        self.inv_scroll_frame.verticalScroll['frameColor'] = (0, 0, 0, 0)
        self.inv_scroll_frame.verticalScroll.incButton['frameColor'] = (0, 0, 0, 0)
        self.inv_scroll_frame.verticalScroll.decButton['frameColor'] = (0, 0, 0, 0)
        self.inv_scroll_frame.verticalScroll.thumb['frameColor'] = (0, 0, 0, 0)


    def refresh_inventory_ui(self):
        # Töröljük a régi elemeket a canvasról
        for child in self.inv_scroll_frame.getCanvas().getChildren():
            child.removeNode()
            
        y_pos = 0
        item_height = 0.08
        
        # Lista rendezése kategória szerint
        sorted_items = sorted(self.inventory.values(), key=lambda x: x.category)
        
        for item in sorted_items:
            # Sor háttér
            row = DirectFrame(
                parent=self.inv_scroll_frame.getCanvas(),
                frameColor=(0.1, 0.1, 0.1, 0.5),
                frameSize=(-0.38, 0.38, -0.06, 0.01),
                pos=(0, 0, y_pos),
                state=DGG.NORMAL
            )
            
            # Ikon helyett most színkódolt szöveg
            cat_color = (0.5, 0.5, 1, 1) if item.category == "Modul" else (0.8, 0.8, 0.8, 1)
            
            # Név és Kategória
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
            
            # Mennyiség (ezres elválasztóval)
            qty_str = "{:,}".format(item.quantity).replace(",", ".")
            DirectLabel(
                parent=row, text=qty_str, text_scale=0.04, 
                text_align=TextNode.ARight, pos=(0.36, 0, -0.04), 
                text_fg=(1, 0.8, 0, 1), frameColor=(0,0,0,0)
            )
            
            y_pos -= item_height

        # Canvas méret igazítása
        self.inv_scroll_frame['canvasSize'] = (-0.4, 0.4, y_pos, 0)
        self.inv_scroll_frame.setCanvasSize()

    # --------------------------------------------------------------------------
    # UI LÉTREHOZÁS - MARKET
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
            pos=(0, 0, 0), # Középen
            state=DGG.NORMAL
        )
        self.windows["market"] = frame
        
        # Fejléc
        self.lbl_wallet = DirectLabel(
            parent=frame, text=f"Pénztárca: {self.credits:,.0f} ISK", 
            scale=0.05, pos=(-0.5, 0, 0.62), 
            text_align=TextNode.ALeft, text_fg=(0, 1, 1, 1), frameColor=(0,0,0,0)
        )
        
        DirectLabel(
            parent=frame, text="REGIONÁLIS PIAC", scale=0.07, 
            pos=(0, 0, 0.62), text_fg=(1, 1, 1, 1), frameColor=(0,0,0,0)
        )
        DirectButton(
            parent=frame, text="Bezár", scale=0.05, pos=(0.5, 0, 0.63),
            command=frame.hide
        )

        # Scrollozható piac lista
        self.market_scroll_frame = DirectScrolledFrame(
            parent=frame,
            canvasSize=(-0.5, 0.5, -2, 0),
            frameSize=(-0.55, 0.55, -0.6, 0.5),
            frameColor=(0, 0, 0, 0.3),
            verticalScroll_frameSize=(0, 0.02, -0.6, 0.5),
            manageScrollBars=True,
            autoHideScrollBars=True
        )

        # GÖRGETŐSÁV ELREJTÉSE (Átlátszóvá tétel)
        self.market_scroll_frame.verticalScroll['frameColor'] = (0, 0, 0, 0)
        self.market_scroll_frame.verticalScroll.incButton['frameColor'] = (0, 0, 0, 0)
        self.market_scroll_frame.verticalScroll.decButton['frameColor'] = (0, 0, 0, 0)
        self.market_scroll_frame.verticalScroll.thumb['frameColor'] = (0, 0, 0, 0)
        
        # Dummy Market Data (Eladó cuccok)
        self.market_data = [
            InventoryItem("Civillian Gatling Laser", "Fegyver", 999, 1200),
            InventoryItem("Small Shield Booster", "Modul", 50, 45000),
            InventoryItem("Micro Warp Drive", "Modul", 20, 120000),
            InventoryItem("Veldspar", "Nyersanyag", 100000, 15),
            InventoryItem("Scordite", "Nyersanyag", 50000, 22),
            InventoryItem("Antimatter Charge S", "Lőszer", 20000, 50),
            InventoryItem("Standard Missile", "Lőszer", 5000, 120),
            InventoryItem("Damage Control I", "Modul", 10, 85000),
        ]

    def buy_item(self, item):
        if self.credits >= item.base_price:
            self.credits -= item.base_price
            self.add_item(item.name, item.category, 1, item.base_price)
            self.refresh_market_ui() # Pénz frissítése
            print(f"Vásároltál: {item.name}")
        else:
            print("Nincs elég fedezet!")

    def refresh_market_ui(self):
        # Pénz frissítése
        self.lbl_wallet['text'] = f"Pénztárca: {self.credits:,.0f} ISK".replace(",", " ")

        # Lista törlése
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
            
            # Item név
            DirectLabel(
                parent=row, text=item.name, scale=0.045,
                pos=(-0.48, 0, -0.05), text_align=TextNode.ALeft,
                text_fg=(1,1,1,1), frameColor=(0,0,0,0)
            )
            
            # Ár
            price_str = f"{item.base_price:,.0f} ISK".replace(",", " ")
            DirectLabel(
                parent=row, text=price_str, scale=0.045,
                pos=(0.2, 0, -0.05), text_align=TextNode.ARight,
                text_fg=(0, 1, 0, 1), frameColor=(0,0,0,0)
            )
            
            # Vásárlás Gomb
            DirectButton(
                parent=row, text="Vétel", scale=0.04,
                pos=(0.35, 0, -0.05),
                command=self.buy_item, extraArgs=[item],
                frameColor=(0.2, 0.4, 0.2, 1)
            )

            y_pos -= item_height

        self.market_scroll_frame['canvasSize'] = (-0.5, 0.5, y_pos, 0)
        self.market_scroll_frame.setCanvasSize()