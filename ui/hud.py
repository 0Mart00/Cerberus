from .overview_panel import OverviewPanel
# from data.overview_item import OverviewManager # Eltávolítva, mert az OverviewPanel maga generálja az adatokat a mintában

class HUD:
    """
    A Cerberus játék interfésze. Ide integráljuk az Overview Panelt.
    """
    def __init__(self, base):
        self.base = base
        
        # 1. Initialize the Overview Panel (átadva a Base-t)
        self.overview_panel = OverviewPanel(base)

        # 2. Hozzáadjuk a mintában lévő egér eseménykezelő logikát a fő task managerhez
        self.base.taskMgr.add(self.update_mouse_state_task, "UpdateMouseStateTask")
        self.base.accept('wheel_up', self.handle_scroll, ['up'])
        self.base.accept('wheel_down', self.handle_scroll, ['down'])
        self.scroll_direction = None

        # Kezdetben elrejti a HUD-ot, hogy a menü látható legyen
        self.hide()

    # --- Görgetés/Zoom Kezelés Logika (a mintából átvéve) ---
    def handle_scroll(self, direction):
        self.scroll_direction = direction
        
    def update_mouse_state_task(self, task):
        """Manuálisan ellenőrzi, hogy az egér a UI panel felett van-e, és kezeli a görgetést/zoomot."""
        
        is_over = False
        
        if self.base.mouseWatcherNode.hasMouse():
            mouse_x = self.base.mouseWatcherNode.getMouseX()
            mouse_z = self.base.mouseWatcherNode.getMouseY() 
            
            # A DirectFrame határán belül van-e az egér (aspect2d koordinátákkal)
            # NOTE: Az OverviewPanel most az aspect2d-re van parentelve.
            
            # A main_frame határai aspektus2d-n belül
            # getBounds() Panda3D NodePath hívás: (xmin, xmax, ymin, ymax)
            # Itt NodePath van, a DirectFrame egy NodePath
            frame_bounds = self.overview_panel.main_frame.getBounds()
            
            # Konvertálás a képernyő (screen) koordinátákra, ahol az egér van
            # A hiba elkerülése érdekében most egy egyszerű rect check-et futtatunk a DirectFrame-en, 
            # de a mintában szereplő getBounds() hívás használata a legjobb gyakorlat
            
            # A mintában szereplő logikát implementáljuk újra, hogy az a DirectFrame-en működjön:
            
            # A NodePath-ról lekérjük a kiterjedést
            bounds = self.overview_panel.main_frame.getBounds()
            
            # A koordináták normál (-1, 1) tartományúak az aspect2d-n
            # xmin és xmax a fő keret széle
            xmin = self.overview_panel.main_frame.getX() + bounds[0]
            xmax = self.overview_panel.main_frame.getX() + bounds[1]
            zmin = self.overview_panel.main_frame.getZ() + bounds[2]
            zmax = self.overview_panel.main_frame.getZ() + bounds[3]
            
            if xmin <= mouse_x <= xmax and zmin <= mouse_z <= zmax:
                is_over = True
        
        self.overview_panel.set_mouse_over_ui(is_over)
        
        # Görgetés/Zoom kezelése
        if self.scroll_direction:
            if self.overview_panel.is_mouse_over_ui:
                # 1. UI FELETT: Görgetés kezelése a DirectScrolledFrame-en
                bar = self.overview_panel.scroll_frame.verticalScroll
                current_value = bar['value']
                scroll_amount = 0.25 
                
                if self.scroll_direction == 'up':
                    bar['value'] = max(0.0, current_value - scroll_amount)
                elif self.scroll_direction == 'down':
                    bar['value'] = min(1.0, current_value + scroll_amount)
            else:
                # 2. 3D TÉRBEN: Zoomolás kezelése a kamerán
                if self.scroll_direction == 'up':
                    self.zoom_in()
                elif self.scroll_direction == 'down':
                    self.zoom_out()
                    
            self.scroll_direction = None
        
        return task.cont

    def zoom_in(self):
        current_pos = self.base.camera.getPos()
        new_y = current_pos.y + 2
        # Limit: maximális bezoomolás
        self.base.camera.setY(min(new_y, -5)) 

    def zoom_out(self):
        current_pos = self.base.camera.getPos()
        new_y = current_pos.y - 2
        # Limit: maximális kizoomolás
        self.base.camera.setY(max(new_y, -50)) 

    def toggle_visibility(self):
        """Toggles the visibility of the HUD elements."""
        if self.overview_panel.main_frame.isHidden():
            self.show()
        else:
            self.hide()

    def show(self):
        """Shows the HUD components."""
        self.overview_panel.main_frame.show()

    def hide(self):
        """Hides the HUD components."""
        self.overview_panel.main_frame.hide()

    def destroy(self):
        """Clean up all HUD elements."""
        self.base.taskMgr.remove("UpdateMouseStateTask")
        self.base.ignore('wheel_up')
        self.base.ignore('wheel_down')
        self.overview_panel.destroy()