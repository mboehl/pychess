from pos import Pos
from board import Board
from move import Move
from piece import Piece

class Game:

    def __init__(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        #FEN syntax: <position> <color to move> <castle rights> <possible en passant> <halfmoves since last capture/pawn move> <current fullmove> 
        fen = fen.split(' ')
        castleRight = {char: (char in fen[2]) for char in 'KQkq'}
        self.board = Board(fen[0], castleRight, Pos(sqr=fen[3]))
        self.active = fen[1]
        self.passive = 'w' if self.active == 'b' else 'b' #not self.active
        self.halfmoveClock = 0
        self.currentMove = 1
        self.pgnDict = {}
        if self.active == 'b':
            self.pgnDict[1] = ['...']
        self.pgnDict['score'] = []

    def __str__(self):
        return str(f'{str(self.board)} \n FEN: {self.FEN()} \n PGN: {self.PGN()}')

    def FEN(self):
        castleRight = ''.join([char for (char, val) in self.board.castleRight.items() if val])

        return ' '.join([self.board.fenPos(), self.active, castleRight, str(self.board.enpassantPossible), str(self.halfmoveClock), str(self.currentMove)])

    def addPgnEntry(self, pgnEntry):
        if self.checkmate():
            pgnEntry = pgnEntry[:-1] + '#'
            if self.active == 'w':
                self.pgnDict['score'] = (1, 0)
            else:
                self.pgnDict['score'] = (0, 1)

        if self.stalemate():
            self.pgnDict['score'] = (0.5, 0.5)

        if self.active == 'w':
            self.pgnDict[self.currentMove] = [pgnEntry]
        
        else:
            self.pgnDict[self.currentMove].append(pgnEntry)

    def PGN(self):
        score = '-'.join([str(x) for x in self.pgnDict['score']])
        return '\n'.join([f'{str(k)}. ' + ' '.join(v) for k, v in self.pgnDict.items() if isinstance(k, int)]) + ' ' + score
        
    def turn(self, thisMove=None):
        """Play one halfmove."""
        #print(self)

        activePiece = None
        if thisMove:
            if not thisMove.isLegal():
                return

            activePiece = self.board(thisMove.pos)

        #played in console
        if not thisMove:
            pos = Pos(sqr=input(f'Player: {self.active}. Move from: '))
            while not self.board(pos) or self.board(pos).col != self.active:
                print('There is no such square or this is not one of your pieces.')
                pos = Pos(sqr=input(f'Player: {self.active}. Move from: '))

            activePiece = self.board(pos)

            while not self.legalMoves(self.active, pos=pos):
                print("This piece doesn't have any legal moves.")
                pos = Pos(sqr=input('Move from: '))
                activePiece = self.board(pos)

            newpos = Pos(sqr=input('To: '))
            thisMove = Move(self.board, pos, newpos, self.active)

            while not thisMove.isLegal(isPlayerMove=True):
                newpos = Pos(sqr=input('To: '))
                thisMove = Move(self.board, pos, newpos, self.active)
        
        #keeping track of en passant
        if thisMove.newEnpassant:
            self.board.enpassantPossible = thisMove.newEnpassant
        else:
            self.board.enpassantPossible = Pos(sqr='-')

        if thisMove.castles:
            self.board.castleRight[thisMove.castles] = False
        
        pgnEntry = str(thisMove)

        #execute move
        thisMove.execute()

        #adding after execution to be able to check for checkmate/stalemate
        self.addPgnEntry(pgnEntry)

        #adjust move counters
        if thisMove.capture or activePiece.role == 'p':
            self.halfmoveClock = 0
        else:
            self.halfmoveClock += 1
            
        if self.active == 'b':
            self.currentMove += 1

        #50 move rule
        if self.halfmoveClock == 50 and not self.pgnDict['score']:
            self.pgnDict['score'] = (0.5, 0.5)

        self.active, self.passive = self.passive, self.active
        #print(self)      

    def checkmate(self, passive=None):
        if passive is None:
            passive = self.passive
        return self.board.inCheck(passive) and not self.legalMoves(passive)

    def stalemate(self, passive=None):
        if passive is None:
            passive = self.passive
        return not self.board.inCheck(self.passive) and not self.legalMoves(self.passive)

    def legalMoves(self, col, pos=None):
        moves = []
        if pos and self.board(pos):
            moves = [ Move(self.board, pos, newpos, col) for newpos in self.board(pos).squaresInReach(pos) ]
            
        else:
            moves = [ Move(self.board, pos, newpos, col) for pos in self.board.squaresOfPlayer(col) for newpos in self.board(pos).squaresInReach(pos) ]

        return [ move for move in moves if move.isLegal() ]

if __name__ == '__main__':
    game = Game()
    #C = Chessboard('rnb1qbnr/pppPk1p1/7p/5p2/4P3/8/PPPP2PP/RNBQKBNR w KQ - 1 6')
    #C = Chessboard('r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/3B1N2/PPPP1PPP/RNBQK2R w KQkq - 4 4')
    #print(game)
    while True:
        game.turn()

        if game.checkmate():
            game.PGN += '#'
            if game.active == 'w':
                game.PGN += ' 0-1'
            else:
                game.PGN += ' 1-0'
            print(game)
            print(f'{game.passive.upper()} wins the match by checkmate!')
            break

        elif game.board.inCheck(game.active):
            game.PGN += '+'

        elif game.stalemate():
            game.PGN += ' 0.5-0.5'
            print(game)
            print('Draw by stalemate.')
            break