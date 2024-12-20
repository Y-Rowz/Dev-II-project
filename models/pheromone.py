from typing import Tuple
from models.food import Food
from config.settings import Config


class Pheromone:
    def __init__(self, position: Tuple[float, float], food_source, food_number: int, alert=False, expiration_time=None):
        self.position = position
        self.food_source = food_source
        self.food_number = food_number
        self.alert = alert
        self.expiration_time = expiration_time
        
        # Définir une taille en fonction du type de phéromone
        if alert:
            self.size = 40  # Taille pour une phéromone d'alerte
        else:
            self.size = 5  # Taille pour une phéromone normale liée à la nourriture