import random
import time
from typing import Tuple
from config.settings import Config


class Menace:
    """
    Classe représentant une menace mobile dans la simulation.
    Les menaces se déplacent aléatoirement et possèdent une puissance.
    """

    def __init__(self):
        self.position = self._generate_random_position()  # Position initiale
        self.color = (255, 0, 0)  # Rouge pour représenter la menace
        self.size = 20 # Taille de la menace
        self.power = random.randint(3, 5)  # Puissance aléatoire entre 3 et 5
        self.direction = self._random_direction()  # Direction initiale
        self.direction_time = time.time()  # Dernier changement de direction
        self.direction_duration = random.uniform(1, 3)  # Temps avant de changer de direction
        self.speed = 1.0  # Vitesse de déplacement

    def _generate_random_position(self) -> Tuple[int, int]:
        """
        Génère une position aléatoire pour la menace dans les limites de la carte.
        """
        return (
            random.randint(0, Config.WINDOW_WIDTH),
            random.randint(0, Config.WINDOW_HEIGHT)
        )

    def _random_direction(self) -> Tuple[float, float]:
        """
        Génère une direction aléatoire normalisée.
        """
        return (
            random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'],
            random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer']
        )

    def move(self) -> None:
        """
        Déplace la menace dans une direction constante pendant un temps donné,
        puis change de direction de manière aléatoire.
        """
        # Changer de direction après un temps aléatoire
        if time.time() - self.direction_time >= self.direction_duration:
            self.direction = self._random_direction()
            self.direction_time = time.time()
            self.direction_duration = random.uniform(1, 3)

        # Calculer la nouvelle position avec la direction actuelle
        dx, dy = self.direction
        self.position = (
            max(0, min(self.position[0] + dx * self.speed, Config.WINDOW_WIDTH)),
            max(0, min(self.position[1] + dy * self.speed, Config.WINDOW_HEIGHT))
        )
