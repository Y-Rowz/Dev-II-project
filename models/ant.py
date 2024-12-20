from typing import Tuple
import random
import time
from config.settings import Config

class Ant:
    """
    Représente une fourmi individuelle dans la simulation.
    """

    def __init__(self, position: Tuple[float, float]):
        self.position = position
        self.has_food = False
        self.direction = self._random_direction()
        self.direction_time = time.time()
        self.direction_duration = random.uniform(0.5, 2)
        self.target_food = None
        self.emitting_pheromones = False
        self.food_number = 0
        self.state = "searching"  # État initial de la fourmi

    def _random_direction(self) -> Tuple[float, float]:
        return (random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'],
                random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'])

    def move_randomly(self, width: int, height: int) -> None:
        """
        Déplacement aléatoire de la fourmi dans les limites de l'écran.

        PRE: width et height sont des entiers positifs représentant les limites de l'écran.
        POST: Met à jour la position de la fourmi dans les limites de l'écran.
        """
        if time.time() - self.direction_time >= self.direction_duration:
            # Changement de direction après un certain temps
            self.direction = self._random_direction()
            self.direction_time = time.time()
            self.direction_duration = random.uniform(0.5, 1.5)

        # Calcul de la nouvelle position en restant dans les limites
        new_x = max(0, min(self.position[0] + self.direction[0], width))
        new_y = max(0, min(self.position[1] + self.direction[1], height))
        self.position = (new_x, new_y)

    def get_state(self) -> str:
        """
        Retourne l'état actuel de la fourmi.
        """
        return self.state

    def set_state(self, new_state: str) -> None:
        """
        Met à jour l'état de la fourmi.

        PRE: new_state est une chaîne valide ("searching", "returning_to_nest", "going_to_food", etc.)
        POST: L'état de la fourmi est mis à jour.
        """
        self.state = new_state
        print(f"État mis à jour : {self.state}")

    def perform_action(self, simulation) -> None:
        """
        Par défaut, les fourmis ne font rien. Cette méthode est redéfinie dans les sous-classes.
        """
        pass
