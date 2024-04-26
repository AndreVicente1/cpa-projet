class Node:
    """Représente un noeud dans le graphe utilisé pour A*"""
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # coût du chemin depuis le point de départ
        self.h = 0  # estimation du coût vers le point d'arrivée
        self.f = 0  # coût total (g + h)
    
    def __eq__(self, other):
        return self.position == other.position

def manhattan(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def astar(start, end, grid):
    """Algorithme A* pour trouver le chemin le plus court entre deux points sur une grille"""

    lst = []
    closed_set = set() # Noeuds déjà visités

    start_node = Node(start)
    end_node = Node(end)

    lst.append(start_node)

    while lst:
        current_node = min(lst, key=lambda o: o.f) # Noeud avec le plus petit f dans lst
        lst.remove(current_node)
        closed_set.add(tuple(current_node.position)) # Ajoute la position actuelle aux fermés

        if tuple(current_node.position) == tuple(end_node.position):
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # chemin inversé

        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Voisins
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # position impossible
            if node_position[0] > (len(grid) - 1) or node_position[0] < 0 or node_position[1] > (len(grid[0]) - 1) or node_position[1] < 0:
                continue
            # mur (ou ennemi)
            if grid[node_position[0]][node_position[1]] != 0:
                continue

            new_node = Node(node_position, current_node)

            if tuple(new_node.position) in closed_set:
                continue

            new_node.g = current_node.g + 1
            new_node.h = manhattan(new_node.position, end_node.position)
            new_node.f = new_node.g + new_node.h

            # On ajoute le nouveau noeud à open_list s'il n'y est pas déjà avec un g inférieur
            if any(child for child in lst if child.position == new_node.position and child.g <= new_node.g):
                continue

            lst.append(new_node)

