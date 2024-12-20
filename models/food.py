from typing import Tuple
import random


class Food:
    """
    Représente une source de nourriture dans la simulation.
    Chaque source de nourriture a une quantité initiale de ressources aléatoire 
    et peut être épuisée.
    
    PRE: position est un tuple de coordonnées valides, number est un entier
    POST: Initialise une source de nourriture avec des ressources aléatoires
    """
    def __init__(self, position: Tuple[float, float], number: int):
        self.position = position
        self.resources = random.randint(10, 50)  # ressources initiales aléatoires entre les valeurs indiquées
        self.pheromone_path_active = True
        self.number = number
    
    def take_resource(self) -> None:
        """
        Diminue les ressources lorsqu'une fourmi collecte de la nourriture
        
        PRE: resources > 0
        POST: Diminue les ressources de 1
        """
        if self.resources > 0:
            self.resources -= 1
    
    def is_empty(self) -> bool:
        """
        Vérifie si la source de nourriture est complètement épuisée
        
        PRE: /
        POST: Retourne True si resources <= 0, False sinon
        """
        return self.resources <= 0
