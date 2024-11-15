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
        """
        Loan :
        But de la méthode
        La méthode is_empty vérifie si la source de nourriture est vide, c'est-à-dire si elle n'a plus de ressources disponibles.
    
        Préconditions
        - L'instance de la classe Food est valide et son attribut resources doit être défini.
    
        Postconditions
        - Si le nombre de ressources dans la source de nourriture est inférieur ou égal à 0, la méthode retourne True, indiquant que la source est bel et bien vide.
        - Sinon, elle retourne False.
    
        Programmation défensive
        - Vérifier que l'attribut resources est bien défini et qu'il est de type integer avant de procéder à la comparaison.
        """
        return self.resources <= 0

class Nest:
    """Class representing the ant colony's nest"""
    def __init__(self, position: Tuple[float, float]):
        self.position = position
        self.resources = 0
    
    def add_resource(self) -> None:
        """
        But de la méthode
        La méthode add_resource permet d'ajouter une ressource au nid de la fourmi. 
        Si le nombre de ressources du nid atteint la capacité maximale, aucune ressource n'est ajoutée.
    
        Préconditions
        - L'instance de la classe Nest est valide et sa position ainsi que ses ressources doivent être définies.
        - La clé max_nest_resources dans Config.GAME_SETTINGS doit être définie et contenir une valeur numérique valide.
    
        Postconditions
        - Si le nombre de ressources dans le nid est inférieur à la capacité maximale, une ressource est ajoutée.
        - Si la capacité maximale est atteinte, le nombre de ressources ne dépasse pas la limite.
    
        Programmation défensive
        - Vérifier que la clé max_nest_resources est bien définie dans Config.GAME_SETTINGS.
        - Vérifier que la valeur actuelle des ressources dans le nid ne dépasse pas la capacité maximale.
        """
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
        """
        But de la méthode
        La méthode _create_ants est responsable de la création des objets Ant (fourmis) au début de la simulation. 
        Chaque fourmi est placée aléatoirement autour du nid et prête à commencer ses actions.
    
        Préconditions
        - L'instance de la classe AntColonySimulation est initialisée.
        - La valeur de Config.GAME_SETTINGS['ant_count'] doit être définie et être un nombre entier valide.
    
        Postconditions
        - Une liste d'objets Ant est retournée, chaque objet ayant une position initiale près du nid.
        - Chaque fourmi a une position aléatoire et est prête à commencer à chercher de la nourriture.
    
        Programmation défensive
        - Vérifier que Config.GAME_SETTINGS['ant_count'] est bien un entier valide et supérieur à 0 avant de créer les fourmis.
        - Vérifier que la position du nid est valide et bien définie.
        """
        return [Ant(self._random_nest_position()) 
                for _ in range(Config.GAME_SETTINGS['ant_count'])]
    
    def _random_nest_position(self) -> Tuple[float, float]:
        """
        But de la méthode
        La méthode _random_nest_position génère une position aléatoire pour chaque fourmi autour du nid. 
        Cette position sert à initialiser les fourmis au début de la simulation.
    
        Préconditions
        - L'instance de la classe AntColonySimulation est initialisée.
        - La position du nid doit être valide, définie par self.nest.position.
    
        Postconditions
        - La méthode retourne un tuple de coordonnées (x, y) correspondant à une position aléatoire autour du nid.
    
        Programmation défensive
        - Vérifier que self.nest.position existe et contient des coordonnées valides (x, y).
        - Vérifier que les valeurs des tailles du nid (Config.SIZES['nest']) sont raisonnables.
        - Eviter des erreurs lors du calcul des positions.
        """
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
        for pheromone in self.pheromones:
            distance = math.hypot(ant.position[0] - pheromone.position[0],
                                ant.position[1] - pheromone.position[1])
            if distance < Config.GAME_SETTINGS['pheromone_detection_distance']:
                ant.target_food = pheromone.food_source
                return True
        return False
    
    def _process_return_to_nest(self, ant: Ant) -> None:
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
        But de la méthode
        Cette méthode gère le mouvement de la fourmi lorsqu'elle retourne à une source de nourriture après en avoir collecté. 
        Elle met également à jour son état et son positionnement en fonction de la distance avec la nourriture.
    
        Préconditions
        - L'instance ant doit être une instance valide de la classe Ant, avec une position et un attribut target_food définis.
        - L'instance target_food de la fourmi doit être une source de nourriture valide.
    
        Postconditions
        - La fourmi se déplace vers la nourriture et met à jour sa position.
        - Si la nourriture est épuisée, la fourmi retourne à son état de recherche.
    
        Programmation défensive
        - Vérifier que ant.target_food est bien une instance de la classe Food et qu'elle est définie avant de tenter de se déplacer.
        - Vérifier que la nourriture n'est pas déjà vide avant que la fourmi n'essaie d'en prendre.
        - Gerer les erreurs si la distance entre la fourmi et la source de nourriture est trop faible pour un mouvement fluide et correct.
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
        if not self.pheromones or math.hypot(
            ant.position[0] - self.pheromones[-1].position[0],
            ant.position[1] - self.pheromones[-1].position[1]
        ) > Config.GAME_SETTINGS['min_pheromone_distance']:
            self.pheromones.append(Pheromone(ant.position, ant.target_food, ant.food_number))
    
    def _remove_food_pheromones(self, food_number: int) -> None:
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
