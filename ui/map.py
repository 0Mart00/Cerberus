from direct.gui.DirectGui import DirectFrame, DirectButton
from panda3d.core import LVecBase2f

class GalaxyMap:
    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.visible = False
        
        # Térkép háttere
        self.frame = DirectFrame(
            frameColor=(0.05, 0.05, 0.1, 0.9),
            frameSize=(-1.2, 1.2, -0.9, 0.9),
            pos=(0, 0, 0)
        )
        self.frame.hide()
        
        # Rendszerek gombjai a térképen
        self.node_buttons = {}
        self._generate_map_layout()

    def _generate_map_layout(self):
        # Véletlenszerű pozíciók a 2D térképen
        for sys_id in self.galaxy.systems:
            pos = (random.uniform(-1.1, 1.1), 0, random.uniform(-0.8, 0.8))
            
            btn = DirectButton(
                parent=self.frame,
                text=str(sys_id),
                scale=0.04,
                pos=pos,
                command=self.on_node_click,
                extraArgs=[sys_id]
            )
            self.node_buttons[sys_id] = btn

    def on_node_click(self, sys_id):
        print(f"Információ a {sys_id}. rendszerről...")

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.frame.show()
            # Kiemeljük az aktuális tartózkodási helyet
            for sid, btn in self.node_buttons.items():
                if sid == self.galaxy.current_system_id:
                    btn['frameColor'] = (0, 1, 0, 1) # Zöld = itt vagy
                elif sid in self.galaxy.adj_list[self.galaxy.current_system_id]:
                    btn['frameColor'] = (0, 0.5, 1, 1) # Kék = közvetlen szomszéd
                else:
                    btn['frameColor'] = (0.5, 0.5, 0.5, 1)
        else:
            self.frame.hide()