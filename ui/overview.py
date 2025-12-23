from panda3d.core import LVector2, TextNode, Point3
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectScrolledFrame import DirectScrolledFrame 
from direct.gui import DirectGuiGlobals as DGG
from direct.task import Task
import random

# Importáljuk a Theme-t a konzisztens megjelenéshez
try:
    from ui.Theme import UITheme
except ImportError:
    class UITheme:
        WINDOW_BG_COLOR = (0.05, 0.05, 0.05, 0.95)
        TEXT_COLOR = (0.9, 0.9, 0.9, 1.0)
        BUTTON_NORMAL = (0.2, 0.4, 0.6, 1.0)
        BUTTON_COLORS = ((0.2, 0.4, 0.6, 1.0), (0.5, 0.7, 1.0, 1.0), (0.4, 0.6, 0.8, 1.0), (0.1, 0.1, 0.1, 1.0))

class Overview:
    def __init__(self, base_app):
        self.base = base_app
        
        # Konfiguráció
        self.RESIZE_EDGE = 0.05
        self.SCREEN_LIMIT = 1.3
        self.MIN_FRAME_SIZE = 0.25
        
        # Állapotváltozók
        self.is_dragging = False
        self.is_resizing = False 
        self.drag_offset = LVector2(0, 0) 
        self.active_frame = None 
        self.resizing_sides = "" 
        
        self.frame_list = []
        self.filter_buttons = []
        self.frame3_data = [] 
        self.scrolled_frames = [] # Itt tartjuk számon a görgethető paneleket

        self.container = DirectFrame(parent=self.base.aspect2d)
        
        self._generate_data()
        self._setup_ui()
        self._setup_events()

    def _generate_data(self):
        for i in range(30):
            is_danger = random.random() > 0.7
            self.frame3_data.append({
                "id": i,
                "text": f"System Core {i+1:02d}",
                "type": "Critical" if is_danger else "Stable",
                "color": (0.8, 0.2, 0.2, 1) if is_danger else (0.2, 0.8, 0.2, 1)
            })

    def _setup_ui(self):
        # Panelek létrehozása
        self.frame1 = self._create_base_frame("Ship Systems", (-0.7, 0, 0.4))
        self.frame2 = self._create_base_frame("Sensor Logs", (0.0, 0, -0.4))
        self.frame3 = self._create_base_frame("Fleet Status", (0.7, 0, 0.4))

        # 1. Panel: Gomb
        self.btn_diag = DirectButton(
            parent=self.frame1, text="Run Diagnostics", 
            frameColor=UITheme.BUTTON_COLORS,
            text_fg=UITheme.TEXT_COLOR, text_scale=0.045,
            relief=DGG.FLAT, pos=(0, 0, -0.05)
        )

        # 2. Panel: Görgethető logok
        self.scroll2 = DirectScrolledFrame(
            parent=self.frame2, frameColor=(0.1, 0.1, 0.1, 0.5),
            verticalScroll_thumb_frameColor=UITheme.BUTTON_NORMAL,
            relief=DGG.FLAT, scrollBarWidth=0.03
        )
        self.scrolled_frames.append(self.scroll2)
        
        for i in range(20):
            OnscreenText(parent=self.scroll2.getCanvas(), text=f"LOG #{i:03d}: Sector scanning...", 
                        scale=0.035, pos=(-0.25, -0.05 - i*0.06), fg=UITheme.TEXT_COLOR, align=TextNode.ALeft)
        self.scroll2['canvasSize'] = (-0.3, 0.3, -1.3, 0)

        # 3. Panel: Flotta lista
        self.scroll3 = DirectScrolledFrame(
            parent=self.frame3, frameColor=(0.1, 0.1, 0.1, 0.5),
            verticalScroll_thumb_frameColor=UITheme.BUTTON_NORMAL,
            relief=DGG.FLAT, scrollBarWidth=0.03
        )
        self.scrolled_frames.append(self.scroll3)
        self._refresh_fleet_list()

        for f in self.frame_list:
            self._update_content_layout(f)

    def _create_base_frame(self, title, pos):
        f = DirectFrame(
            parent=self.container,
            frameColor=UITheme.WINDOW_BG_COLOR,
            frameSize=(-0.35, 0.35, -0.3, 0.3),
            pos=pos,
            text=title,
            text_fg=UITheme.TEXT_COLOR,
            text_align=TextNode.ACenter,
            borderWidth=(0.005, 0.005),
            relief=DGG.FLAT
        )
        self.frame_list.append(f)
        return f

    def _refresh_fleet_list(self):
        for child in self.scroll3.getCanvas().getChildren(): child.removeNode()
        y = -0.05
        for item in self.frame3_data:
            row = DirectFrame(parent=self.scroll3.getCanvas(), frameColor=(0.15, 0.15, 0.2, 0.8),
                              frameSize=(-0.3, 0.3, -0.03, 0.03), pos=(0, 0, y))
            OnscreenText(parent=row, text=item['text'], scale=0.03, pos=(-0.28, -0.01), fg=UITheme.TEXT_COLOR, align=TextNode.ALeft)
            y -= 0.07
        self.scroll3['canvasSize'] = (-0.3, 0.3, y, 0)

    # ---------------- ESEMÉNYKEZELÉS ----------------

    def _setup_events(self):
        self.base.accept('mouse1', self.start_interaction)
        self.base.accept('mouse1-up', self.stop_interaction)
        # Görgetés események
        self.base.accept('wheel_up', self._handle_scroll, [-1])
        self.base.accept('wheel_down', self._handle_scroll, [1])
        self.base.taskMgr.add(self.interaction_task, 'overview_interaction_task')

    def _get_hovered_scroll_frame(self):
        """Megkeresi, hogy az egér épp egy görgethető panel felett van-e."""
        if not self.base.mouseWatcherNode.hasMouse(): return None
        m_pos = Point3(self.base.mouseWatcherNode.getMouseX(), 0, self.base.mouseWatcherNode.getMouseY())
        
        for sf in self.scrolled_frames:
            # Relatív pozíció a ScrolledFrame-hez képest
            local_pos = sf.getRelativePoint(self.base.render2d, m_pos)
            fs = sf['frameSize']
            if fs[0] <= local_pos.x <= fs[1] and fs[2] <= local_pos.z <= fs[3]:
                return sf
        return None

    def _handle_scroll(self, direction):
        if self.container.isHidden(): return
        target_sf = self._get_hovered_scroll_frame()
        if target_sf:
            sb = target_sf.verticalScroll
            if sb and not sb.isHidden():
                # Görgetési lépköz (SCROLL_STEP)
                step = 0.1 * direction
                sb['value'] = max(sb['range'][0], min(sb['range'][1], sb['value'] + step))

    def _check_interaction_area(self, mx, my, frame):
        pos = frame.getPos(self.base.aspect2d)
        fs = frame['frameSize']
        left, right = pos.getX() + fs[0], pos.getX() + fs[1]
        bottom, top = pos.getZ() + fs[2], pos.getZ() + fs[3]
        
        if not (left <= mx <= right and bottom <= my <= top):
            return None, ""
            
        sides = ""
        if mx > right - self.RESIZE_EDGE: sides += "r"
        elif mx < left + self.RESIZE_EDGE: sides += "l"
        if my > top - self.RESIZE_EDGE: sides += "t"
        elif my < bottom + self.RESIZE_EDGE: sides += "b"
        
        if sides: return 'resize', sides
        return 'drag', ""

    def start_interaction(self):
        if self.container.isHidden() or not self.base.mouseWatcherNode.hasMouse(): return
        m = self.base.mouseWatcherNode.getMouse()
        mx, my = m.getX(), m.getY()
        
        for frame in reversed(self.frame_list):
            action, sides = self._check_interaction_area(mx, my, frame)
            if action:
                self.active_frame = frame
                self.frame_list.remove(frame)
                self.frame_list.append(frame)
                frame.reparentTo(self.container)
                
                if action == 'resize':
                    self.is_resizing = True
                    self.resizing_sides = sides
                elif action == 'drag':
                    self.is_dragging = True
                    self.drag_offset = LVector2(frame.getX() - mx, frame.getZ() - my)
                return

    def stop_interaction(self):
        if self.active_frame:
            self._update_content_layout(self.active_frame)
        self.active_frame = None
        self.is_dragging = False
        self.is_resizing = False

    def interaction_task(self, task):
        if not self.active_frame or not self.base.mouseWatcherNode.hasMouse():
            return Task.cont
            
        m = self.base.mouseWatcherNode.getMouse()
        mx, my = m.getX(), m.getY()
        frame = self.active_frame
        
        if self.is_dragging:
            frame.setPos(mx + self.drag_offset.getX(), 0, my + self.drag_offset.getY())
        elif self.is_resizing:
            fs = frame['frameSize']
            cx, cz = frame.getX(), frame.getZ()
            w_half, h_half = (fs[1]-fs[0])/2, (fs[3]-fs[2])/2
            l, r, b, t = cx-w_half, cx+w_half, cz-h_half, cz+h_half
            
            if 'r' in self.resizing_sides: r = mx
            if 'l' in self.resizing_sides: l = mx
            if 't' in self.resizing_sides: t = my
            if 'b' in self.resizing_sides: b = my
            
            nw, nh = max(self.MIN_FRAME_SIZE, r-l), max(self.MIN_FRAME_SIZE, t-b)
            frame.setPos((l+r)/2, 0, (b+t)/2)
            frame['frameSize'] = (-nw/2, nw/2, -nh/2, nh/2)
            self._update_content_layout(frame)
        return Task.cont

    def _update_content_layout(self, frame):
        fs = frame['frameSize']
        w, h = fs[1] - fs[0], fs[3] - fs[2]
        t_scale = min(0.045, w * 0.12) 
        frame['text_scale'] = t_scale
        frame['text_pos'] = (0, (h / 2) - t_scale - 0.02)
        
        # Belső scrollek igazítása
        if hasattr(self, 'scroll2') and frame == self.frame2:
            self.scroll2['frameSize'] = (-w/2+0.05, w/2-0.05, -h/2+0.05, h/2-0.12)
        if hasattr(self, 'scroll3') and frame == self.frame3:
            self.scroll3['frameSize'] = (-w/2+0.05, w/2-0.05, -h/2+0.05, h/2-0.12)

    def show(self): self.container.show()
    def hide(self): self.container.hide()
    def toggle(self):
        if self.container.isHidden(): self.show()
        else: self.hide()