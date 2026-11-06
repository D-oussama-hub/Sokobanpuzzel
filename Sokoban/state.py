from Sokoban.moves import successor_function


class SokobanPuzzle:

    def __init__(self, grid):
        self.grid = grid
        self.player = self.find_player()

    def find_player(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] == 'R' or self.grid[i][j] == '.':
                    return (i, j)

    def isGoal(self):
        for row in self.grid:
            if 'B' in row:
                return False
        return True

    def boxes_left(self):
        #Caisses pas encore sur une cible ('B')
        return [(i, j)
                for i in range(len(self.grid))
                for j in range(len(self.grid[i]))
                if self.grid[i][j] == 'B']

    def free_targets(self):
        #Cibles libres : 'S' ou '.' (joueur dessus)
        return [(i, j)
                for i in range(len(self.grid))
                for j in range(len(self.grid[i]))
                if self.grid[i][j] in ('S', '.')]

    def successorFunction(self):
        return successor_function(self)

    def __eq__(self, other):
        return self.grid == other.grid

    def __hash__(self):
        return hash(tuple("".join(row) for row in self.grid))