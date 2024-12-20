import pygame
import random
import math
from typing import List, Tuple
from config.settings import Config
from models.ant import Ant
from models.food import Food
from models.nest import Nest
from models.pheromone import Pheromone
from models.queen import Queen


class AntColonySimulation:
    """
    Classe principale gérant la simulation complète de la colonie de fourmis.

    PRE: /
    POST: Initialise tous les composants nécessaires pour la simulation
    RAISE:
    - pygame.error si l'initialisation de Pygame échoue
    """
    def __init__(self):
        """
        Initialise les composants principaux de la simulation.

        PRE: /
        POST:
        - Pygame est initialisé
        - Fenêtre de jeu créée
        - Nid, reine, sources de nourriture et fourmis générés
        """
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Simulation de Colonie de Fourmis - MVP")

        self.font = pygame.font.SysFont(None, 24)
        self.win_font = pygame.font.SysFont(None, 72)

        self.nest = Nest((
            random.randint(0, Config.WINDOW_WIDTH),
            random.randint(0, Config.WINDOW_HEIGHT)
        ))

        self.queen = Queen((
            self.nest.position[0] + 10,
            self.nest.position[1] + 10
        ))

        self.food_sources = self._create_food_sources()
        self.ants = self._create_ants()
        self.pheromones: List[Pheromone] = []

        self.running = True
        self.victory = False

    def _create_food_sources(self) -> List[Food]:
        """
        Méthode privée pour créer un ensemble de sources de nourriture.

        PRE: Configuration des paramètres de jeu disponible
        POST:
        - Retourne une liste de sources de nourriture générées aléatoirement
        - Chaque source a une position unique sur l'écran
        """
        return [
            Food((
                random.randint(0, Config.WINDOW_WIDTH),
                random.randint(0, Config.WINDOW_HEIGHT)
            ), i + 1)
            for i in range(Config.GAME_SETTINGS['food_count'])
        ]

    def _create_ants(self) -> List[Ant]:
        """
        Méthode privée pour créer la population initiale de fourmis.

        PRE: Configuration des paramètres de jeu et nid initialisés
        POST:
        - Retourne une liste de fourmis générées
        - Chaque fourmi est positionnée à proximité du nid
        """
        return [
            Ant(self._random_nest_position())
            for _ in range(Config.GAME_SETTINGS['ant_count'])
        ]

    def _random_nest_position(self) -> Tuple[float, float]:
        """
        Génère une position aléatoire à proximité du nid pour les fourmis.

        PRE: Nid déjà initialisé
        POST:
        - Retourne des coordonnées x et y à proximité du nid
        - Position générée de manière aléatoire dans un rayon défini
        """
        return (
            self.nest.position[0] + random.randint(
                -Config.SIZES['nest'],
                Config.SIZES['nest']
            ),
            self.nest.position[1] + random.randint(
                -Config.SIZES['nest'],
                Config.SIZES['nest']
            )
        )

    def update(self) -> None:
        """
        Méthode principale de mise à jour de la simulation.

        PRE: Simulation initialisée et en cours
        POST:
        - Comportement des fourmis mis à jour
        - Conditions de victoire vérifiées
        """
        self._process_ants()
        self._check_victory()

    def _process_ants(self) -> None:
        """
        Gère le comportement de chaque fourmi selon son état actuel.

        PRE: Liste des fourmis initialisée
        POST:
        - État et position de chaque fourmi mis à jour
        - Interactions avec l'environnement (nourriture, phéromones) traitées
        """
        for ant in self.ants:
            if ant.get_state() == "searching":
                if not self._detect_pheromone(ant):
                    ant.move_randomly(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
                    self._detect_food(ant)
            elif ant.get_state() == "returning_to_nest":
                self._process_return_to_nest(ant)
            elif ant.get_state() == "going_to_food":
                self._process_return_to_food(ant)

    def _detect_food(self, ant: Ant) -> bool:
        """
        Vérifie si une fourmi est à proximité d'une source de nourriture.

        PRE:
        - Fourmi en mode recherche
        - Liste des sources de nourriture initialisée
        POST:
        - Retourne True si nourriture détectée, False sinon
        - Gère la collecte de ressources si une source est proche
        """
        for food in self.food_sources:
            distance = math.hypot(
                ant.position[0] - food.position[0],
                ant.position[1] - food.position[1]
            )

            if distance < Config.SIZES['food']:
                if food.pheromone_path_active:
                    ant.has_food = True
                    ant.target_food = food
                    food.take_resource()
                    ant.emitting_pheromones = True
                    food.pheromone_path_active = False
                    ant.food_number = food.number
                elif not food.is_empty():
                    ant.has_food = True
                    ant.target_food = food
                    food.take_resource()
                    ant.food_number = food.number
                return True
        return False

    def _detect_pheromone(self, ant: Ant) -> bool:
        """
        Permet à une fourmi de détecter les traces de phéromones.

        PRE:
        - Liste des phéromones initialisée
        - Fourmi en mode "searching"
        POST:
        - Retourne True si phéromone détectée, False sinon
        - Définit la cible de nourriture si une phéromone est trouvée
        """
        for pheromone in self.pheromones:
            distance = math.hypot(
                ant.position[0] - pheromone.position[0],
                ant.position[1] - pheromone.position[1]
            )

            if distance < Config.GAME_SETTINGS['pheromone_detection_distance']:
                ant.target_food = pheromone.food_source
                return True
        return False

    def _process_return_to_nest(self, ant: Ant) -> None:
        """
        Gère le déplacement d'une fourmi transportant de la nourriture vers le nid.

        PRE:
        - Fourmi en mode retour au nid
        - Nid initialisé
        POST:
        - Fourmi se déplace vers le nid
        - Phéromones déposées si nécessaire
        - Ressources ajoutées au nid si la fourmi y arrive
        """
        dx = self.nest.position[0] - ant.position[0]
        dy = self.nest.position[1] - ant.position[1]
        distance = math.hypot(dx, dy)

        if distance > 0:
            speed = 5 / Config.GAME_SETTINGS['speed_reducer']
            ant.position = (
                ant.position[0] + (dx / distance) * speed,
                ant.position[1] + (dy / distance) * speed
            )

            if ant.emitting_pheromones:
                self._add_pheromone(ant)

        if distance < Config.SIZES['nest'] and ant.has_food:
            self.nest.add_resource()
            ant.has_food = False
            ant.emitting_pheromones = False

    def _process_return_to_food(self, ant: Ant) -> None:
        """
        Gère le déplacement d'une fourmi vers une source de nourriture ciblée.

        PRE:
        - Fourmi en mode recherche de nourriture
        - Source de nourriture ciblée existe
        POST:
        - Fourmi se déplace vers la source de nourriture
        - Ressources collectées si la source est atteinte
        - Gestion de l'épuisement des sources de nourriture
        """
        if not ant.target_food or ant.target_food not in self.food_sources:
            ant.target_food = None
            ant.food_number = 0
            return

        dx = ant.target_food.position[0] - ant.position[0]
        dy = ant.target_food.position[1] - ant.position[1]
        distance = math.hypot(dx, dy)

        if distance > 0:
            speed = 5 / Config.GAME_SETTINGS['speed_reducer']
            ant.position = (
                ant.position[0] + (dx / distance) * speed,
                ant.position[1] + (dy / distance) * speed
            )

        if distance < Config.SIZES['food'] and not ant.target_food.is_empty():
            ant.has_food = True
            ant.target_food.take_resource()

            if ant.target_food.is_empty():
                self._remove_food_pheromones(ant.target_food.number)
                self.food_sources.remove(ant.target_food)
                ant.target_food = None
                ant.food_number = 0

    def _add_pheromone(self, ant: Ant) -> None:
        """
        Ajoute une trace de phéromone laissée par une fourmi.

        PRE:
        - Fourmi transportant de la nourriture
        - Liste des phéromones initialisée
        POST:
        - Nouvelle phéromone ajoutée si la distance minimale est respectée
        """
        if not self.pheromones:
            self.pheromones.append(
                Pheromone(ant.position, ant.target_food, ant.food_number)
            )
            return

        last_pheromone_distance = math.hypot(
            ant.position[0] - self.pheromones[-1].position[0],
            ant.position[1] - self.pheromones[-1].position[1]
        )
        if last_pheromone_distance > Config.GAME_SETTINGS['min_pheromone_distance']:
            self.pheromones.append(
                Pheromone(ant.position, ant.target_food, ant.food_number)
            )

    def _remove_food_pheromones(self, food_number: int) -> None:
        """
        Supprime les phéromones associées à une source de nourriture épuisée.

        PRE:
        - Source de nourriture épuisée
        - Liste des phéromones initialisée
        POST:
        - Phéromones liées à la source de nourriture supprimées
        """
        self.pheromones = [
            p for p in self.pheromones if p.food_number != food_number
        ]

    def _check_victory(self) -> None:
        """
        Vérifie si la colonie a atteint son objectif de ressources.

        PRE:
        - Nid initialisé
        - Simulation en cours
        POST:
        - Drapeau de victoire mis à jour si objectif atteint
        """
        if self.nest.is_full():
            self.victory = True

    def render(self) -> None:
        """
        Méthode principale de rendu graphique de la simulation.

        PRE:
        - L'écran Pygame est initialisé
        - Tous les éléments de la simulation sont créés
        POST:
        - L'écran est mis à jour avec tous les éléments dessinés
        - L'affichage est rafraîchi
        """
        self.screen.fill(Config.COLORS['background'])

        self._render_nest()
        self._render_food()
        self._render_pheromones()
        self._render_queen()
        self._render_ants()
        self._render_victory()

        pygame.display.flip()

    def _render_nest(self) -> None:
        """
        Dessine le nid et affiche le nombre de ressources accumulées.

        PRE:
        - Le nid existe
        - La police de caractères est initialisée
        - L'écran Pygame est prêt
        POST:
        - Le nid est dessiné sur l'écran
        - Le nombre de ressources est affiché
        """
        pygame.draw.circle(
            self.screen,
            Config.COLORS['nest'],
            self.nest.position,
            Config.SIZES['nest']
        )
        resources_text = self.font.render(
            f"Ressources du Nid : {self.nest.resources}",
            True,
            Config.COLORS['text']
        )
        self.screen.blit(
            resources_text,
            (self.nest.position[0] - 50, self.nest.position[1] - 40)
        )

    def _render_food(self) -> None:
        """
        Dessine les sources de nourriture et leur information.

        PRE:
        - La liste des sources de nourriture n'est pas vide
        - L'écran Pygame est initialisé
        - La police de caractères est prête
        POST:
        - Chaque source de nourriture est dessinée
        - Le numéro et les ressources de chaque source sont affichés
        """
        for food in self.food_sources:
            pygame.draw.circle(
                self.screen,
                Config.COLORS['food'],
                food.position,
                Config.SIZES['food']
            )
            food_text = self.font.render(
                f"{food.number} ({food.resources})",
                True,
                (0, 0, 0)
            )
            self.screen.blit(
                food_text,
                (food.position[0] - 10, food.position[1] - 10)
            )

    def _render_pheromones(self) -> None:
        """
        Dessine les traces de phéromones sur l'écran.

        PRE:
        - La liste des phéromones est initialisée
        - L'écran Pygame est prêt

        POST:
        - Toutes les phéromones sont dessinées sur l'écran
        """
        for pheromone in self.pheromones:
            pygame.draw.circle(
                self.screen,
                Config.COLORS['pheromone'],
                (int(pheromone.position[0]), int(pheromone.position[1])),
                Config.SIZES['pheromone']
            )

    def _render_queen(self) -> None:
        """
        Dessine la reine de la colonie.

        PRE:
        - La reine existe et est initialisée
        - L'écran Pygame est prêt

        POST:
        - La reine est dessinée sur l'écran
        """
        self.queen.render(self.screen)

    def _render_ants(self) -> None:
        """
        Dessine toutes les fourmis de la colonie.

        PRE:
        - La liste des fourmis est initialisée
        - L'écran Pygame est prêt

        POST:
        - Toutes les fourmis sont dessinées sur l'écran
        """
        for ant in self.ants:
            pygame.draw.circle(
                self.screen,
                Config.COLORS['ant'],
                (int(ant.position[0]), int(ant.position[1])),
                Config.SIZES['ant']
            )

    def _render_victory(self) -> None:
        """
        Affiche un message de fin si la colonie a atteint son objectif.

        PRE:
        - La police du message est initialisée
        - L'état du message est défini
        - L'écran Pygame est prêt

        POST:
        - Un message de fin est affiché si la condition est remplie
        """
        if self.victory:
            win_text = self.win_font.render(
                "Simulation terminée.",
                True,
                Config.COLORS['text']
            )
            self.screen.blit(
                win_text,
                (
                    Config.WINDOW_WIDTH // 2 - win_text.get_width() // 2,
                    Config.WINDOW_HEIGHT // 2 - win_text.get_height() // 2
                )
            )

    def run(self) -> None:
        """
        Boucle principale de la simulation.

        PRE:
        - Pygame est initialisé
        - Tous les composants de la simulation sont prêts

        POST:
        - La simulation est terminée proprement
        - Pygame est fermé correctement
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.update()
            self.render()
        
        pygame.quit()
