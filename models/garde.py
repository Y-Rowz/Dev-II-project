from models.ant import Ant
from config.settings import Config
from typing import Tuple
import math

class Garde(Ant):
    def __init__(self, position):
        super().__init__(position)
        self.color = (0, 0, 255)  # Bleu pour les gardes
        self.size = Config.SIZES['ant'] + 2  # Taille légèrement plus grande
        self.target_position = None  # Position cible pour attaquer une menace
        self.is_attacking = False  # Indique si le garde est en mission d'attaque

    def perform_action(self, simulation) -> None:
        if self.is_attacking and self.target_position:
            # Déplacement vers la menace
            simulation._move_to_target(self, self.target_position)

            # Vérifie si le garde touche la menace
            for menace in simulation.menaces:
                distance = math.hypot(self.position[0] - menace.position[0], self.position[1] - menace.position[1])
                if distance < menace.size:
                    menace.power -= 1
                    print(f"Garde attaque la menace à {menace.position}. Puissance restante : {menace.power}")
                    simulation.ants.remove(self)  # Le garde disparaît après l'attaque
                    if menace.power <= 0:
                        simulation.menaces.remove(menace)
                        simulation._spawn_food(menace.position)
                        print(f"La menace à {menace.position} a été éliminée.")
                    return