from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, WindowProperties
import sys

# Egyéni rendszerek importálása
from systems.movement import MovingSystem
from systems.camera import CameraSystem
from systems.combat import CombatSystem  # <--- ÚJ
from ui.menus import MainMenu
from ui.map import GalaxyMap
from ui.ShipHUD import ShipHUD 
from ui.overview import Overview
from systems.galaxy import Galaxy
from systems.gamestats import GameStats
from globals import *
from entities.ship import Ship
class PlayerShipData:
    def __init__(self, node_path):
        self.node = node_path
        self.current_shield = 100.0
        self.current_armor = 100.0
        self.current_hull = 100.0
        self.name = "Cerberus One"
    
    def __getattr__(self, name):
        return getattr(self.node, name)

class Game(ShowBase):
    def __init__(self):
        super().__init__()
        
        loadPrcFile("config/settings.prc")
        
        props = WindowProperties()
        props.setTitle("Cerberus Engine - Space Sim")
        self.win.requestProperties(props)
        
        self.state = "GAME"
        self.stats = GameStats()
        self.galaxy = Galaxy(self.render, self)
        self.galaxy_map = GalaxyMap(self, self.galaxy)
        self.moving_system = MovingSystem(self)
        self.camera_system = CameraSystem(self)
        self.combat_system = CombatSystem(self) # <--- ÚJ

        self.my_id = "1"

        # Játékos setup
        player_node = self.render.attachNewNode("PlayerShip")
        self.local_ship = Ship(self,player_node)
        self.player = self.local_ship 

        try:
            model = loader.loadModel("assets/models/SpaceShip.egg")
            model.reparentTo(self.local_ship.node)
            model.setScale(0.5)
        except:
            print("[Warning] SpaceShip modell hiányzik, box használata.")
            loader.loadModel("models/box").reparentTo(self.local_ship.node)

        # UI rendszerek inicializálása
        self.hud = ShipHUD(self, self.local_ship)
        self.hud.container.hide()
        self.hud_visible = False

        self.overview = Overview(self)
        self.overview.hide()

        self.menu = MainMenu(self)
        self.galaxy.warp_player(self.local_ship.node, 0)

        self.setup_controls()
        self.taskMgr.add(self.update, "MainUpdateTask")
        print("[System] Motor kész. O: HUD | M: Térkép | I: Overview")
        print("[Combat] Egér Bal: Lézer | Egér Jobb: Vonósugár")

    def setup_controls(self):
        self.accept('escape', self.toggle_menu)
        self.accept('p', self.galaxy.warp_random, [self.local_ship.node])
        self.accept('m', self.toggle_map)
        self.accept('o', self.toggle_hud)
        self.accept('O', self.toggle_hud)
        self.accept('i', self.toggle_overview)
        self.accept('I', self.toggle_overview)

    def toggle_hud(self):
        self.hud_visible = not self.hud_visible
        if self.hud_visible: self.hud.container.show()
        else: self.hud.container.hide()

    def toggle_overview(self):
        self.overview.toggle()

    def toggle_menu(self):
        if self.state == "GAME":
            self.state = "MENU"
            self.menu.show()
        else:
            self.state = "GAME"
            self.menu.hide()
            
    def toggle_map(self):
        if hasattr(self, 'galaxy_map'):
            self.galaxy_map.toggle()

    def update(self, task):
        dt = globalClock.getDt()
        self.stats.update()
        
        if self.state == "GAME":
            self.moving_system.update(dt)
            self.camera_system.update(dt)
            self.combat_system.update(dt) # <--- ÚJ
            
            if self.hud_visible:
                self.hud.update()
            
        return task.cont

    def start_host(self):
        self.state = "GAME"
        self.menu.hide()
        return True

if __name__ == "__main__":
    game = Game()
    game.run()