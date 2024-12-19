from typing import Tuple
import pygame
from config.settings import Config


class Queen:
    """
    Représente la reine de la colonie de fourmis.
    Dans cette simulation, la reine est principalement un élément visuel 
    sans logique comportementale complexe.
    
    PRE: position est un tuple de coordonnées valides
    POST: Initialise la reine à la position spécifiée
    """
    def __init__(self, position: Tuple[float, float]):
        """
        Initialise une instance de la reine.

        PRE: position est un tuple de coordonnées valides (x, y)
        POST: La reine est créée et positionnée aux coordonnées spécifiées
        """
        self.position = position
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Dessine la reine sur l'écran pygame
        
        PRE: screen est une surface pygame valide
        POST: Dessine un cercle représentant la reine à sa position
        """
        pygame.draw.circle(screen, Config.COLORS['queen'],
                         (int(self.position[0]), int(self.position[1])),
                         Config.SIZES['queen'])
