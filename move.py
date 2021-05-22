from pos import Pos
from piece import Piece
from board import Board

class Move:

    def __init__(self, board, pos, newpos, active, isPlayerMove=False):
        self.board = board
        self.piece = board(pos)
        self.active = active
        self.pos = pos
        self.newpos = newpos
        self.isPlayerMove = isPlayerMove
        
        self.capture = '' 
        self.castles = ''
        self.newEnpassant = None
        self.promotion = ''
        self.enpassant = False

        if self.piece.role == 'p':
            self.detectNewEnpassantPossible()
            self.detectEnpassant()
            self.detectPromotion()
        self.detectCapture()
            
    def detectEnpassant(self):
        if self.board.enpassantPossible == self.newpos:
            self.enpassant = True

    def detectCapture(self):
        if (self.board(self.newpos) and self.board(self.newpos).col == self.piece.opcol) or self.enpassant:
            self.capture = 'x'
            return True

    def detectNewEnpassantPossible(self):
        if self.piece.role == 'p' and self.pos.distance(self.newpos) == 2:
            #check for neighbouring pawns
            neighbours = [self.newpos + Pos(0, 1), self.newpos + Pos(0, -1)]
            neighbours = [self.board(pos).role == 'p' for pos in neighbours if self.board(pos)]
            if any(neighbours):
                self.newEnpassant = self.pos + Pos(self.board(self.pos).dir, 0)

    def detectPromotion(self):
        if self.piece.role == 'p' and (self.active == 'w' and self.newpos.rank == 8) or (self.active == 'b' and self.newpos.rank == 1):
            promoteTo = None
            if not self.isPlayerMove:
                promoteTo = 'q'

            while not promoteTo in ['q', 'r', 'n', 'b']:
                promoteTo = input('What to promote to? (q/r/n/b): ')
            
            self.promotion = promoteTo
            if self.active == 'w':
                promoteTo = promoteTo.upper()
            
            return True

        return False

    def isLegal(self, isPlayerMove=False):
        #there is a piece at pos belonging to active player
        if not self.piece or not self.active == self.active:
            return False

        #newpos is on the board
        if not self.newpos.isOnBoard():
            if self.isPlayerMove:
                print('There is no such field on the board.')
            return False
        
        #newpos is different from current pos
        if self.pos == self.newpos:
            if self.isPlayerMove:
                print('You have to move by at least one field.')
            return False

        #possible move
        if not self.piece.canMove(self.pos, self.newpos):
            if self.isPlayerMove:
                print('Invalid move.')
            return False

        #castles
        if self.piece.role == 'k' and self.newpos.fileDistance(self.pos) == 2:
            #king is in check
            if self.board.inCheck(self.active):
                return False
            
            #king steps into check
            if Move(self.board, self.pos, Pos(self.newpos.i, int((self.newpos.j + self.pos.j)/2)), self.active).leavesKingInCheck(self.active):
                return False

            if self.active == 'w' and str(self.pos) == 'e1':
                if str(self.newpos) == 'g1':
                    if self.board.castleRight['K']:
                        self.castles = 'K'
                    else:
                        return False

                elif str(self.newpos) == 'c1':
                    if self.board.castleRight['Q']:
                        self.castles = 'Q'
                    else:
                        return False
            
            elif self.active == 'b' and str(self.pos) == 'e8':
                if str(self.newpos) == 'g8':
                    if self.board.castleRight['k']:
                        self.castles = 'k'
                    else:
                        return False

                elif str(self.newpos) == 'c8':
                    if self.board.castleRight['q']:
                        self.castles = 'q'
                    else:
                        return False

        #pawn capture/en passant
        if self.piece.role == 'p' and self.pos.fileDistance(self.newpos) == 1 and self.board.isEmpty(self.newpos) and not self.enpassant:
            return False

        #path is clear
        if not self.board.isPathClear(self.pos, self.newpos):
            if self.isPlayerMove:
                print('Path obstructed.')
            return False
       
        #King not in check after move
        if self.leavesKingInCheck(self.active):
            if self.isPlayerMove:
                print('King would be in check after this move.')
            return False

        return True

    def leavesKingInCheck(self, col):
        tmp = self.board.copy()
        Move(tmp, self.pos, self.newpos, self.active).execute()
        return tmp.inCheck(col)

    def __str__(self):
        algebraicNotation = ''
        
        if self.piece.role == 'p':
            if self.capture:
                algebraicNotation += self.pos.file

        else:
            algebraicNotation += str(self.piece).upper()
        
            #look for squares with pieces of the same kind, that could also do this move
            ambiguousSquares = list(filter(lambda pos: self.board(pos).role == self.piece.role and Move(self.board, pos, self.newpos, self.active).isLegal(), self.board.squaresOfPlayer(self.active)))

            if len(ambiguousSquares) == 2:
                pos1, pos2 = ambiguousSquares
                if pos1.isSameFile(pos2):
                    algebraicNotation += str(self.pos.rank)

                else:
                    algebraicNotation += self.pos.file

            elif len(ambiguousSquares) > 2:
                algebraicNotation += str(self.pos)
        
        algebraicNotation += self.capture + str(self.newpos)
        if self.promotion:
            algebraicNotation += '=' + self.promotion.upper()

        elif self.castles.lower() == 'k':
            algebraicNotation = 'O-O'
        
        elif self.castles.lower() == 'q':
            algebraicNotation = 'O-O-O'

        if self.leavesKingInCheck(self.piece.opcol):
            algebraicNotation += '+'

        return algebraicNotation

    def execute(self):
        #assuming self.isLegal() has been run before

        if self.promotion:
            self.board.movePiece(self.pos, self.newpos)
            self.board(self.newpos).role = self.promotion
            self.board(self.newpos).dir = None
            return

        elif self.enpassant:
            self.board.setEmpty(Pos(self.pos.i, self.newpos.j))

        elif self.castles:
            if self.active == 'w':
                self.board.castleRight['K'] = False
                self.board.castleRight['Q'] = False
            else:
                self.board.castleRight['k'] = False
                self.board.castleRight['q'] = False
                
            if self.castles == 'K':
                self.board.movePiece(Pos(sqr='h1'), Pos(sqr='f1'))
                
            elif self.castles == 'Q':
                self.board.movePiece(Pos(sqr='a1'), Pos(sqr='d1'))

            elif self.castles == 'k':
                self.board.movePiece(Pos(sqr='h8'), Pos(sqr='f8'))
            
            elif self.castles == 'q':
                self.board.movePiece(Pos(sqr='a8'), Pos(sqr='d8'))

        self.board.movePiece(self.pos, self.newpos)


        
