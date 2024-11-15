import random
import pygame
import math
import time

pygame.init()

# Paramètres de la fenêtre et des couleurs
longueur, largeur = 1920, 1080
Bg_Couleur = (181, 101, 29)
Bouffe_Couleur = (0, 255, 0)
Nid_Couleur = (101, 67, 33)
Fourmi_Couleur = (0, 0, 0)
Pheromone_Couleur = (200, 200, 255)
Reine_Couleur = (0, 0, 0)
Nbr_Bouffe = 5
Bouffe_Taille = 20
Nid_Taille = 50
Fourmi_Taille = 4
Reine_Taille = 10
Pheromone_Taille = 10
Nbr_Fourmi = 10

VITESSE_REDUITE = 13
DETECTION_PHEROMONE_DISTANCE = 15  # Distance de détection des phéromones
DETECTION_PHEROMONE_MIN_DISTANCE = 20  # Distance minimale pour poser une phéromone

# Initialisation des ressources du nid
ressources_nid = 0
RESSOURCES_NID_MAX = 100

# Créer la fenêtre
screen = pygame.display.set_mode((longueur, largeur))
pygame.display.set_caption("Simulation de Colonie de Fourmis - MVP")
font = pygame.font.SysFont(None, 24)
win_font = pygame.font.SysFont(None, 72)


pheromones = []

class Reine:
    '''
    
    '''
    def __init__(self, position):
        self.position = position

    def afficher(self, surface):
        pygame.draw.circle(surface, Reine_Couleur, (int(self.position[0]), int(self.position[1])), Reine_Taille)


class Fourmi:
    '''
    
    '''
    def __init__(self, position):
        self.position = position
        self.nourriture_en_stock = 0
        self.direction = (random.randint(-1, 1) / VITESSE_REDUITE, random.randint(-1, 1) / VITESSE_REDUITE)
        self.temps_direction = time.time()
        self.duree_direction = random.uniform(0.5, 2)
        self.destination = None
        self.emission_pheromones = 0  # État d'émission des phéromones
        self.numéro_spawn = 0  # Numéro du spawn de nourriture touché, par défaut 0

    def mission(self):
        if self.nourriture_en_stock == 1:
            return "Retour au nid"
        elif self.destination:
            return "Retour à la nourriture"
        else:
            return "Recherche"

    def deplacement_aleatoire(self):
        if time.time() - self.temps_direction >= self.duree_direction:
            self.direction = (random.choice([-1, 0, 1]) / VITESSE_REDUITE, random.choice([-1, 0, 1]) / VITESSE_REDUITE)
            self.temps_direction = time.time()
            self.duree_direction = random.uniform(0.5, 1.5)
        
        new_x = max(0, min(self.position[0] + self.direction[0], longueur))
        new_y = max(0, min(self.position[1] + self.direction[1], largeur))
        self.position = (new_x, new_y)
    
    def detecter_nourriture(self, Spawn_Bouffe):
        for bouffe in Spawn_Bouffe:
            distance = math.hypot(self.position[0] - bouffe["position"][0], self.position[1] - bouffe["position"][1])
            if distance < Bouffe_Taille:
                # Si la nourriture est disponible pour la création de phéromones
                if bouffe["chemin_pheromone_actif"] == 1:
                    self.nourriture_en_stock = 1
                    self.destination = bouffe
                    bouffe["ressources"] -= 1
                    self.emission_pheromones = 1  # Activer l'émission de phéromones
                    bouffe["chemin_pheromone_actif"] = 0  # Désactiver pour les autres fourmis
                    self.numéro_spawn = bouffe["numéro"]  # Enregistrer le numéro du spawn
                elif bouffe["ressources"] > 0:
                    self.nourriture_en_stock = 1
                    self.destination = bouffe
                    bouffe["ressources"] -= 1
                    self.numéro_spawn = bouffe["numéro"]  # Enregistrer le numéro du spawn
                return True
        return False

    def retour_au_nid(self):
        dx, dy = Nid_Position[0] - self.position[0], Nid_Position[1] - self.position[1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.position = (self.position[0] + (dx / distance) * (5 / VITESSE_REDUITE),
                             self.position[1] + (dy / distance) * (5 / VITESSE_REDUITE))
            # Déposer des phéromones si l'émission est active
            if self.emission_pheromones == 1:
                # Ajoute une phéromone tous les `DETECTION_PHEROMONE_MIN_DISTANCE`
                if not pheromones or math.hypot(self.position[0] - pheromones[-1]["position"][0],
                                                self.position[1] - pheromones[-1]["position"][1]) > DETECTION_PHEROMONE_MIN_DISTANCE:
                    pheromones.append({"position": self.position, "nourriture": self.destination, "numéro": self.numéro_spawn})
        if distance < Nid_Taille and self.nourriture_en_stock == 1:
            global ressources_nid
            ressources_nid = min(RESSOURCES_NID_MAX, ressources_nid + 1)
            self.nourriture_en_stock = 0
            self.emission_pheromones = 0  # Désactiver l'émission des phéromones après le retour au nid
            return True
        return False

    def retour_vers_nourriture(self):
        # Vérifier si la destination est toujours dans Spawn_Bouffe
        if not self.destination or self.destination not in Spawn_Bouffe:
            self.destination = None  # Si la nourriture est épuisée, revenir en mode recherche
            self.numéro_spawn = 0  # Réinitialiser le numéro du spawn de nourriture
            return

        dx, dy = self.destination["position"][0] - self.position[0], self.destination["position"][1] - self.position[1]
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.position = (self.position[0] + (dx / distance) * (5 / VITESSE_REDUITE),
                             self.position[1] + (dy / distance) * (5 / VITESSE_REDUITE))

        if distance < Bouffe_Taille and self.destination["ressources"] > 0:
            self.nourriture_en_stock = 1
            self.destination["ressources"] -= 1
            if self.destination["ressources"] <= 0:
                # Supprimer le spawn de nourriture épuisé et les phéromones associées
                self.invalidate_pheromones(self.destination["numéro"])
                Spawn_Bouffe.remove(self.destination)
                self.destination = None  # Réinitialiser la destination
                self.numéro_spawn = 0  # Réinitialiser le numéro du spawn de nourriture

    def detecter_pheromone(self):
        for pheromone in pheromones:
            distance = math.hypot(self.position[0] - pheromone["position"][0], self.position[1] - pheromone["position"][1])
            if distance < DETECTION_PHEROMONE_DISTANCE:
                # Si la fourmi détecte un point de phéromone, elle suit le chemin vers le spawn de nourriture associé
                self.destination = pheromone["nourriture"]
                return True
        return False

    def invalidate_pheromones(self, numéro_spawn):
        # Supprimer les phéromones associées au spawn de nourriture
        global pheromones
        pheromones = [p for p in pheromones if p["numéro"] != numéro_spawn]

# Générer les positions et valeurs de la nourriture avec un numéro unique pour chaque spawn
Spawn_Bouffe = [{"position": (random.randint(0, longueur), random.randint(0, largeur)), 
                 "ressources": random.randint(10, 50), 
                 "chemin_pheromone_actif": 1,
                 "numéro": i + 1} for i in range(Nbr_Bouffe)]
Nid_Position = (random.randint(0, longueur), random.randint(0, largeur))
Spawn_Fourmis = [Fourmi((Nid_Position[0] + random.randint(-Nid_Taille, Nid_Taille),
                         Nid_Position[1] + random.randint(-Nid_Taille, Nid_Taille))) for _ in range(Nbr_Fourmi)]

# Initialiser la reine près du nid
reine = Reine((Nid_Position[0] + 10, Nid_Position[1] + 10))

# Boucle principale
running = True
you_win = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(Bg_Couleur)
    pygame.draw.circle(screen, Nid_Couleur, Nid_Position, Nid_Taille)
    screen.blit(font.render(f"Ressources du Nid : {ressources_nid}", True, (255, 255, 255)), (Nid_Position[0] - 50, Nid_Position[1] - 40))

    reine.afficher(screen)

    for bouffe in Spawn_Bouffe:
        pos = bouffe["position"]
        pygame.draw.circle(screen, Bouffe_Couleur, pos, Bouffe_Taille)
        screen.blit(font.render(f"{bouffe['numéro']} ({bouffe['ressources']})", True, (0, 0, 0)), (pos[0] - 10, pos[1] - 10))

    # Dessiner les phéromones
    for pheromone in pheromones:
        pygame.draw.circle(screen, Pheromone_Couleur, (int(pheromone["position"][0]), int(pheromone["position"][1])), Pheromone_Taille)

    for fourmi in Spawn_Fourmis:
        if fourmi.mission() == "Recherche":
            # Essayer de détecter une phéromone
            if not fourmi.detecter_pheromone():
                fourmi.deplacement_aleatoire()
                fourmi.detecter_nourriture(Spawn_Bouffe)
        elif fourmi.mission() == "Retour au nid":
            fourmi.retour_au_nid()
        elif fourmi.mission() == "Retour à la nourriture":
            fourmi.retour_vers_nourriture()
        pygame.draw.circle(screen, Fourmi_Couleur, (int(fourmi.position[0]), int(fourmi.position[1])), Fourmi_Taille)

    # Vérifier si le joueur a gagné
    if ressources_nid >= RESSOURCES_NID_MAX:
        you_win = True

    # Afficher "Gagné !" si les ressources du nid sont à 100
    if you_win:
        win_text = win_font.render("Gagné !", True, (255, 255, 255))
        screen.blit(win_text, (longueur // 2 - win_text.get_width() // 2, largeur // 2 - win_text.get_height() // 2))

    pygame.display.flip()

pygame.quit()
