from models.ant import Ant
from config.settings import Config
import math

class Ouvriere(Ant):
    def __init__(self, position):
        super().__init__(position)
        self.color = (0, 0, 0)  # Vert pour les ouvrières
        self.size = Config.SIZES['ant']  # Taille standard des fourmis

    def perform_action(self, simulation) -> None:
        if self.get_state() == "searching":
            # Recherche normale de nourriture
            if not simulation._detect_pheromone(self):
                self.move_randomly(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
                simulation._detect_food(self)

        elif self.get_state() == "returning_to_nest":
            simulation._process_return_to_nest(self)

        elif self.get_state() == "going_to_food":
            simulation._process_return_to_food(self)

        # Vérifie si l'ouvrière touche une phéromone d'alerte
        for pheromone in simulation.pheromones:
            distance = math.hypot(self.position[0] - pheromone.position[0], self.position[1] - pheromone.position[1])
            if pheromone.alert and distance < pheromone.size:
                self.target_position = simulation.nest.position
                self.state = "returning_to_nest"
                print(f"Ouvrière détecte une phéromone d'alerte à {pheromone.position} et retourne au nid.")