import random
import pygame
import math
import time
from typing import List, Tuple, Dict

class Config:
    """Configuration class holding all game constants"""
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    
    COLORS = {
        'background': (181, 101, 29),
        'food': (0, 255, 0),
        'nest': (101, 67, 33),
        'ant': (0, 0, 0),
        'queen': (0, 0, 0),
        'pheromone': (200, 200, 255),
        'text': (255, 255, 255)
    }
    
    SIZES = {
        'food': 20,
        'nest': 50,
        'ant': 4,
        'queen': 10,
        'pheromone': 10
    }
    
    GAME_SETTINGS = {
        'food_count': 5,
        'ant_count': 70,
        'speed_reducer': 13,
        'pheromone_detection_distance': 15,
        'min_pheromone_distance': 20,
        'max_nest_resources': 100
    }

class Queen:
    """Class representing the ant colony's queen"""
    def __init__(self, position: Tuple[float, float]):
        self.position = position
    
    def render(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, Config.COLORS['queen'],
                         (int(self.position[0]), int(self.position[1])),
                         Config.SIZES['queen'])

class Food:
    """Class representing a food source"""
    def __init__(self, position: Tuple[float, float], number: int):
        self.position = position
        self.resources = random.randint(10, 50)
        self.pheromone_path_active = True
        self.number = number
    
    def take_resource(self) -> None:
        if self.resources > 0:
            self.resources -= 1
    
    def is_empty(self) -> bool:
        return self.resources <= 0

class Nest:
    """Class representing the ant colony's nest"""
    def __init__(self, position: Tuple[float, float]):
        self.position = position
        self.resources = 0
    
    def add_resource(self) -> None:
        self.resources = min(Config.GAME_SETTINGS['max_nest_resources'], self.resources + 1)
    
    def is_full(self) -> bool:
        return self.resources >= Config.GAME_SETTINGS['max_nest_resources']

class Pheromone:
    """Class representing a pheromone marker"""
    def __init__(self, position: Tuple[float, float], food_source, food_number: int):
        self.position = position
        self.food_source = food_source
        self.food_number = food_number

class Ant:
    """Class representing an individual ant"""
    def __init__(self, position: Tuple[float, float]):
        self.position = position
        self.has_food = False
        self.direction = self._random_direction()
        self.direction_time = time.time()
        self.direction_duration = random.uniform(0.5, 2)
        self.target_food = None
        self.emitting_pheromones = False
        self.food_number = 0
    
    def _random_direction(self) -> Tuple[float, float]:
        return (random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'],
                random.choice([-1, 0, 1]) / Config.GAME_SETTINGS['speed_reducer'])
    
    def get_state(self) -> str:
        if self.has_food:
            return "returning_to_nest"
        elif self.target_food:
            return "going_to_food"
        return "searching"
    
    def move_randomly(self, width: int, height: int) -> None:
        """
        #But de la méthode

            La méthode `move_randomly` déplace un objet (par exemple, une entité dans un jeu ou une simulation) de manière aléatoire dans un espace défini par ses dimensions (`width` et `height`). La direction du mouvement est modifiée à intervalles réguliers de manière aléatoire. Le déplacement de l'objet est limité pour qu'il reste dans les limites de l'espace.

        #Préconditions

            1.Position initiale de l'objet 
                - L'objet doit posséder un attribut `position` sous forme de tuple `(x, y)`, représentant ses coordonnées actuelles dans l'espace.

            2.Direction initiale  
                - L'objet doit avoir un attribut `direction` sous forme de tuple `(dx, dy)` représentant la direction actuelle du mouvement.

            3.Temps de direction et durée  
                - L'objet doit posséder les attributs `direction_time` et `direction_duration` :
                    - `direction_time` représente l'heure du dernier changement de direction (en timestamp).
                    - `direction_duration` représente la durée pendant laquelle l'objet maintient la direction actuelle avant de la changer de manière aléatoire.

            4.Dimensions de l'espace  
                - La méthode prend en entrée deux paramètres `width` et `height`, représentant respectivement la largeur et la hauteur maximales de l'espace dans lequel l'objet peut se déplacer.

        #Postconditions

            1.Mise à jour de la position  
                - La position de l'objet est mise à jour selon la direction actuelle (`self.direction`). 
                - La nouvelle position (`new_x`, `new_y`) est calculée en ajoutant la direction au `x` et `y` actuels de l'objet, tout en garantissant que l'objet reste dans les limites de l'espace défini (entre `0` et `width` pour la coordonnée `x`, et entre `0` et `height` pour la coordonnée `y`).

            2.Changement de direction  
                - Si la durée depuis le dernier changement de direction (`time.time() - self.direction_time`) est supérieure ou égale à la durée définie (`self.direction_duration`), la direction de l'objet est mise à jour de manière aléatoire à l'aide de la méthode `_random_direction()`.
                - La `direction_time` est mise à jour à l'heure actuelle (`time.time()`), et la `direction_duration` est définie aléatoirement entre 0.5 et 1.5 secondes.

        #Programmation défensive

            1.Vérification des dimensions  
                - Il est important de vérifier que les dimensions de l'espace (`width` et `height`) sont des entiers positifs non nuls. Si les dimensions sont invalides, la méthode pourrait provoquer un comportement inattendu, comme un dépassement des bords de l'espace.

            2.Vérification de la position initiale  
                - La position de l'objet (`self.position`) doit être un tuple contenant deux éléments numériques (représentant les coordonnées). Si la position est mal définie, la mise à jour de la position pourrait échouer.

            3.Validation de la direction aléatoire  
                - La méthode `_random_direction()` doit renvoyer un tuple `(dx, dy)` où `dx` et `dy` sont des valeurs numériques, typiquement dans un intervalle spécifié (comme -1, 0, ou 1). Un contrôle sur la validité de ces valeurs peut être ajouté pour éviter des directions incorrectes.

            4.Vérification de `direction_time` et `direction_duration`  
                - Les attributs `direction_time` et `direction_duration` doivent être initialisés correctement pour éviter des erreurs de calcul lors du changement de direction. Si ces variables ne sont pas définies ou initialisées incorrectement, la méthode pourrait se comporter de manière erronée.

        """

        if time.time() - self.direction_time >= self.direction_duration:
            self.direction = self._random_direction()
            self.direction_time = time.time()
            self.direction_duration = random.uniform(0.5, 1.5)
        
        new_x = max(0, min(self.position[0] + self.direction[0], width))
        new_y = max(0, min(self.position[1] + self.direction[1], height))
        self.position = (new_x, new_y)

class AntColonySimulation:
    """Main simulation class managing the game state and rendering"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Simulation de Colonie de Fourmis - MVP")
        self.font = pygame.font.SysFont(None, 24)
        self.win_font = pygame.font.SysFont(None, 72)
        
        self.nest = Nest((random.randint(0, Config.WINDOW_WIDTH),
                         random.randint(0, Config.WINDOW_HEIGHT)))
        self.queen = Queen((self.nest.position[0] + 10, self.nest.position[1] + 10))
        self.food_sources = self._create_food_sources()
        self.ants = self._create_ants()
        self.pheromones: List[Pheromone] = []
        self.running = True
        self.victory = False
    
    def _create_food_sources(self) -> List[Food]:
        return [Food((random.randint(0, Config.WINDOW_WIDTH),
                     random.randint(0, Config.WINDOW_HEIGHT)), i + 1)
                for i in range(Config.GAME_SETTINGS['food_count'])]
    
    def _create_ants(self) -> List[Ant]:
        return [Ant(self._random_nest_position()) 
                for _ in range(Config.GAME_SETTINGS['ant_count'])]
    
    def _random_nest_position(self) -> Tuple[float, float]:
        return (self.nest.position[0] + random.randint(-Config.SIZES['nest'], Config.SIZES['nest']),
                self.nest.position[1] + random.randint(-Config.SIZES['nest'], Config.SIZES['nest']))
    
    def update(self) -> None:
        self._process_ants()
        self._check_victory()
    
    def _process_ants(self) -> None:
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
        #But de la méthode

            La méthode `_detect_pheromone` a pour objectif de détecter la présence de phéromones dans un rayon donné autour de la fourmi. Si une phéromone est détectée, la fourmi cible la source de nourriture associée à cette phéromone. 
            Si aucune phéromone n'est détectée, la méthode retourne `False`.
        
        #Préconditions

            1.Liste des phéromones valide  
                L'attribut `self.pheromones` doit être une liste contenant des objets représentant des phéromones. Chaque objet doit avoir :
                    - Un attribut `position`, représentant les coordonnées `(x, y)` de la phéromone.
                    - Un attribut `food_source`, représentant la source de nourriture associée à la phéromone.

            2.Objet `ant` valide  
                L'argument `ant` doit être une instance de la classe `Ant` avec :
                    - Un attribut `position`, qui doit être une paire de coordonnées `(x, y)` représentant la position actuelle de la fourmi.
                    - Un attribut `target_food`, qui sera mis à jour pour indiquer la source de nourriture associée à la phéromone détectée.

            3.Distance de détection valide  
                La clé `pheromone_detection_distance` dans `Config.GAME_SETTINGS` doit être définie et contenir une valeur numérique positive représentant la distance maximale de détection des phéromones.

        #Postconditions

            1.Phéromone détectée  
                Si une phéromone est détectée dans la portée définie par `pheromone_detection_distance` :
                    - L'attribut `target_food` de l'instance `ant` est mis à jour pour pointer vers la source de nourriture associée à la phéromone.
                    - La méthode retourne `True`.

            2.Aucune phéromone détectée  
                Si aucune phéromone n'est détectée dans le rayon spécifié, la méthode retourne `False`. L'attribut `target_food` de la fourmi reste inchangé.

        #Programmation défensive

            1.Validation des entrées  
                Avant de procéder à la détection, il est nécessaire de vérifier que la liste `self.pheromones` existe et qu'elle contient des objets valides. Chaque phéromone doit avoir les attributs `position` et `food_source` correctement définis. De même, l'argument `ant` doit être une instance valide de la classe `Ant`.

            2.Vérification de la clé de détection  
                Il est important de s'assurer que la clé `pheromone_detection_distance` existe dans `Config.GAME_SETTINGS` et que sa valeur est un nombre valide et positif. Si cette clé est manquante ou invalide, la méthode doit renvoyer `False`.

            3.Éviter les erreurs de calcul  
                Le calcul de la distance entre la fourmi et les phéromones ne doit pas échouer si les coordonnées `position` de la fourmi ou de la phéromone sont mal définies. Une vérification préalable doit être effectuée pour éviter des erreurs de type.
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
        #But de la méthode

            La méthode `_process_return_to_nest` gère le déplacement d'une fourmi (`ant`) vers son nid (`nest`) et les interactions associées, comme l'émission de phéromones et la gestion de la ressource alimentaire lorsque la fourmi retourne au nid avec de la nourriture.

        #Préconditions

            1.Position de la fourmi  
                L'objet `ant` doit posséder un attribut `position` représentant ses coordonnées actuelles sous forme de tuple `(x, y)`.

            2.Position du nid  
                L'objet `self.nest` doit posséder un attribut `position` représentant les coordonnées du nid sous forme de tuple `(x, y)`.

            3.Vitesse de réduction  
                La constante `speed_reducer` dans `Config.GAME_SETTINGS` doit être définie et non nulle pour ajuster la vitesse de déplacement de la fourmi.

            4.Existence de ressources dans le nid  
                L'objet `self.nest` doit être en mesure d'ajouter des ressources via la méthode `add_resource()` lorsqu'une fourmi retourne avec de la nourriture.

            5.Vérification de l'état de la fourmi  
                L'objet `ant` doit avoir les attributs suivants :
                    - `emitting_pheromones`: un booléen indiquant si la fourmi émet des phéromones.
                    - `has_food`: un booléen indiquant si la fourmi transporte de la nourriture.

        #Postconditions

            1.Mise à jour de la position de la fourmi 
                La position de la fourmi (`ant.position`) est mise à jour pour se rapprocher du nid, en fonction de la distance calculée entre la fourmi et le nid. La fourmi se déplace en direction du nid, avec la vitesse ajustée par la constante `speed_reducer`.

            2.Ajout de phéromones  
                Si la fourmi émet des phéromones (`ant.emitting_pheromones`), la méthode `_add_pheromone` est appelée pour ajouter une phéromone à la liste des phéromones du système.

            3.Ajout de la ressource au nid  
                Lorsque la distance entre la fourmi et le nid est inférieure à la taille du nid (`Config.SIZES['nest']`) et que la fourmi porte de la nourriture (`ant.has_food`), la méthode `add_resource()` du nid est appelée pour ajouter une ressource. La fourmi ne porte alors plus de nourriture (`ant.has_food = False`), et l'émission de phéromones est désactivée (`ant.emitting_pheromones = False`).

            4.Désactivation des phéromones  
                Si la fourmi est arrivée au nid avec de la nourriture, l'attribut `ant.emitting_pheromones` est mis à `False`.

        #Programmation défensive

            1.Vérification de la validité de la position  
                Avant de calculer la distance, il est important de s'assurer que `self.nest.position` et `ant.position` sont des tuples contenant des coordonnées valides (deux nombres). Cela permet d'éviter toute erreur de calcul.

            2.Vérification de la validité de `speed_reducer`  
                Il est crucial de vérifier que `Config.GAME_SETTINGS['speed_reducer']` est une valeur positive et non nulle. Sinon, cela pourrait entraîner un comportement inattendu ou une division par zéro lors du calcul du déplacement de la fourmi.

            3.Vérification de l'état de la fourmi 
                Il est nécessaire de vérifier que l'attribut `ant.has_food` est un booléen valide et que l'attribut `ant.emitting_pheromones` est également un booléen. Des valeurs incorrectes ou inattendues pourraient perturber le fonctionnement de la méthode.

            4.Vérification de l'état du nid  
                La méthode `add_resource()` du nid doit être définie et fonctionnelle. Avant d'ajouter une ressource, il peut être utile de s'assurer que cette méthode existe et fonctionne correctement.
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
        #But de la méthode

            La méthode `_add_pheromone` permet d'ajouter une nouvelle phéromone à la liste `self.pheromones` en fonction de la position de la fourmi et de la distance par rapport à la dernière phéromone ajoutée. Elle garantit que les phéromones ne sont ajoutées que si elles sont suffisamment éloignées de la dernière phéromone.

        #Préconditions

            1.Liste des phéromones valide
                L'attribut `self.pheromones` doit être une liste valide, pouvant contenir des objets représentant des phéromones. La liste peut être vide si aucune phéromone n'a été ajoutée auparavant.

            2.Objet `ant` valide
                L'argument `ant` doit être une instance de la classe `Ant` et doit posséder les attributs suivants :
                    - `position` : une paire de coordonnées `(x, y)` représentant la position actuelle de la fourmi.
                    - `target_food` : un identifiant ou un objet représentant la source de nourriture que la fourmi cible.
                    - `food_number` : un identifiant ou une valeur qui représente la quantité de nourriture liée à cette phéromone.

            3.Distance minimale de détection des phéromones  
                La clé `min_pheromone_distance` dans `Config.GAME_SETTINGS` doit être définie et contenir une valeur numérique positive représentant la distance minimale entre deux phéromones avant d'en ajouter une nouvelle.

        #Postconditions

            1.Ajout de la phéromone 
                Si la liste `self.pheromones` est vide ou si la distance entre la position de la fourmi et la dernière phéromone de la liste est supérieure à la distance minimale définie par `min_pheromone_distance` :
                    - Une nouvelle instance de `Pheromone` est créée avec les attributs suivants : `position` (position de la fourmi), `target_food` (cible de nourriture de la fourmi), et `food_number` (quantité de nourriture).
                    - Cette phéromone est ajoutée à la liste `self.pheromones`.

            2.Aucune modification si la distance est insuffisante  
                Si la distance entre la position actuelle de la fourmi et la dernière phéromone est inférieure à `min_pheromone_distance`, aucune phéromone n'est ajoutée et la liste `self.pheromones` reste inchangée.

        #Programmation défensive

            1.Validation de la liste `self.pheromones`  
                Avant de procéder à l'ajout, il est important de s'assurer que `self.pheromones` est bien une liste valide (initialisée et définie correctement). Si `self.pheromones` n'est pas une liste valide, la méthode pourrait échouer lors de l'ajout de nouvelles phéromones.

            2.Vérification de la clé `min_pheromone_distance` 
                Il est crucial de vérifier que la clé `min_pheromone_distance` existe dans `Config.GAME_SETTINGS` et qu'elle contient une valeur numérique valide. Si cette clé est absente ou mal définie, la méthode ne pourra pas effectuer de vérification de la distance.

            3.Vérification des coordonnées de la fourmi  
                La position de la fourmi doit être correctement définie sous forme de coordonnées `(x, y)` pour calculer la distance entre la fourmi et la dernière phéromone. Si la position est mal définie ou absente, la méthode risque de générer des erreurs de calcul.

        """
        if not self.pheromones or math.hypot(
            ant.position[0] - self.pheromones[-1].position[0],
            ant.position[1] - self.pheromones[-1].position[1]
        ) > Config.GAME_SETTINGS['min_pheromone_distance']:
            self.pheromones.append(Pheromone(ant.position, ant.target_food, ant.food_number))
    
    def _remove_food_pheromones(self, food_number: int) -> None:
        """
        #But de la méthode

            La méthode `_remove_food_pheromones` permet de supprimer toutes les phéromones associées à une source de nourriture spécifique, identifiée par `food_number`, de la liste `self.pheromones`.

        #Préconditions

            1.Liste des phéromones valide  
                L'attribut `self.pheromones` doit être une liste valide contenant des objets représentant des phéromones. Chaque objet `Pheromone` doit avoir un attribut `food_number` pour identifier la source de nourriture à laquelle il est lié.

            2.`food_number` valide  
                L'argument `food_number` doit être un entier valide qui correspond à l'identifiant de la source de nourriture dont on veut supprimer les phéromones associées.

            3.Existence de phéromones  
                La liste `self.pheromones` peut être vide ou contenir des phéromones. Si la liste est vide, la méthode n'effectue aucune action.

        #Postconditions

            1.Suppression des phéromones associées  
                Toutes les phéromones dont l'attribut `food_number` est égal à l'argument `food_number` sont supprimées de la liste `self.pheromones`.

            2.Liste mise à jour  
                La liste `self.pheromones` est mise à jour pour ne contenir que les phéromones dont `food_number` est différent de celui spécifié.

        # Programmation défensive

            1.Vérification de l'existence de self.pheromones  
                Avant de procéder à la suppression, il est important de vérifier que `self.pheromones` est bien une liste définie. Si ce n'est pas le cas, la méthode pourrait échouer.

            2.Vérification de la validité de `food_number`  
                Il est nécessaire que l'argument `food_number` soit un entier valide pour éviter tout comportement inattendu. Si `food_number` est mal défini ou n'est pas un entier, une erreur pourrait se produire lors de la comparaison avec l'attribut `food_number` des phéromones.
        """
        self.pheromones = [p for p in self.pheromones if p.food_number != food_number]
    
    def _check_victory(self) -> None:
        if self.nest.is_full():
            self.victory = True
    
    def render(self) -> None:
        self.screen.fill(Config.COLORS['background'])
        self._render_nest()
        self._render_food()
        self._render_pheromones()
        self._render_queen()
        self._render_ants()
        self._render_victory()
        pygame.display.flip()
    
    def _render_nest(self) -> None:
        pygame.draw.circle(self.screen, Config.COLORS['nest'],
                         self.nest.position, Config.SIZES['nest'])
        resources_text = self.font.render(f"Ressources du Nid : {self.nest.resources}",
                                        True, Config.COLORS['text'])
        self.screen.blit(resources_text,
                        (self.nest.position[0] - 50, self.nest.position[1] - 40))
    
    def _render_food(self) -> None:
        for food in self.food_sources:
            pygame.draw.circle(self.screen, Config.COLORS['food'],
                             food.position, Config.SIZES['food'])
            food_text = self.font.render(f"{food.number} ({food.resources})",
                                       True, (0, 0, 0))
            self.screen.blit(food_text,
                           (food.position[0] - 10, food.position[1] - 10))
    
    def _render_pheromones(self) -> None:
        for pheromone in self.pheromones:
            pygame.draw.circle(self.screen, Config.COLORS['pheromone'],
                             (int(pheromone.position[0]), int(pheromone.position[1])),
                             Config.SIZES['pheromone'])
    
    def _render_queen(self) -> None:
        self.queen.render(self.screen)
    
    def _render_ants(self) -> None:
        for ant in self.ants:
            pygame.draw.circle(self.screen, Config.COLORS['ant'],
                             (int(ant.position[0]), int(ant.position[1])),
                             Config.SIZES['ant'])
    
    def _render_victory(self) -> None:
        if self.victory:
            win_text = self.win_font.render("Gagné !", True, Config.COLORS['text'])
            self.screen.blit(win_text,
                           (Config.WINDOW_WIDTH // 2 - win_text.get_width() // 2,
                            Config.WINDOW_HEIGHT // 2 - win_text.get_height() // 2))
    
    def run(self) -> None:
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