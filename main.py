import sys
import os

# Hozzáadjuk a jelenlegi könyvtárat az útvonalhoz, hogy a modulok (core, net, stb) láthatók legyenek
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import CerberusGame

if __name__ == "__main__":
    app = CerberusGame()
    try:
        app.run()
    except Exception as e:
        print(f"Kritikus hiba: {e}")