class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = 0 if parent is None else parent.g + 1      # coût d'un pas = 1
        self.f = 0

    def setF(self, heuristic):
        #f = g + h
        self.f = self.g + heuristic(self.state)

    def getPath(self):
        path = []
        node = self
        while node is not None:
            path.append(node.state)
            node = node.parent
        path.reverse()
        return path

    def getSolution(self):
        actions = []
        node = self
        while node.parent is not None:
            actions.append(node.action)
            node = node.parent
        actions.reverse()
        return actions