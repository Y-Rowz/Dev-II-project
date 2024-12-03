import random
import pygame
import math
import time
from typing import List, Tuple, Dict

class Config:
    """
    Classe de configuration centralisant tous les paramètres constants du jeu.
    Cette approche permet de modifier facilement les paramètres du jeu 
    sans changer la logique principale de la simulation.
    
    Sections principales :
    - WINDOW_WIDTH/HEIGHT : Définissent la zone d'affichage de la simulation
    - COLORS : Définissent la palette de couleurs des différents éléments du jeu
    - SIZES : Définissent les tailles des différents objets du jeu
    - GAME_SETTINGS : Paramètres configurables de la mécanique du jeu
    """
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    
    # Palette de couleurs utilisant des tuples RVB pour divers éléments du jeu
    COLORS = {
        'background': (181, 101, 29),  # Marron terreux pour le fond
        'food': (0, 255, 0),           # Vert vif pour les sources de nourriture
        'nest': (101, 67, 33),         # Marron pour le nid
        'ant': (0, 0, 0),              # Noir pour les fourmis
        'queen': (0, 0, 0),            # Noir pour la reine
        'pheromone': (200, 200, 255),  # Bleu clair pour les traces de phéromones
        'text': (255, 255, 255)        # Blanc pour le texte
    }
    
    # Tailles définissant l'échelle de rendu des différents objets du jeu
    SIZES = {
        'food': 20,       # Taille des cercles de sources de nourriture
        'nest': 50,       # Taille du cercle du nid
        'ant': 4,         # Taille des fourmis individuelles
        'queen': 10,      # Taille de la reine fourmi
        'pheromone': 10   # Taille des marqueurs de phéromones
    }
    
    # Paramètres du jeu pour contrôler la dynamique de la simulation
    GAME_SETTINGS = {
        'food_count': 5,                     # Nombre initial de sources de nourriture
        'ant_count': 70,                     # Nombre total de fourmis dans la colonie
        'speed_reducer': 13,                 # Divise la vitesse de déplacement pour contrôler la mobilité des fourmis
        'pheromone_detection_distance': 15,  # Distance à laquelle une fourmi peut détecter une phéromone
        'min_pheromone_distance': 20,        # Distance minimale entre les dépôts de phéromones
        'max_nest_resources': 100            # Ressources maximales que le nid peut accumuler
    }

class Queen:
    """
    Représente la reine de la colonie de fourmis.
    Dans cette simulation, la reine est principalement un élément visuel 
    sans logique comportementale complexe.
    """
    def __init__(self, position: Tuple[float, float]):
        # Stocke la position de la reine sur l'écran
        self.position = position
    
    def render(self, screen: pygame.Surface) -> None:
        # Dessine la reine comme un cercle sur l'écran pygame
        pygame.draw.circle(screen, Config.COLORS['queen'],
                         (int(self.position[0]), int(self.position[1])),
                         Config.SIZES['queen'])

class Food:
    """
    Représente une source de nourriture dans la simulation.
    Chaque source de nourriture a une quantité initiale de ressources aléatoire 
    et peut être épuisée.
    """
    def __init__(self, position: Tuple[float, float], number: int):
        self.position = position  # Emplacement de la source de nourriture
        self.resources = random.randint(10, 50)  # Ressources initiales aléatoires
        self.pheromone_path_active = True  # Indicateur de la voie de phéromones initiale
        self.number = number  # Identifiant unique de la source de nourriture
    
    def take_resource(self) -> None:
        # Diminue les ressources lorsqu'une fourmi collecte de la nourriture
        if self.resources > 0:
            self.resources -= 1
    
    def is_empty(self) -> bool:
        # Vérifie si la source de nourriture est complètement épuisée
        return self.resources <= 0

class Nest:
    """
    Représente le nid de la colonie de fourmis.
    Suit les ressources accumulées et a une capacité maximale.
    """
    def __init__(self, position: Tuple[float, float]):
        self.position = position  # Emplacement du nid
        self.resources = 0  # Aucune ressource au début
    
    def add_resource(self) -> None:
        # Ajoute une ressource au nid, en respectant la capacité maximale
        self.resources = min(Config.GAME_SETTINGS['max_nest_resources'], self.resources + 1)
    
    def is_full(self) -> bool:
        # Vérifie si le nid a atteint sa capacité maximale de ressources
        return self.resources >= Config.GAME_SETTINGS['max_nest_resources']

class Pheromone:
    """
    Représente un marqueur de phéromones dans la simulation.
    Les phéromones guident les fourmis vers les sources de nourriture.
    """
    def __init__(self, position: Tuple[float, float], food_source, food_number: int):
        self.position = position  # Position du marqueur de phéromones
        self.food_source = food_source  # Source de nourriture associée
        self.food_number = food_number  # Numéro de la source de nourriture

class Ant:
    """
    Représente une fourmi individuelle dans la simulation.
    Gère le comportement et les déplacements de la fourmi.
    """
    def __init__(self, position: Tuple[float, float]):
        self.position = position  # Position actuelle de la fourmi
        self.has_food = False  # Indique si la fourmi transporte de la nourriture
        self.direction = self._random_direction()  # Direction initiale aléatoire
        self.direction_time = time.time()  # Temps du dernier changement de direction
        self.direction_duration = random.uniform(0.5, 2)  # Durée avant le prochain changement de direction
        self.target_food = None  # Source de nourriture ciblée
        self.emitting_pheromones = False  # Indique si la fourmi laisse des phéromones
        self.food_number = 0  # Numéro de la source de nourriture
    
    def _random_direction(self) -> Tuple[float, float]:
        # Génère une direction de déplacement aléatoire
        return (random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'],
                random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'])
    
    def get_state(self) -> str:
        # Renvoie l'état actuel de la fourmi
        if self.has_food:
            return "returning_to_nest"  # Retourne au nid avec de la nourriture
        elif self.target_food:
            return "going_to_food"  # Se dirige vers une source de nourriture
        return "searching"  # Recherche de la nourriture
    
    def move_randomly(self, width: int, height: int) -> None:
        # Déplacement aléatoire de la fourmi dans les limites de l'écran
        if time.time() - self.direction_time >= self.direction_duration:
            # Changement de direction après un certain temps
            self.direction = self._random_direction()
            self.direction_time = time.time()
            self.direction_duration = random.uniform(0.5, 1.5)
        
        # Calcul de la nouvelle position en restant dans les limites
        new_x = max(0, min(self.position[0] + self.direction[0], width))
        new_y = max(0, min(self.position[1] + self.direction[1], height))
        self.position = (new_x, new_y)

class AntColonySimulation:
    """
    Classe principale gérant la simulation complète de la colonie de fourmis.
    
    Cette classe est responsable de :
    - Initialiser tous les éléments de la simulation
    - Gérer les mises à jour du jeu
    - Rendre graphiquement la simulation
    - Contrôler la logique de victoire
    """
    def __init__(self):
        # Initialisation de Pygame pour la création de l'interface graphique
        pygame.init()
        
        # Création de la fenêtre de jeu avec les dimensions définies dans la configuration
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        
        # Définition du titre de la fenêtre
        pygame.display.set_caption("Simulation de Colonie de Fourmis - MVP")
        
        # Création des polices pour afficher du texte (normal et grand)
        self.font = pygame.font.SysFont(None, 24)
        self.win_font = pygame.font.SysFont(None, 72)
        
        # Placement aléatoire du nid sur l'écran
        self.nest = Nest((random.randint(0, Config.WINDOW_WIDTH),
                         random.randint(0, Config.WINDOW_HEIGHT)))
        
        # Placement de la reine à proximité du nid
        self.queen = Queen((self.nest.position[0] + 10, self.nest.position[1] + 10))
        
        # Génération des sources de nourriture
        self.food_sources = self._create_food_sources()
        
        # Création de la population de fourmis
        self.ants = self._create_ants()
        
        # Liste pour stocker les phéromones laissées par les fourmis
        self.pheromones: List[Pheromone] = []
        
        # Indicateurs de l'état de la simulation
        self.running = True  # La simulation est-elle en cours ?
        self.victory = False  # La colonie a-t-elle atteint son objectif ?
    
    def _create_food_sources(self) -> List[Food]:
        """
        Méthode privée pour créer un ensemble de sources de nourriture.
        
        Génère un nombre de sources de nourriture défini dans la configuration,
        avec des positions aléatoires sur l'écran.
        
        Returns:
            List[Food]: Une liste de sources de nourriture
        """
        return [Food((random.randint(0, Config.WINDOW_WIDTH),
                     random.randint(0, Config.WINDOW_HEIGHT)), i + 1)
                for i in range(Config.GAME_SETTINGS['food_count'])]
    
    def _create_ants(self) -> List[Ant]:
        """
        Méthode privée pour créer la population initiale de fourmis.
        
        Génère un nombre de fourmis défini dans la configuration,
        en les positionnant autour du nid.
        
        Returns:
            List[Ant]: Une liste de fourmis
        """
        return [Ant(self._random_nest_position()) 
                for _ in range(Config.GAME_SETTINGS['ant_count'])]
    
    def _random_nest_position(self) -> Tuple[float, float]:
        """
        Génère une position aléatoire à proximité du nid pour les fourmis.
        
        Permet de répartir les fourmis autour du nid de manière aléatoire.
        
        Returns:
            Tuple[float, float]: Les coordonnées x et y d'une position près du nid
        """
        return (self.nest.position[0] + random.randint(-Config.SIZES['nest'], Config.SIZES['nest']),
                self.nest.position[1] + random.randint(-Config.SIZES['nest'], Config.SIZES['nest']))
    
    def update(self) -> None:
        """
        Méthode principale de mise à jour de la simulation.
        
        Appelée à chaque frame pour :
        - Mettre à jour le comportement des fourmis
        - Vérifier les conditions de victoire
        """
        self._process_ants()
        self._check_victory()
    
    def _process_ants(self) -> None:
        """
        Gère le comportement de chaque fourmi selon son état actuel.
        
        Trois états possibles :
        - Recherche : déplacement aléatoire et détection de nourriture
        - Retour au nid : transport de nourriture vers le nid
        - Recherche de nourriture : se diriger vers une source de nourriture connue
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
        
        Gère la logique de collecte de nourriture :
        - Vérifie la distance entre la fourmi et les sources de nourriture
        - Permet la collection de ressources si la source est active
        - Gère l'activation des chemins de phéromones
        
        Args:
            ant (Ant): La fourmi en train de chercher de la nourriture
        
        Returns:
            bool: True si la nourriture a été détectée, False sinon
        """
        for food in self.food_sources:
            distance = math.hypot(ant.position[0] - food.position[0],
                                ant.position[1] - food.position[1])
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
        
        Recherche des phéromones dans un rayon de détection défini.
        Si une phéromone est détectée, la fourmi se dirige vers la source 
        de nourriture associée.
        
        Args:
            ant (Ant): La fourmi en train de chercher des phéromones
        
        Returns:
            bool: True si une phéromone est détectée, False sinon
        """
        for pheromone in self.pheromones:
            distance = math.hypot(ant.position[0] - pheromone.position[0],
                                ant.position[1] - pheromone.position[1])
            if distance < Config.GAME_SETTINGS['pheromone_detection_distance']:
                ant.target_food = pheromone.food_source
                return True
        return False
    
    def _process_return_to_nest(self, ant: Ant) -> None:
        """
        Gère le déplacement d'une fourmi transportant de la nourriture vers le nid.
        
        Fonctionnalités principales :
        - Calcul de la direction et du déplacement vers le nid
        - Dépôt de phéromones le long du trajet
        - Ajout des ressources au nid une fois arrivée
        
        Args:
            ant (Ant): La fourmi en train de retourner au nid
        """
        dx = self.nest.position[0] - ant.position[0]
        dy = self.nest.position[1] - ant.position[1]
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            ant.position = (
                ant.position[0] + (dx / distance) * (5 / Config.GAME_SETTINGS['speed_reducer']),
                ant.position[1] + (dy / distance) * (5 / Config.GAME_SETTINGS['speed_reducer'])
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
        
        Principales actions :
        - Vérification de l'existence de la source de nourriture
        - Déplacement vers la source
        - Collecte de nourriture
        - Gestion de l'épuisement des sources de nourriture
        
        Args:
            ant (Ant): La fourmi se dirigeant vers une source de nourriture
        """
        if not ant.target_food or ant.target_food not in self.food_sources:
            ant.target_food = None
            ant.food_number = 0
            return
        
        dx = ant.target_food.position[0] - ant.position[0]
        dy = ant.target_food.position[1] - ant.position[1]
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            ant.position = (
                ant.position[0] + (dx / distance) * (5 / Config.GAME_SETTINGS['speed_reducer']),
                ant.position[1] + (dy / distance) * (5 / Config.GAME_SETTINGS['speed_reducer'])
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
        
        Vérifie la distance minimale entre les dépôts de phéromones 
        pour éviter une surcharge de marqueurs.
        
        Args:
            ant (Ant): La fourmi laissant une trace de phéromone
        """
        if not self.pheromones or math.hypot(
            ant.position[0] - self.pheromones[-1].position[0],
            ant.position[1] - self.pheromones[-1].position[1]
        ) > Config.GAME_SETTINGS['min_pheromone_distance']:
            self.pheromones.append(Pheromone(ant.position, ant.target_food, ant.food_number))
    
    def _remove_food_pheromones(self, food_number: int) -> None:
        """
        Supprime les phéromones associées à une source de nourriture épuisée.
        
        Nettoie les traces de phéromones pour une source de nourriture 
        qui n'existe plus.
        
        Args:
            food_number (int): Identifiant de la source de nourriture
        """
        self.pheromones = [p for p in self.pheromones if p.food_number != food_number]
    
    def _check_victory(self) -> None:
        """
        Vérifie si la colonie a atteint son objectif de ressources.
        
        Déclare la victoire lorsque le nid a accumulé le nombre maximum 
        de ressources configuré.
        """
        if self.nest.is_full():
            self.victory = True
    
    def render(self) -> None:
        """
        Méthode principale de rendu graphique de la simulation.
        
        Dessine tous les éléments de la simulation :
        - Fond
        - Nid
        - Sources de nourriture
        - Phéromones
        - Reine
        - Fourmis
        - Message de victoire si applicable
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
        """
        pygame.draw.circle(self.screen, Config.COLORS['nest'],
                         self.nest.position, Config.SIZES['nest'])
        resources_text = self.font.render(f"Ressources du Nid : {self.nest.resources}",
                                        True, Config.COLORS['text'])
        self.screen.blit(resources_text,
                        (self.nest.position[0] - 50, self.nest.position[1] - 40))
    
    def _render_food(self) -> None:
        """
        Dessine les sources de nourriture et affiche leur numéro et ressources restantes.
        """
        for food in self.food_sources:
            pygame.draw.circle(self.screen, Config.COLORS['food'],
                             food.position, Config.SIZES['food'])
            food_text = self.font.render(f"{food.number} ({food.resources})",
                                       True, (0, 0, 0))
            self.screen.blit(food_text,
                           (food.position[0] - 10, food.position[1] - 10))
    
    def _render_pheromones(self) -> None:
        """
        Dessine les traces de phéromones sur l'écran.
        """
        for pheromone in self.pheromones:
            pygame.draw.circle(self.screen, Config.COLORS['pheromone'],
                             (int(pheromone.position[0]), int(pheromone.position[1])),
                             Config.SIZES['pheromone'])
    
    def _render_queen(self) -> None:
        """
        Dessine la reine de la colonie.
        """
        self.queen.render(self.screen)
    
    def _render_ants(self) -> None:
        """
        Dessine toutes les fourmis de la colonie.
        """
        for ant in self.ants:
            pygame.draw.circle(self.screen, Config.COLORS['ant'],
                             (int(ant.position[0]), int(ant.position[1])),
                             Config.SIZES['ant'])
    
    def _render_victory(self) -> None:
        """
        Affiche un message de victoire si la colonie a atteint son objectif.
        """
        if self.victory:
            win_text = self.win_font.render("Gagné !", True, Config.COLORS['text'])
            self.screen.blit(win_text,
                           (Config.WINDOW_WIDTH // 2 - win_text.get_width() // 2,
                            Config.WINDOW_HEIGHT // 2 - win_text.get_height() // 2))
    
    def run(self) -> None:
        """
        Boucle principale de la simulation.
        
        Gère :
        - La capture des événements (fermeture de la fenêtre)
        - Les mises à jour de la simulation
        - Le rendu graphique
        - La fermeture propre de Pygame
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.update()
            self.render()
        
        pygame.quit()

if __name__ == "__main__":
    simulation = AntColonySimulation()
    simulation.run()
