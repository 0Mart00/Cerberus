from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, WindowProperties
import sys

# Importok a gyökérből (Cerberus/ prefix nélkül)
from systems.movement import MovingSystem
from systems.camera import CameraSystem
from ui.hud import HUD
from ui.menus import MainMenu
from systems.galaxy import Galaxy
from systems.gamestats import GameStats
from globals import *
from systems.galaxy import Galaxy
class Game(ShowBase):
    def __init__(self):
        super().__init__()
        
        # Konfiguráció betöltése
        loadPrcFile("config/settings.prc")
        
        props = WindowProperties()
        props.setTitle("Cerberus Engine")
        self.win.requestProperties(props)
        
        self.state = "GAME"
        
        # 1. Statisztikai rendszer (Idle számolás)
        self.stats = GameStats()
        
        # 2. Galaxis rendszer (Optimalizált betöltéssel)
        self.galaxy = Galaxy(self.render, self)
        
        # 3. Mozgás és Kamera rendszerek
        self.moving_system = MovingSystem(self)
        self.camera_system = CameraSystem(self)


        self.my_id = "1"
        # Define the player ship
        self.player = self.render.attachNewNode("PlayerShip") 

        # LINK THE PLAYER TO THE HUD HERE:
        self.local_ship = self.player
        # 4. UI elemek
        self.hud = HUD(self)
        self.menu = MainMenu(self)
        
        # Játékos hajó beállítása
        self.player = self.render.find("**/PlayerShip")
        if not self.player or self.player.isEmpty():
            self.player = self.render.attachNewNode("PlayerShip")
            # Megpróbáljuk a modelledet, ha nincs, marad a box
            try:
                model = loader.loadModel("assets/models/SpaceShip.egg")
                model.reparentTo(self.player)
                model.setScale(0.5)
            except:
                loader.loadModel("models/box").reparentTo(self.player)

        # Első rendszer betöltése
        self.galaxy.warp_player(self.player, 0)

        # Irányítás
        self.setup_controls()
        
        self.taskMgr.add(self.update, "MainUpdateTask")
        print("[System] Motor kész. P gomb: Stargate ugrás.")

    def setup_controls(self):
        self.accept('escape', self.toggle_menu)
        # P gomb az ugráshoz
        self.accept('p', self.galaxy.warp_random, [self.player])
        self.accept('P', self.galaxy.warp_random, [self.player])

    def toggle_menu(self):
        if self.state == "GAME":
            self.state = "MENU"
            self.menu.show()
        else:
            self.state = "GAME"
            self.menu.hide()

    def update(self, task):
        dt = globalClock.getDt()
        
        # Idle/Statisztika frissítése
        self.stats.update()
        
        if self.state == "GAME":
            # EREDETI RENDSZEREK UPDATE-JEI
            self.moving_system.update(dt)
            self.camera_system.update(dt)
            self.hud.update(dt)
            
        return task.cont

    def start_host(self):
        print("[Network] Szerver indítása a 1234-es porton...")
        self.state = "GAME"
        self.menu.hide()
        return True

        
if __name__ == "__main__":
    game = Game()
    game.run()