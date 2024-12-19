from typing import Tuple
from config.settings import Config


class Nest:
    """
    Représente le nid de la colonie de fourmis.
    Suit les ressources accumulées et a une capacité maximale.
    
    PRE: position est un tuple de coordonnées valides
    POST: Initialise le nid à la position spécifiée avec 0 ressources
    """
    def __init__(self, position: Tuple[float, float]):
        self.position = position
        self.resources = 0
    
    def add_resource(self) -> None:
        """
        Ajoute une ressource au nid, en respectant la capacité maximale
        
        PRE: /
        POST: Incrémente les ressources du nid jusqu'à la capacité maximale
        """
        self.resources = min(Config.GAME_SETTINGS['max_nest_resources'], self.resources + 1)
    
    def is_full(self) -> bool:
        """
        Vérifie si le nid a atteint sa capacité maximale de ressources
        
        PRE: /
        POST: Retourne True si resources >= capacité maximale, False sinon
        """
        return self.resources >= Config.GAME_SETTINGS['max_nest_resources']