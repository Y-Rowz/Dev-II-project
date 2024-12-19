from typing import Tuple
from models.food import Food


class Pheromone:
    """
    Représente un marqueur de phéromones dans la simulation.
    Les phéromones guident les fourmis vers les sources de nourriture.
    
    PRE: position est un tuple de coordonnées valides
    POST: Initialise un marqueur de phéromones associé à une source de nourriture
    """
    def __init__(self, position: Tuple[float, float], food_source, food_number: int):
        self.position = position  #position du marqueur de phéromones
        self.food_source = food_source  # source de nourriture associée
        self.food_number = food_number  # numéro de la source de nourriture
