from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from move import Move
from game import Game
from pos import Pos

class BoardScene(QGraphicsScene):
    def __init__(self, parentLayout, game):
        super().__init__()
        self.game = game
        self.parentLayout = parentLayout

        self.boardWidth = 600
        self.squareWidth = int(self.boardWidth/8)
        
        #pixmaps
        self.boardPixmap = QPixmap('graphics/chessboard.png').scaledToWidth(self.boardWidth)
        self.piecesPixmap = QPixmap('graphics/pieces_sprites.svg').scaledToWidth(6 * self.squareWidth, mode=Qt.SmoothTransformation)
        
        self.addPixmap(self.boardPixmap).setZValue(-1)

        #event memory
        self.clickPos = None
        self.activePos = None
        self.activePiece = None
        self.legalMoves = []

        self.state = 'idle'
        #state in [idle, draggingPiece, pieceSelected]
        
        self.boardSetup()
        self.updateHighlights()

    def setState(self, state):
        #self.parentLayout.stateDisplay.setText(f'now in state: {state}.')
        self.state = state

        if state == 'idle':
            if self.activePiece:
                self.activePiece.setZValue(1)
            self.clickPos = None
            self.activePos = None
            self.activePiece = None
            self.legalMoves = []
            self.updateHighlights()


    def posToOffset(self, pos):
        return (pos.j * self.squareWidth, (7 - pos.i) * self.squareWidth)

    def piecePix(self, role, col):
        offset = int(self.piecesPixmap.height()/2)
        y = 0
        if col == 'b':
            y = offset

        roles = ['k', 'q', 'b', 'n', 'r', 'p']
        x = roles.index(role) * offset

        return self.piecesPixmap.copy(x, y, offset, offset)

    def boardSetup(self):
        for pos, piece in self.game.board.pieces.items():
            piece = self.addPixmap(self.piecePix(piece.role, piece.col))
            piece.setZValue(1)
            piece.setPos(*self.posToOffset(pos))

    def mouseposToPos(self, x, y):
        return Pos(7 - y // self.squareWidth, x // self.squareWidth)

    def legalMovesActivePos(self):
        return self.game.legalMoves(self.game.active, self.clickPos)

    def drawSquare(self, pos, color):
        
        if isinstance(pos, Pos):
            thickness = 5
            pen = QPen(QColor(color), thickness)
            pen.setJoinStyle(Qt.MiterJoin)
            x, y = self.posToOffset(pos)
            self.addRect(x + thickness/2, y + thickness/2, self.squareWidth - thickness, self.squareWidth - thickness, pen)
        
        elif isinstance(pos, list):
            for p in pos:
                self.drawSquare(p, color)

    def pieces(self):
        return list(filter(lambda item: isinstance(item, QGraphicsPixmapItem) and item.zValue() > 0, self.items()))

    def getPieceAt(self, pos, notReturnActive=False):
        x, y = self.posToOffset(pos)
        if notReturnActive:
            
            items = self.items(QRectF(float(x), float(y), float(self.squareWidth), float(self.squareWidth)), order=Qt.DescendingOrder)
            items = list(filter(lambda item: item.zValue() == 1, items))
            return items.pop()            

        return self.itemAt(x + 0.5 * self.squareWidth, y + 0.5 * self.squareWidth, QTransform())

    def updateHighlights(self, yellowHighlights=[]):
        #clear all highlights
        for item in filter(lambda item: isinstance(item, QGraphicsRectItem), self.items()):
            self.removeItem(item)
        
        #highlight given squares in organge (legal moves) 
        self.drawSquare(yellowHighlights, 'orange')
        
        #check
        if self.game.board.inCheck(self.game.active):
            self.drawSquare(self.game.board.king(self.game.active), 'red')
        
        #selected piece
        if self.activePos:
            self.drawSquare(self.activePos, QColor(0, 140, 250))

    def movePiece(self, piece, newpos, pos=None, capture=False, promotion='', enpassant=False):
        
        #executed after the move is executed on the board
        col = self.game.passive

        #move/remove other pieces when required
        if capture:
            if enpassant:
                self.removeItem(self.getPieceAt(Pos(pos.i, newpos.j), notReturnActive=True)) 
            
            else:
                self.removeItem(self.getPieceAt(newpos, notReturnActive=True))

        if promotion:
            piece.setPixmap(self.piecePix(promotion, col))

        #move the piece
        piece.setPos(*self.posToOffset(newpos))

    def mouseMoveEvent(self, event):
        #dragging a piece
        x, y = event.scenePos().toPoint().toTuple()
        if self.activePos:
            x, y = event.scenePos().toPoint().toTuple()
            self.activePiece.setPos(x - self.squareWidth/2, y - self.squareWidth/2)

    def mousePressEvent(self, event):
        #get mouse position
        x, y = event.scenePos().toPoint().toTuple()
        self.clickPos = self.mouseposToPos(x, y)

        if x <= self.boardWidth and y <= self.boardWidth:

            if self.state == 'idle':
                #clicking on active player's piece
                if self.game.board(self.clickPos) and self.game.board(self.clickPos).col == self.game.active:
                    self.legalMoves = [move.newpos for move in self.game.legalMoves(self.game.active, self.clickPos)]
                    self.activePos = self.clickPos
                    self.activePiece = self.getPieceAt(self.activePos)
                    self.activePiece.setZValue(2)
                    self.updateHighlights(self.legalMoves)
                    self.setState('draggingPiece')            

            elif self.state == 'pieceSelected':
                #make move by clicking twice
                if self.clickPos in self.legalMoves:
                    self.makeMove(Move(self.game.board, self.activePos, self.clickPos, self.game.active))
                    self.setState('idle')
                
                #drag piece or unselect by clicking active piece
                elif self.clickPos == self.activePos:
                    #self.setState('draggingPiece')
                    pass

                #unselect selected piece
                elif not self.game.board(self.clickPos) or self.game.board(self.clickPos).col != self.game.active:
                    self.setState('idle')

                #clicking on active player's piece
                elif self.game.board(self.clickPos).col == self.game.active:
                    self.setState('idle')
                    self.mousePressEvent(event)

        #click not on board
        else:
            self.setState('idle')
        

    def mouseReleaseEvent(self, event):     
        #get mouse position
        x, y = event.scenePos().toPoint().toTuple()
        if self.clickPos and x <= self.boardWidth and y <= self.boardWidth:
            releasepos = self.mouseposToPos(x, y)
            
            if self.state == 'draggingPiece' and self.activePos:

                #select Piece
                if self.activePos == releasepos:
                    self.setState('pieceSelected')
                    self.activePiece.setPos(*self.posToOffset(self.activePos))
                    return
                
                #drag piece
                elif releasepos in self.legalMoves:
                    self.makeMove(Move(self.game.board, self.activePos, releasepos, self.game.active))

                else:
                    self.activePiece.setPos(*self.posToOffset(self.activePos))

            elif self.state == 'pieceSelected':
                #unselect selected piece
                if releasepos == self.activePos:
                    self.activePiece.setPos(*self.posToOffset(releasepos))
                    self.setState('idle')

                #drag piece
                elif releasepos in self.legalMoves:
                    self.makeMove(Move(self.game.board, self.activePos, releasepos, self.game.active))

                else:
                    self.activePiece.setPos(*self.posToOffset(self.activePos))

        elif self.activePiece:
            self.activePiece.setPos(*self.posToOffset(self.activePos))

        self.setState('idle')

    def makeMove(self, move: Move):
        if move.isLegal():
            self.game.turn(move)
            self.movePiece(self.activePiece, move.newpos, move.pos, move.capture, move.promotion, move.enpassant)
            
            #castles
            if move.castles:
                if move.castles == 'K':
                    self.movePiece(self.getPieceAt(Pos(sqr='h1')), Pos(sqr='f1'))
                
                elif move.castles == 'k':
                    self.movePiece(self.getPieceAt(Pos(sqr='h8')), Pos(sqr='f8'))

                elif move.castles == 'Q':
                    self.movePiece(self.getPieceAt(Pos(sqr='a1')), Pos(sqr='d1'))

                elif move.castles == 'q':
                    self.movePiece(self.getPieceAt(Pos(sqr='a8')), Pos(sqr='d8'))
        
            self.parentLayout.updateGameInfo()
            if self.game.pgnDict['score']:
                self.parentLayout.endGame()

            
 