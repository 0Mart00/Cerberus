from direct.gui.DirectGui import DirectFrame, DirectButton, DGG
from panda3d.core import LVecBase3f
import random
from .UITheme.Theme import UITheme

class GalaxyMap:
    def __init__(self, base, galaxy):
        self.base = base
        self.galaxy = galaxy
        self.visible = False
        
        # Térkép háttere a UITheme-ből
        self.frame = DirectFrame(
            frameColor=UITheme.MAP_BG_COLOR,
            frameSize=(-1.2, 1.2, -0.9, 0.9),
            pos=(0, 0, 0),
            parent=self.base.aspect2d,
            state=DGG.NORMAL # Megakadályozza az átkattintást a térkép mögé
        )
        self.frame.hide()
        
        self.node_buttons = {}
        self._generate_map_layout()

    def _generate_map_layout(self):
        """Létrehozza a rendszerek gombjait a térképen."""
        
        # Alapstílus lekérése a témából
        btn_style = UITheme.get_button_style()
        # A térképen a kisebb betűméretet használjuk
        btn_style["text_scale"] = UITheme.SMALL_BUTTON_SCALE

        for sys_id in self.galaxy.systems:
            # Véletlenszerű pozíció elhelyezés a 2D síkon
            pos = (random.uniform(-1.1, 1.1), 0, random.uniform(-0.8, 0.8))
            
            btn = DirectButton(
                parent=self.frame,
                text=str(sys_id),
                pos=pos,
                frameSize=(-0.07, 0.07, -0.07, 0.07),
                command=self.on_node_click,
                extraArgs=[sys_id],
                **btn_style # Alkalmazza a színeket és a flat stílust
            )
            self.node_buttons[sys_id] = btn

    def on_node_click(self, sys_id):
        """Eseménykezelő a rendszerre kattintáshoz."""
        print(f"Térkép: Kiválasztott rendszer: {sys_id}")
        # Itt lehetne elindítani az ugrást (Warp/Jump)

    def toggle(self):
        """Térkép ki/be kapcsolása."""
        self.visible = not self.visible
        if self.visible:
            self.frame.show()
            self.update_colors()
        else:
            self.frame.hide()

    def update_colors(self):
        """Frissíti a gombok színeit a játékos aktuális pozíciója alapján."""
        curr = self.galaxy.current_system_id
        neighbors = self.galaxy.adj_list.get(curr, [])
        
        for sid, btn in self.node_buttons.items():
            if sid == curr:
                # Aktuális helyzet: Zöld
                new_color = UITheme.MAP_NODE_CURRENT
            elif sid in neighbors:
                # Szomszédok: Kék
                new_color = UITheme.MAP_NODE_NEIGHBOR
            else:
                # Minden más: Szürke
                new_color = UITheme.MAP_NODE_DISTANT
            
            # Mivel a DirectButton-nak tuple-t adtunk a stílusban, 
            # itt is érdemes mind a 4 állapotot (normal, pressed, rollover, disabled) 
            # ugyanarra a színre állítani, hogy ne villogjon elvándorláskor.
            btn['frameColor'] = (new_color, new_color, new_color, UITheme.BUTTON_DISABLED)

    def show(self):
        self.visible = True
        self.frame.show()
        self.update_colors()

    def hide(self):
        self.visible = False
        self.frame.hide()