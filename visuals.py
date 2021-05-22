import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from game import Game
from playGameLayout import PlayGameLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Python Chess')
        self.game = Game()#'rnbqkbnr/2pp1ppp/pp6/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 4')
        layout = PlayGameLayout(self, self.game)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication()
    widget = MainWindow()
    widget.show()

    sys.exit(app.exec_())