from direct.gui.DirectGui import DirectFrame, DirectButton
from panda3d.core import LVecBase2f
import random

class GalaxyMap:
    def __init__(self, base, galaxy):
        self.base = base
        self.galaxy = galaxy
        self.visible = False
        
        # Térkép háttere
        self.frame = DirectFrame(
            frameColor=(0.05, 0.05, 0.1, 0.95),
            frameSize=(-1.2, 1.2, -0.9, 0.9),
            pos=(0, 0, 0),
            parent=self.base.aspect2d
        )
        self.frame.hide()
        
        self.node_buttons = {}
        self._generate_map_layout()

    def _generate_map_layout(self):
        # Véletlenszerű pozíciók a 2D térképen a rendszereknek
        for sys_id in self.galaxy.systems:
            # Véletlen elhelyezés, hogy ne legyenek egymáson
            pos = (random.uniform(-1.0, 1.0), 0, random.uniform(-0.7, 0.7))
            
            btn = DirectButton(
                parent=self.frame,
                text=str(sys_id),
                text_scale=0.05,
                text_fg=(1,1,1,1),
                frameSize=(-0.05, 0.05, -0.05, 0.05),
                pos=pos,
                command=self.on_node_click,
                extraArgs=[sys_id]
            )
            self.node_buttons[sys_id] = btn

    def on_node_click(self, sys_id):
        print(f"Térkép: Kiválasztott rendszer: {sys_id}")

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.frame.show()
            self.update_colors()
        else:
            self.frame.hide()

    def update_colors(self):
        # Színkódok frissítése az aktuális helyzet alapján
        curr = self.galaxy.current_system_id
        neighbors = self.galaxy.adj_list.get(curr, [])
        
        for sid, btn in self.node_buttons.items():
            if sid == curr:
                btn['frameColor'] = (0, 0.8, 0, 1) # Zöld: Itt vagy
            elif sid in neighbors:
                btn['frameColor'] = (0, 0.4, 0.8, 1) # Kék: Szomszédos
            else:
                btn['frameColor'] = (0.3, 0.3, 0.3, 1) # Szürke: Távoli