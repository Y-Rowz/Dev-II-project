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
        self.position = position
        self.food_source = food_source
        self.food_number = food_number
