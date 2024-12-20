
import pygame
import random
import math
import time
from models.menace import Menace
from typing import List, Tuple
from config.settings import Config
from models.ant import Ant
from models.food import Food
from models.nest import Nest
from models.pheromone import Pheromone
from models.queen import Queen
from models.nourrice import Nourrice
from models.garde import Garde
from models.ouvriere import Ouvriere


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
        
        # Reprend les parametres de la fenetre pour les dimentions
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        
        # Titre
        pygame.display.set_caption("Simulation de Colonie de Fourmis - MVP")
        

        self.font = pygame.font.SysFont(None, 24)  # informations classic
        self.win_font = pygame.font.SysFont(None, 72)  # messages importants
        
        # Placement aléatoire du nid
        self.nest = Nest((random.randint(0, Config.WINDOW_WIDTH),
                         random.randint(0, Config.WINDOW_HEIGHT)))
        
        # Placement de la reine
        self.queen = Queen((self.nest.position[0] + 10, self.nest.position[1] + 10))
        
        # sources de nourriture
        self.food_sources = self._create_food_sources()
        
        # Fourmis
        self.ants = self._create_ants()
        
        # Liste pour suivre les traces de phéromones laissées par les fourmis
        self.pheromones: List[Pheromone] = []
        
        
        self.running = True  # Contrôle l'exécution continue de la simulation
        self.victory = False  # Indicateur de succès de la colonie

        self.menaces = []  # Liste pour stocker les menaces
        self.last_menace_spawn_time = time.time()  #
    
    def _create_food_sources(self) -> List[Food]:
        """
        Méthode privée pour créer un ensemble de sources de nourriture.
        
        PRE: Configuration des paramètres de jeu disponible
        POST: 
        - Retourne une liste de sources de nourriture générées aléatoirement
        - Chaque source a une position unique sur l'écran
        """
        # Générer des sources de nourriture aléatoirement selon le nombre configuré
        return [Food((random.randint(0, Config.WINDOW_WIDTH),
                     random.randint(0, Config.WINDOW_HEIGHT)), i + 1)
                for i in range(Config.GAME_SETTINGS['food_count'])]
    
    def _create_ants(self) -> List[Ant]:
        """
        Méthode privée pour créer la population initiale de fourmis.
        
        Chaque fourmi a une probabilité de rôle :
        - 25% Nourrice
        - 25% Garde
        - 50% Ouvrière
        """

        ants = []
        for _ in range(Config.GAME_SETTINGS['ant_count']):
            position = self._random_nest_position()
            roll = random.random()
            if roll < 0.25:
                ants.append(Nourrice(position))
            elif roll < 0.50:
                ants.append(Garde(position))
            else:
                ants.append(Ouvriere(position))
        return ants

    
    def _random_nest_position(self) -> Tuple[float, float]:
        """
        Génère une position aléatoire à proximité du nid pour les fourmis.
        
        PRE: Nid déjà initialisé
        POST: 
        - Retourne des coordonnées x et y à proximité du nid
        - Position générée de manière aléatoire dans un rayon défini
        """
        # Générer des coordonnées légèrement dispersées autour du nid
        return (self.nest.position[0] + random.randint(-Config.SIZES['nest'], Config.SIZES['nest']),
                self.nest.position[1] + random.randint(-Config.SIZES['nest'], Config.SIZES['nest']))
    
    def update(self) -> None:
        """
        Méthode principale de mise à jour de la simulation.
        
        PRE: Simulation initialisée et en cours
        POST: 
        - Comportement des fourmis mis à jour
        - Conditions de victoire vérifiées
        """
        # Mettre à jour le comportement des fourmis et vérifier si la colonie a atteint son objectif
        self._process_ants()
        self._check_victory()
        self._spawn_menace()
        self._check_menace_collisions()
        self._update_pheromones() 
        for menace in self.menaces:
            menace.move()
    
    def _process_ants(self) -> None:
        """
        Gère le comportement de chaque fourmi selon son état actuel.

        Trois états possibles :
        - Recherche : déplacement aléatoire et détection de nourriture
        - Retour au nid : transport de nourriture vers le nid
        - Recherche de nourriture : se diriger vers une source de nourriture connue
        
        PRE: Liste des fourmis initialisée
        POST: 
        - État et position de chaque fourmi mis à jour
        - Interactions avec l'environnement (nourriture, phéromones) traitées
        """

        # Parcourir chaque fourmi et gérer son comportement en fonction de son état

    
        """
        Gère le comportement de chaque fourmi en appelant sa méthode spécifique perform_action().
        """
        for ant in self.ants:
            if isinstance(ant, Nourrice):
                ant.perform_action(self)  # Appel spécifique à la nourrice
            else:
                ant.perform_action(self)  # Garde ou ouvrière

    def _spawn_menace(self) -> None:
        """
        Tente de spawner une menace toutes les minutes avec 33% de chance.
        Limite : 4 menaces maximum.
        """
        if len(self.menaces) < 4 and time.time() - self.last_menace_spawn_time >= 60:
            self.last_menace_spawn_time = time.time()  # Réinitialise le temps du dernier spawn
            if random.random() <= 1:  # 33% de chance de spawn
                menace = Menace()
                self.menaces.append(menace)
                print(f"Nouvelle menace apparue à {menace.position}. Nombre total de menaces : {len(self.menaces)}")
    
    def _check_menace_collisions(self) -> None:
        """
        Vérifie les collisions entre les menaces et les fourmis.
        - Si une menace touche une fourmi, la fourmi disparaît.
        - Une phéromone d'alerte est laissée à la position de la fourmi.
        - Si une menace touche le nid, la simulation s'arrête (game over).
        """
        for menace in self.menaces:
            for ant in list(self.ants):  # Utilisation d'une copie pour éviter des erreurs
                distance = math.hypot(menace.position[0] - ant.position[0], menace.position[1] - ant.position[1])
                if distance < menace.size:
                    self.ants.remove(ant)
                    print(f"Une fourmi a été éliminée par une menace à {ant.position}.")

                    # Ajoute une phéromone d'alerte
                    self.pheromones.append(Pheromone(
                        position=ant.position,
                        food_source=None,
                        food_number=0,
                        alert=True,
                        expiration_time=time.time() + 30
                    ))
                    print(f"Phéromone d'alerte ajoutée à {ant.position}.")

    def _handle_pheromone_menace_collision(self, menace):
        """
        Gère les collisions entre une menace et les phéromones.
        Si une menace touche un phéromone, augmente la taille du phéromone.
        """
        for pheromone in self.pheromones:
            distance_to_pheromone = math.hypot(
                menace.position[0] - pheromone.position[0],
                menace.position[1] - pheromone.position[1]
            )

            if distance_to_pheromone < menace.size:  # Collision détectée
                print(f"Une menace a touché un phéromone à {pheromone.position}.")
                # Pas besoin d'augmenter la taille, car elle est définie à la création


    def _move_to_target(self, ant, target_position) -> None:
        """
        Déplace une fourmi en ligne droite vers une position cible.
        """
        dx = target_position[0] - ant.position[0]
        dy = target_position[1] - ant.position[1]
        distance = math.hypot(dx, dy)

        if distance > 0:
            speed = 2  # Ajuste la vitesse de déplacement ici
            ant.position = (
                ant.position[0] + (dx / distance) * speed,
                ant.position[1] + (dy / distance) * speed,
            )

    def _inform_gardes(self, ant):
        """
        Informe les gardes de la position d'une menace et les dirige vers celle-ci.
        """
        for garde in self.ants:
            if isinstance(garde, Garde):
                garde.target_position = ant.target_pheromone.position
                garde.is_attacking = True

    def _spawn_food(self, position) -> None:
        """
        Fait apparaître une source de nourriture après la destruction d'une menace.
        """
        food_amount = random.randint(10, 20)  # Génère une quantité aléatoire de nourriture
        new_food = Food(position, len(self.food_sources) + 1)
        new_food.resources = food_amount  # Définit la quantité de nourriture
        self.food_sources.append(new_food)
        print(f"Nouvelle source de nourriture créée avec {food_amount} unités à la position {position}.")

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

        # Parcourt toutes les sources de nourriture disponibles
        # Calcule la distance entre la fourmi et chaque source
        # Vérifie si la source est à portée et gère la collecte si possible
        if not isinstance(ant, Ouvriere):
            return False

        for food in self.food_sources:
            distance = math.hypot(ant.position[0] - food.position[0], ant.position[1] - food.position[1])
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
    
    def _update_pheromones(self) -> None:
        """
        Met à jour les phéromones :
        - Supprime les phéromones d'alerte expirées.
        """
        current_time = time.time()
        self.pheromones = [
            pheromone for pheromone in self.pheromones
            if not pheromone.alert or (pheromone.alert and pheromone.expiration_time > current_time)
        ]

    
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

        # Recherche de phéromones à proximité de la fourmi
        # Calcule la distance entre la fourmi et chaque phéromone
        # Définit une cible de nourriture si une phéromone est détectée
        for pheromone in self.pheromones:
            distance = math.hypot(
                ant.position[0] - pheromone.position[0],
                ant.position[1] - pheromone.position[1]
            )
            if distance < Config.GAME_SETTINGS['pheromone_detection_distance']:
                if isinstance(ant, Ouvriere) and not pheromone.alert:
                    ant.target_food = pheromone.food_source
                    return True
                elif isinstance(ant, Garde) and pheromone.alert:
                    ant.target_pheromone = pheromone
                    ant.is_attacking = True
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
            ant.position = (
                ant.position[0] + (dx / distance) * (5 / Config.GAME_SETTINGS['speed_reducer']),
                ant.position[1] + (dy / distance) * (5 / Config.GAME_SETTINGS['speed_reducer'])
            )

        if distance < Config.SIZES['nest']:
            if isinstance(ant, Ouvriere) and ant.state == "returning_to_nest":
                print("Ouvrière informe les gardes d'une menace.")
                self._activate_gardes()
                ant.state = "searching"  # L'ouvrière reprend son état normal

            if ant.has_food:
                self.nest.add_resource()
                ant.has_food = False
                ant.emitting_pheromones = False

    def _activate_gardes(self):
        for pheromone in self.pheromones:
            if pheromone.alert:
                for garde in self.ants:
                    if isinstance(garde, Garde):
                        garde.target_position = pheromone.position
                        garde.is_attacking = True
                        print(f"Garde activé pour défendre contre une menace à {pheromone.position}.")

    
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

        # Vérifie l'existence de la source de nourriture ciblée
        # Réinitialise la cible si la source n'existe plus
        if not ant.target_food or ant.target_food not in self.food_sources:
            ant.target_food = None
            ant.food_number = 0
            return

        
        # Calcul de la direction et de la distance vers la source de nourriture
        # Déplace la fourmi progressivement vers la source
        dx = ant.target_food.position[0] - ant.position[0]
        dy = ant.target_food.position[1] - ant.position[1]
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            ant.position = (
                ant.position[0] + (dx / distance) * (5 / Config.GAME_SETTINGS['speed_reducer']),
                ant.position[1] + (dy / distance) * (5 / Config.GAME_SETTINGS['speed_reducer'])
            )

        
        # Collecte des ressources à l'arrivée à la source
        # Gestion de l'épuisement de la source de nourriture
        if distance < Config.SIZES['food'] and not ant.target_food.is_empty():
            ant.has_food = True
            ant.target_food.take_resource()

            if ant.target_food.is_empty():
                self._remove_food_pheromones(ant.target_food.number)
                self.food_sources.remove(ant.target_food)
                ant.target_food = None
                ant.food_number = 0
    
    def _check_and_spawn_new_ant(self) -> bool:
        """
        Vérifie si 3 stacks sont disponibles pour créer une nouvelle fourmi.
        Si oui, spawn une nouvelle fourmi et réinitialise les stacks.

        Retourne True si une nouvelle fourmi est créée, False sinon.
        """
        total_stacks = sum(nourrice.stack for nourrice in self.ants if isinstance(nourrice, Nourrice))
        
        if total_stacks >= 3:
            # Réinitialiser les stacks
            for nourrice in self.ants:
                if isinstance(nourrice, Nourrice):
                    nourrice.stack = 0
            
            # Créer une nouvelle fourmi
            position = self._random_nest_position()
            roll = random.random()
            if roll < 0.25:
                self.ants.append(Nourrice(position))
            elif roll < 0.50:
                self.ants.append(Garde(position))
            else:
                self.ants.append(Ouvriere(position))
            
            print("Nouvelle fourmi créée !")
            return True

        return False

    
    def _add_pheromone(self, ant: Ant) -> None:
        """
        Ajoute une trace de phéromone laissée par une fourmi.
        
        PRE: 
        - Fourmi transportant de la nourriture
        - Liste des phéromones initialisée
        POST: 
        - Nouvelle phéromone ajoutée si la distance minimale est respectée
        """
        # Vérifie la distance minimale entre les phéromones
        # Ajoute une nouvelle phéromone si l'espacement est suffisant
        if not self.pheromones or math.hypot(
            ant.position[0] - self.pheromones[-1].position[0],
            ant.position[1] - self.pheromones[-1].position[1]
        ) > Config.GAME_SETTINGS['min_pheromone_distance']:
            self.pheromones.append(Pheromone(ant.position, ant.target_food, ant.food_number))
    
    def _remove_food_pheromones(self, food_number: int) -> None:
        """
        Supprime les phéromones associées à une source de nourriture épuisée.
        
        PRE: 
        - Source de nourriture épuisée
        - Liste des phéromones initialisée
        POST: 
        - Phéromones liées à la source de nourriture supprimées
        """

        # Filtre et supprime les phéromones associées à une source de nourriture spécifique
        self.pheromones = [p for p in self.pheromones if p.food_number != food_number]
    
    def _check_victory(self) -> None:
        """
        Vérifie si la colonie a atteint son objectif de ressources.
        
        PRE: 
        - Nid initialisé
        - Simulation en cours
        POST: 
        - Drapeau de victoire mis à jour si objectif atteint
        
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
        - Message de fin si applicable

        PRE: 
        - L'écran Pygame est initialisé
        - Tous les éléments de la simulation (nest, food_sources, pheromones, etc.) sont créés
        
        POST:
        - L'écran est mis à jour avec tous les éléments dessinés
        - L'affichage est rafraîchi
        """

        # Efface l'écran avec la couleur de fond
        self.screen.fill(Config.COLORS['background'])

        # Dessine successivement tous les éléments de la simulation
        self._render_nest()
        self._render_food()
        self._render_pheromones()
        self._render_queen()
        self._render_ants()
        self._render_menaces()
        self._render_victory()

        # Met à jour l'affichage
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

        # Dessine le nid
        pygame.draw.circle(self.screen, Config.COLORS['nest'],
                        self.nest.position, Config.SIZES['nest'])
        # Affiche le nombre de ressources du nid
        resources_text = self.font.render(f"Ressources du Nid : {self.nest.resources}",
                                        True, Config.COLORS['text'])
        self.screen.blit(resources_text,
                        (self.nest.position[0] - 50, self.nest.position[1] - 40))
        
    def _render_food(self) -> None:
        """
        Dessine les sources de nourriture et affiche leur numéro et ressources restantes.

        PRE:
        - La liste des sources de nourriture n'est pas vide
        - L'écran Pygame est initialisé
        - La police de caractères est prête

        POST:
        - Chaque source de nourriture est dessinée
        - Le numéro et les ressources de chaque source sont affichés
        """

        # Parcourt et dessine chaque source de nourriture
        for food in self.food_sources:
            pygame.draw.circle(self.screen, Config.COLORS['food'],
                            food.position, Config.SIZES['food'])

            # Affiche le numéro et les ressources restantes
            food_text = self.font.render(f"{food.number} ({food.resources})",
                                    True, (0, 0, 0))
            self.screen.blit(food_text,
                        (food.position[0] - 10, food.position[1] - 10))
        
    def _render_pheromones(self) -> None:
        """
        Dessine les traces de phéromones sur l'écran.

        PRE:
        - La liste des phéromones est initialisée
        - L'écran Pygame est prêt

        POST:
        - Toutes les phéromones sont dessinées sur l'écran
        """
        # Dessine un petit cercle pour chaque trace de phéromone
        for pheromone in self.pheromones:
            pygame.draw.circle(
                self.screen,
                Config.COLORS['pheromone'],
                (int(pheromone.position[0]), int(pheromone.position[1])),
                int(pheromone.size)  # Taille selon le type
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

        # Appelle la méthode de render de la reine
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
            pygame.draw.circle(self.screen, ant.color,
                            (int(ant.position[0]), int(ant.position[1])),
                            ant.size)

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
        
        # Vérifie si la fin de la simulation (100 food->nest) est atteint
        # Affiche le message centré à l'ecran
        if self.victory:
            win_text = self.win_font.render("Simulation terminée.", True, Config.COLORS['text'])
            self.screen.blit(win_text,
                        (Config.WINDOW_WIDTH // 2 - win_text.get_width() // 2,
                            Config.WINDOW_HEIGHT // 2 - win_text.get_height() // 2))
            
    def _render_menaces(self) -> None:
        """
        Dessine toutes les menaces sur la carte.
        """
        for menace in self.menaces:
            pygame.draw.circle(self.screen, menace.color,
                            (int(menace.position[0]), int(menace.position[1])),
                            menace.size)

        
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
        # Boucle principale qui gère les événements, met à jour et affiche la simulation
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.update()
            self.render()
        
        pygame.quit()
