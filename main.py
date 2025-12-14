import sys
import os

# Hozzáadjuk a jelenlegi könyvtárat, valamint a "data" és "ui" mappákat az útvonalhoz, 
# hogy a modulok (core, net, data, ui stb.) láthatóak legyenek.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'data'))
sys.path.append(os.path.join(current_dir, 'ui'))

from core.game import CerberusGame

if __name__ == "__main__":
    app = CerberusGame()
    try:
        app.run()
    except Exception as e:
        print(f"Kritikus hiba: {e}")