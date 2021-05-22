from piece import Piece
from pos import Pos

class Board:

    def __init__(self, fenPos='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', castleRight={char: True for char in 'KQkq'}, enpassantPossible=None):
        rows = fenPos.split('/')
        rows.reverse()
        self.pieces = {}
        for i, row in enumerate(rows):
            j = 0
            for char in row:
                if char.isdigit():
                    j += int(char)

                elif char.isalpha():
                    col = 'w' if char.isupper() else 'b'
                    self.pieces[Pos(i, j)] = Piece(char, col)
                    j += 1

        self.castleRight = castleRight
        self.enpassantPossible = enpassantPossible

    def __call__(self, pos):
        """Returns Piece Object at given position."""
        if pos.isOnBoard() and pos in self.pieces:
            return self.pieces[pos]
        
        return None

    def isEmpty(self, pos):
        """Returns wether a certain square is empty."""
        return pos not in self.pieces

    def sqrStr(self, pos):
        if self.isEmpty(pos):
            return '.'
        else:
            return str(self(pos))

    def __str__(self):
        #convert pieces to strings
        matrix = [[self.sqrStr(Pos(i, j)) for j in range(8)] for i in range(8)]
        #add files and ranks
        printmatrix = [[str(8-i)] + row for i, row in enumerate(reversed(matrix))]
        printmatrix += [[' '] + [chr(i+65) for i in range(8)]]
        return '\n'.join(' '.join(row) for row in printmatrix)

    def fenPos(self):
        position = []
        for i in range(8):
            rowString = ''
            emptiesCount = 0
            prevEmpty = False
            for j in range(8):
                if self.isEmpty(Pos(i, j)):
                    emptiesCount += 1
                    prevEmpty = True
                
                else:
                    if prevEmpty:
                        rowString += str(emptiesCount)
                        emptiesCount = 0
                    
                    prevEmpty = False
                    rowString += str(self(Pos(i, j)))
            
            if prevEmpty:
                rowString += str(emptiesCount)

            position.append(rowString)
       
        return '/'.join(reversed(position))

    def copy(self):
        return Board(self.fenPos(), self.castleRight, self.enpassantPossible)

    def setEmpty(self, pos):
        self.pieces.pop(pos)

    def setPiece(self, pos, role, col):
        self.pieces[pos] = Piece(role, col)

    def movePiece(self, pos, newpos):
        self.pieces[newpos] = self.pieces.pop(pos)

    def populatedSquares(self):
        """Return a list of all non-empty squares."""
        return [pos for pos in self.pieces if not self.isEmpty(pos)]

    def squaresOfPlayer(self, col):
        """Return a list of all squares accommodating a piece of this player."""
        return [pos for pos in self.populatedSquares() if self(pos).col == col]

    def king(self, col):
        """Return position of King of this color."""
        return [pos for pos in self.squaresOfPlayer(col) if self(pos).role == 'k'].pop()

    def inCheck(self, col):
        """Is this King in check?"""
        king = self.king(col)
        oppPieceSquares = self.squaresOfPlayer(self(king).opcol)
        return any(self(pos).isAttackingSquare(pos, king) and self.isPathClear(pos, king) for pos in oppPieceSquares)

    def isPathClear(self, pos, newpos):
        """Returns True if the squares between current and target square are empty and there's no piece of same color on the target square."""
        piece = self(pos)
        target = self(newpos)
        if piece.role == 'n':
            return not target or self(newpos).col != piece.col

        path = pos.path(newpos)
        
        if any(not self.isEmpty(pos) for pos in path[1:-1]):
            return False
        
        if target and (target.col == piece.col or (piece.role == 'p' and pos.isSameFile(newpos) and target.col == piece.opcol)):
            return False

        return True