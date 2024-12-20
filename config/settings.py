class Config:
    """
    Classe de configuration centralisant tous les paramètres constants du jeu.
    Cette approche permet de modifier facilement les paramètres du jeu 
    sans changer la logique principale de la simulation.
    
    Sections principales :
    - WINDOW_WIDTH/HEIGHT : Définissent la zone d'affichage de la simulation
    - COLORS : Définissent la palette de couleurs des différents éléments du jeu
    - SIZES : Définissent les tailles des différents objets du jeu
    - GAME_SETTINGS : Paramètres configurables de la mécanique du jeu
    
    PRE: /
    POST: Initialise une configuration statique pour la simulation
    """
    WINDOW_WIDTH = 1366
    WINDOW_HEIGHT = 768
    
    # Palette de couleurs utilisant des tuples RGB pour les differents éléments de la simulation
    COLORS = {
        'background': (181, 101, 29),
        'food': (0, 255, 0),
        'nest': (101, 67, 33),
        'ant': (0, 0, 0),
        'queen': (0, 0, 0),
        'pheromone': (200, 200, 255),
        'text': (255, 255, 255)
    }
    
    # Tailles définissant l'échelle de rendu
    SIZES = {
        'food': 20,
        'nest': 50,
        'ant': 4,
        'queen': 10,
        'pheromone': 5
    }
    
    # contrôler la dynamique de la simulation
    GAME_SETTINGS = {
        'food_count': 5,
        'ant_count': 20,
        'speed_reducer': 30,
        'pheromone_detection_distance': 15,
        'min_pheromone_distance': 30,
        'max_nest_resources': 100
    }
