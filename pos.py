import numpy as np

class Pos:

    def __init__(self, i=0, j=0, sqr=''):
        #i, j matrix coordinates of position
        self.i, self.j = i, j
        if sqr:
            #handling fen input
            if sqr == '-':
                self.i, self.j = -1, -1
                return

            #converting algebraic square name to matrix coordinates
            sqr = sqr.upper()
            self.i = int(sqr[1]) - 1
            self.j = ord(sqr[0]) - 65
        
        self.rank = self.i + 1
        self.filenr = self.j + 1
        self.file = chr(self.j + 97)

    def __str__(self):
        if self.i == -1 == self.j:
            return '-'
        else:
            return self.file + str(self.rank)

    def __eq__(self, other):
        return self.i == other.i and self.j == other.j

    def __add__(self, other):
        return Pos(self.i + other.i, self.j + other.j)

    def __hash__(self):
        return 10*self.i + self.j

    def isOnBoard(self):
        return 0 <= self.i < 8 and 0 <= self.j < 8 

    def isSameFile(self, other):
        return self.file == other.file
    
    def isSameRank(self, other):
        return self.rank == other.rank

    def isSameDiag(self, other):
        return abs(self.rank - other.rank) == abs(self.filenr - other.filenr)
    
    def distance(self, other):
        """Induced by maximum norm."""
        return max(abs(self.rank - other.rank), abs(self.filenr - other.filenr))
    
    def fileDistance(self, other):
        return abs(self.filenr - other.filenr)

    def rankDistance(self, other):
        return abs(self.rank - other.rank)

    def isAdjacent(self, other):
        return self.distance(other) <= 1

    def path(self, newpos):
        """Returns list of passed squares (coords) for straight or diagonal moves in the order they're passed."""
        #rank ~ row ~ x, file ~ column ~ y
        x, X = self.i, newpos.i
        y, Y = self.j, newpos.j
        xdir, ydir = np.sign(X - x), np.sign(Y - y)

        #straight
        if xdir == 0 and ydir != 0:
            return [Pos(x, b) for b in range(y, Y + ydir, ydir)]

        elif xdir != 0 and ydir == 0:
            return [Pos(a, y) for a in range(x, X + xdir, xdir)]

        #diagonal
        elif abs(X - x) == abs(Y - y) > 0:
            #return list(zip(range(x, X + xdir, xdir), range(y, Y + ydir, ydir)))
            return [Pos(a, b) for a, b in zip(range(x, X + xdir, xdir), range(y, Y + ydir, ydir))]

        print('Squares not on one line.', self, newpos)