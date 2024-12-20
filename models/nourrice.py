from models.ant import Ant
from config.settings import Config
import time
import random
import math
from models.ouvriere import Ouvriere
from models.garde import Garde


class Nourrice(Ant):
    """
    Classe représentant les fourmis nourrices.
    Elles restent dans le nid et utilisent la nourriture du nid pour créer de nouvelles fourmis.
    """

    def __init__(self, position):
        super().__init__(position)
        self.color = (255, 105, 180)  # Rose pour les nourrices
        self.size = Config.SIZES['ant']  # Taille standard des fourmis
        self.stack = 0  # Nombre de stacks créés par cette nourrice
        self.last_stack_time = time.time()  # Dernière fois qu'un stack a été créé
        self.direction = self._random_direction()  # Direction initiale
        self.direction_time = time.time()  # Dernier changement de direction
        self.direction_duration = random.uniform(0.5, 2)  # Temps avant de changer de direction
        self.speed = 0.5  # Réduction de vitesse pour les nourrices

    def perform_action(self, simulation) -> None:
        """
        Effectue les actions des nourrices :
        - Restent dans le nid.
        - Produisent des stacks si le nid a de la nourriture.
        - Aident à spawner de nouvelles fourmis.
        """
        self._move_within_nest(simulation.nest)

        # Produire un stack toutes les 15 secondes si de la nourriture est disponible
        if time.time() - self.last_stack_time >= 15 and simulation.nest.resources > 0:
            self.stack += 1
            simulation.nest.resources -= 1  # Décrémente la nourriture du nid
            self.last_stack_time = time.time()
            print(f"Nourrice a créé un stack. Stacks actuels : {self.stack}. Ressources restantes : {simulation.nest.resources}")

        # Vérifier si le total des stacks permet de créer une nouvelle fourmi
        self._check_and_spawn_new_ant(simulation)

    def _move_within_nest(self, nest):
        """
        Déplace la nourrice à l'intérieur des limites du nid.
        """
        # Changer de direction après un temps aléatoire
        if time.time() - self.direction_time >= self.direction_duration:
            self.direction = self._random_direction()
            self.direction_time = time.time()
            self.direction_duration = random.uniform(0.5, 2)  # Nouvelle durée avant changement

        # Calculer la nouvelle position avec la direction actuelle
        dx, dy = self.direction
        new_position = (
            self.position[0] + dx * self.speed,
            self.position[1] + dy * self.speed
        )

        # Vérifier si la nouvelle position est à l'intérieur des limites du nid
        distance_to_nest_center = math.hypot(new_position[0] - nest.position[0], new_position[1] - nest.position[1])
        if distance_to_nest_center <= Config.SIZES['nest']:
            self.position = new_position  # Met à jour la position uniquement si elle est dans le nid

    def _random_direction(self) -> tuple:
        """
        Génère une direction aléatoire normalisée.
        """
        return (
            random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'],
            random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer']
        )

    def _check_and_spawn_new_ant(self, simulation):
        """
        Vérifie si le total des stacks permet de créer une nouvelle fourmi.
        Si oui, une nouvelle fourmi est créée, et les stacks sont réinitialisés.
        """
        total_stacks = sum(nourrice.stack for nourrice in simulation.ants if isinstance(nourrice, Nourrice))

        if total_stacks >= 3:  # Si 3 stacks sont accumulés
            print("3 stacks accumulés, création d'une nouvelle fourmi.")
            
            # Réinitialise les stacks de toutes les nourrices
            for nourrice in simulation.ants:
                if isinstance(nourrice, Nourrice):
                    nourrice.stack = 0

            # Crée une nouvelle fourmi avec des chances différentes pour les rôles
            position = simulation.nest.position
            roll = random.random()
            if roll < 0.25:
                simulation.ants.append(Nourrice(position))
                print("Une nouvelle nourrice a été créée.")
            elif roll < 0.50:
                simulation.ants.append(Garde(position))
                print("Un nouveau garde a été créé.")
            else:
                simulation.ants.append(Ouvriere(position))
                print("Une nouvelle ouvrière a été créée.")
