from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from boardScene import BoardScene
from game import Game

class PlayGameLayout(QGridLayout):
    
    def __init__(self, parent, game):
        super().__init__()
        self.parent = parent
        self.game = game

        #board scene
        self.board = BoardScene(self, self.game)
        self.boardView = QGraphicsView(self.board)

        self.boardView.setFixedSize(self.board.boardWidth, self.board.boardWidth + 2)
        self.boardView.setSceneRect(-0.5, -0.5, self.board.itemsBoundingRect().width(), self.board.itemsBoundingRect().height())
        self.boardView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.boardView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.addWidget(self.boardView, 0, 0)

        #right panel
        self.rightPanel = QVBoxLayout()
        
        self.fenText = QTextEdit(text=self.game.FEN())
        self.fenText.setMaximumHeight(45)
        self.fenText.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.pgnText = QTextEdit(text=self.game.PGN())
        
        self.gameInfo = QVBoxLayout()
        #self.gameInfo.addWidget(QLabel(text='FEN'), 0, 0)
        #self.gameInfo.addWidget(self.fenText, 0, 1)
        #self.gameInfo.addWidget(self.btnStartFromFen, 1, 1)
        self.gameInfo.addWidget(QLabel(text='PGN'))
        self.gameInfo.addWidget(self.pgnText)

        self.rightPanel.addLayout(self.gameInfo)

        self.btnStartNew = QPushButton('Start new game')
        self.btnStartNew.clicked.connect(self.newGame)
        self.rightPanel.addWidget(self.btnStartNew)

        self.btnStartFromFen = QPushButton('Start game \n from this FEN')
        self.btnStartFromFen.clicked.connect(lambda x: self.newGame(self.fenText.toPlainText()))
        
        self.addLayout(self.rightPanel, 0, 1)
        self.fenLayout = QHBoxLayout()
        self.fenLayout.addWidget(QLabel(text='FEN'))
        self.fenLayout.addWidget(self.fenText)
        self.fenLayout.addWidget(self.btnStartFromFen)
        self.addLayout(self.fenLayout, 1, 0)

    def newGame(self, fen=''):
        if fen:
            self.game = Game(fen)
        else:
            self.game = Game()
        
        self.board = BoardScene(self, self.game)
        self.boardView.setScene(self.board)
        self.updateGameInfo()

    def endGame(self):
        self.board.updateHighlights()
        self.updateGameInfo()
        gameResult = ''
        gameScore = self.game.pgnDict['score']
        if gameScore == (1, 0):
            gameResult = 'White won the game.'
        elif gameScore == (0, 1):
            gameResult = 'Black won the game.'
        elif gameScore == (0.5, 0.5):
            gameResult = 'Game ends in a draw.'

        reply = QMessageBox.question(self.parentWidget(), 'Game Finished', f'{gameResult} Start a new game?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


        if reply == QMessageBox.Yes:
            self.newGame()

    def updateGameInfo(self):
        self.fenText.setText(self.game.FEN())
        self.pgnText.setText(self.game.PGN())
