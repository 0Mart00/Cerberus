from direct.gui.DirectGui import DirectFrame, DirectButton, DirectEntry, DirectLabel
import sys

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.frame = DirectFrame(frameColor=(0.1, 0.1, 0.1, 1), frameSize=(-1, 1, -1, 1))
        
        self.title = DirectLabel(
            text="CERBERUS", scale=0.15, pos=(0, 0, 0.7), 
            parent=self.frame, text_fg=(1, 0.5, 0, 1), frameColor=(0,0,0,0)
        )
        
        self.btn_host = DirectButton(
            text="HOSZT (Szerver)", scale=0.07, pos=(0, 0, 0.3), 
            command=self.game.start_host, parent=self.frame
        )
        
        self.ip_entry = DirectEntry(
            text="", scale=0.07, pos=(-0.2, 0, 0), 
            initialText="127.0.0.1", numLines=1, width=10, parent=self.frame
        )
        self.ip_label = DirectLabel(
            text="IP:", scale=0.05, pos=(-0.35, 0, 0), 
            text_fg=(1,1,1,1), frameColor=(0,0,0,0), parent=self.frame
        )

        self.btn_join = DirectButton(
            text="CSATLAKOZÁS", scale=0.07, pos=(0, 0, -0.2), 
            command=self.game.join_game, parent=self.frame
        )
        
        self.btn_quit = DirectButton(
            text="KILÉPÉS", scale=0.05, pos=(0, 0, -0.6), 
            command=sys.exit, parent=self.frame, frameColor=(0.5, 0, 0, 1)
        )

    def hide(self):
        self.frame.hide()