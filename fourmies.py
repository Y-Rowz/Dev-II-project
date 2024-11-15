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
