from pos import Pos

class Piece:

    def __init__(self, role, col):
        #w, b
        self.col = col
        self.opcol = 'b' if self.col == 'w' else 'w'

        self.role = role.lower() #q, r, b, n, k or p 
        #pawn moving direction
        self.dir = None
        if self.role == 'p':
            if self.col == 'w':
                self.dir = 1
            else:
                self.dir = -1

    def __str__(self):
        if self.col == 'w':
            return self.role.upper()
        
        else:
            return self.role
    
    def canMove(self, pos, newpos):
        #assuming the necessary conditions/board position, can the piece move that way?
        if self.role == 'p':
            #normal move / capture
            if newpos.rank == pos.rank + self.dir and pos.isAdjacent(newpos):
                return True
            
            #initial two square advance
            elif newpos.rank == pos.rank + 2 * self.dir and pos.isSameFile(newpos):
                if self.col == 'w' and pos.rank == 2:
                    return True
                
                elif self.col == 'b' and pos.rank == 7:
                    return True
            
            else:
                return False
        
        elif self.role == 'n':
            return pos.fileDistance(newpos) + pos.rankDistance(newpos) == 3 and pos.distance(newpos) == 2

        elif self.role == 'r':
            return pos.isSameFile(newpos) or pos.isSameRank(newpos)

        elif self.role == 'b':
            return pos.isSameDiag(newpos)

        elif self.role == 'q':
            return pos.isSameDiag(newpos) or pos.isSameFile(newpos) or pos.isSameRank(newpos)

        elif self.role == 'k':
            if pos.isAdjacent(newpos):
                return True
            
            #castles
            elif pos.isSameRank(newpos) and pos.fileDistance(newpos) == 2:
                return (self.col == 'w' and pos == Pos(sqr='e1')) or (self.col == 'b' and pos == Pos(sqr='e8'))

        else:
            return False

    def isAttackingSquare(self, pos, newpos):
        if self.role == 'p':
            return newpos.rank == pos.rank + self.dir and pos.fileDistance(newpos) == 1
        
        else:
            return self.canMove(pos, newpos)

    def squaresInReach(self, pos):
        """Return list of squares the piece can reach."""
        squares = []
        if self.role == 'p':
            squares = [pos + diff for diff in [Pos(self.dir, -1), Pos(self.dir, 0), Pos(self.dir, 1), Pos(2*self.dir, 0)]]

        elif self.role == 'n':
            squares = [pos + Pos(x, y) for x in [1, -1] for y in [2, -2]] + [pos + Pos(x, y) for y in [1, -1] for x in [2, -2]]

        elif self.role == 'b':
            squares = [Pos(i, pos.j - pos.i + i) for i in range(8)] + [Pos(i, pos.j + pos.i - i) for i in range(8)]

        elif self.role == 'r':
            squares = [Pos(pos.i, y) for y in range(8)] + [Pos(x, pos.j) for x in range(8)]

        elif self.role == 'q':
            squares = Piece('r', col='w').squaresInReach(pos) + Piece('b', col='w').squaresInReach(pos)

        elif self.role == 'k':
            squares = [pos + Pos(x, y) for x in range(-1, 2) for y in range(-1, 2)] + [pos + Pos(0, 2), pos + Pos(0, -2)]

        return [sqr for sqr in squares if sqr.isOnBoard()]