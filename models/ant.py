from typing import Tuple
import random
import time
from config.settings import Config


class Ant:
    """
    Représente une fourmi individuelle dans la simulation.
    Gère le comportement et les déplacements de la fourmi.
    
    PRE: position est un tuple de coordonnées valides
    POST: Initialise une fourmi avec une position et une direction aléatoires
    """
    def __init__(self, position: Tuple[float, float]):
        self.position = position
        self.has_food = False  # indique si la fourmi transporte de la nourriture (initialement non)
        self.direction = self._random_direction()  #direction initiale aléatoire
        self.direction_time = time.time()  # temps du dernier changement de direction
        self.direction_duration = random.uniform(0.5, 2)  # durée avant le prochain changement de direction
        self.target_food = None  # source de nourriture ciblée
        self.emitting_pheromones = False  # indique si la fourmi laisse des phéromones
        self.food_number = 0  # Id de la source de nourriture
    
    def _random_direction(self) -> Tuple[float, float]:
        """
        Génère une direction de déplacement aléatoire
        
        PRE: /
        POST: Retourne un tuple de direction aléatoire normalisé
        """
        return (random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'],
                random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'])
    
    def get_state(self) -> str:
        """
        Renvoie l'état actuel de la fourmi
        
        PRE: /
        POST: Retourne une chaîne décrivant l'état de la fourmi
        """
        if self.has_food:
            return "returning_to_nest"
        elif self.target_food:
            return "going_to_food"
        return "searching"
    
    def move_randomly(self, width: int, height: int) -> None:
        """
        Déplacement aléatoire de la fourmi dans les limites de l'écran
        
        PRE: width et height sont des entiers positifs représentant les limites de l'écran
        POST: Met à jour la position de la fourmi dans les limites de l'écran
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
