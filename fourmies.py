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
Nbr_Bouffe = 5
Bouffe_Taille = 10
Nid_Taille = 30
Fourmi_Taille = 4
Pheromone_Taille = 5
Nbr_Fourmi = 50

VITESSE_REDUITE = 13  # Facteur de réduction de vitesse
DETECTION_PHEROMONE_DISTANCE = 10  # Distance de détection des phéromones
PHEROMONE_LIFETIME = 10  # Durée de vie des phéromones en secondes
PHEROMONE_DETECTION_FREQUENCY = 10  # Fréquence de détection en nombre de frames

# Initialisation des ressources du nid
ressources_nid = 0
RESSOURCES_NID_MAX = 100

# Créer la fenêtre
screen = pygame.display.set_mode((longueur, largeur))
pygame.display.set_caption("Simulation de Colonies de Fourmis - MVP")

# Définir la police pour l'affichage des ressources
font = pygame.font.SysFont(None, 24)

# Liste des phéromones avec leur timestamp
pheromones = []

# Classe pour la Fourmi
class Fourmi:
    def __init__(self, position):
        self.position = position
        self.nourriture_en_stock = 0  # Valeur initiale, 0 signifie qu'elle est en recherche
        self.direction = (random.randint(-1, 1) / VITESSE_REDUITE, random.randint(-1, 1) / VITESSE_REDUITE)  # Direction initiale
        self.temps_direction = time.time()  # Moment du dernier changement de direction
        self.duree_direction = random.uniform(0.5, 2)  # Durée pendant laquelle elle garde la direction
        self.destination = None  # La destination actuelle de la fourmi (nid ou nourriture)
        self.frame_counter = 0  # Compteur de frames pour réduire la fréquence de détection

    def mission(self):
        # Mission de la fourmi, selon sa valeur de nourriture
        if self.nourriture_en_stock == 1:
            return "Retour au nid"
        elif self.destination:
            return "Retour à la nourriture"
        else:
            return "Recherche"
    
    def deplacement_aleatoire(self):
        # Changer de direction si la durée est écoulée
        if time.time() - self.temps_direction >= self.duree_direction:
            # Générer une nouvelle direction et un nouveau délai
            self.direction = (random.randint(-1, 1) / VITESSE_REDUITE, random.randint(-1, 1) / VITESSE_REDUITE)
            self.temps_direction = time.time()
            self.duree_direction = random.uniform(0.2, 1)
        
        # Déplacer la fourmi dans la direction actuelle
        new_x = self.position[0] + self.direction[0]
        new_y = self.position[1] + self.direction[1]
        
        # Vérifier les limites de la fenêtre
        new_x = max(0, min(new_x, longueur))
        new_y = max(0, min(new_y, largeur))
        
        # Mettre à jour la position de la fourmi
        self.position = (new_x, new_y)
    
    def detecter_nourriture(self, Spawn_Bouffe):
        for bouffe in Spawn_Bouffe:
            # Calculer la distance entre la fourmi et la nourriture
            distance = math.hypot(self.position[0] - bouffe["position"][0], self.position[1] - bouffe["position"][1])
            if distance < Bouffe_Taille:
                # Si la nourriture est proche, changer de mission et passer à "Retour au nid"
                self.nourriture_en_stock = 1
                self.destination = bouffe  # Enregistrer cette nourriture comme destination
                bouffe["ressources"] -= 1  # Décrémenter la ressource de la nourriture trouvée
                # Vérifier si les ressources sont épuisées
                if bouffe["ressources"] <= 0:
                    Spawn_Bouffe.remove(bouffe)  # Supprimer la nourriture si ressource épuisée
                    self.destination = None  # Réinitialiser la destination si la nourriture est épuisée
                return True
        return False

    def retour_au_nid(self):
        # Calculer le vecteur de déplacement vers le nid
        dx = Nid_Position[0] - self.position[0]
        dy = Nid_Position[1] - self.position[1]
        distance = math.hypot(dx, dy)

        # Déplacement progressif vers le nid avec une vitesse réduite
        if distance > 0:
            move_x = self.position[0] + (dx / distance) * (5 / VITESSE_REDUITE)
            move_y = self.position[1] + (dy / distance) * (5 / VITESSE_REDUITE)
            self.position = (move_x, move_y)

        # Si elle arrive au nid, déposer la nourriture au nid et repasser en mode retour à la nourriture
        if distance < Nid_Taille and self.nourriture_en_stock == 1:
            global ressources_nid
            ressources_nid = min(RESSOURCES_NID_MAX, ressources_nid + 1)
            self.nourriture_en_stock = 0
            return True
        return False

    def retour_vers_nourriture(self):
        if self.destination:  # S'assurer qu'il y a une destination
            dx = self.destination["position"][0] - self.position[0]
            dy = self.destination["position"][1] - self.position[1]
            distance = math.hypot(dx, dy)

            if distance > 0:
                move_x = self.position[0] + (dx / distance) * (5 / VITESSE_REDUITE)
                move_y = self.position[1] + (dy / distance) * (5 / VITESSE_REDUITE)
                self.position = (move_x, move_y)

            # Si elle arrive à la nourriture, reprendre de la nourriture si disponible
            if distance < Bouffe_Taille and self.destination["ressources"] > 0:
                self.nourriture_en_stock = 1
                self.destination["ressources"] -= 1
                # Vérifier si la nourriture est épuisée
                if self.destination["ressources"] <= 0:
                    Spawn_Bouffe.remove(self.destination)  # Supprimer la nourriture si épuisée
                    self.destination = None  # Réinitialiser la destination

    def deposer_pheromone(self):
        # Ajouter la position actuelle comme point de phéromone avec un lien vers la source de nourriture
        if self.nourriture_en_stock == 1:  # Seulement pendant le retour au nid
            pheromones.append({"position": self.position, "time_created": time.time(), "nourriture": self.destination})

    def detecter_pheromone(self, pheromones):
        # Vérifie les phéromones seulement tous les PHEROMONE_DETECTION_FREQUENCY frames
        self.frame_counter += 1
        if self.frame_counter % PHEROMONE_DETECTION_FREQUENCY != 0:
            return False

        for pheromone in pheromones:
            # Calculer la distance entre la fourmi et le point de phéromone
            distance = math.hypot(self.position[0] - pheromone["position"][0], self.position[1] - pheromone["position"][1])
            if distance < DETECTION_PHEROMONE_DISTANCE and pheromone["nourriture"] is not None and pheromone["nourriture"]["ressources"] > 0:
                # Si elle détecte une phéromone valide, elle commence les allers-retours vers la nourriture
                self.destination = pheromone["nourriture"]
                return True
        return False

# Le reste du code (génération de la nourriture, boucles de déplacement) reste inchangé...


# Générer les positions et valeurs de la nourriture
Spawn_Bouffe = []
for i in range(Nbr_Bouffe):
    bx = random.randint(0, longueur)
    by = random.randint(0, largeur)
    ressource = random.randint(10, 50)
    Spawn_Bouffe.append({"position": (bx, by), "ressources": ressource})

# Générer la position du nid aléatoirement
Nid_Position = (random.randint(0, longueur), random.randint(0, largeur))

# Générer les fourmis autour du nid
Spawn_Fourmis = []
for i in range(Nbr_Fourmi):
    fx = random.randint(-Nid_Taille, Nid_Taille)
    fy = random.randint(-Nid_Taille, Nid_Taille)
    position = (Nid_Position[0] + fx, Nid_Position[1] + fy)
    fourmi = Fourmi(position)
    Spawn_Fourmis.append(fourmi)

# Boucle principale
running = True
while running:
    # Gérer les événements (fermeture de fenêtre)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Nettoyer les phéromones plus anciennes que la durée de vie
    current_time = time.time()
    pheromones = [p for p in pheromones if current_time - p["time_created"] < PHEROMONE_LIFETIME]

    # Remplir l'arrière-plan
    screen.fill(Bg_Couleur)

    # Dessiner le nid et afficher la ressource du nid
    pygame.draw.circle(screen, Nid_Couleur, Nid_Position, Nid_Taille)
    texte_nid = font.render(f"Ressources du Nid : {ressources_nid}", True, (255, 255, 255))
    screen.blit(texte_nid, (Nid_Position[0] - 50, Nid_Position[1] - 40))

    # Dessiner les points de nourriture et afficher leurs ressources
    for bouffe in Spawn_Bouffe:
        pos = bouffe["position"]
        pygame.draw.circle(screen, Bouffe_Couleur, pos, Bouffe_Taille)
        texte_ressource = font.render(str(bouffe["ressources"]), True, (0, 0, 0))
        screen.blit(texte_ressource, (pos[0] - 10, pos[1] - 10))

    # Dessiner les phéromones
    for pheromone in pheromones:
        pygame.draw.circle(screen, Pheromone_Couleur, pheromone["position"], Pheromone_Taille)

    # Dessiner et déplacer les fourmis
    for fourmi in Spawn_Fourmis:
        if fourmi.mission() == "Recherche":
            # Vérifier si la fourmi détecte une phéromone
            if not fourmi.detecter_pheromone(pheromones):
                fourmi.deplacement_aleatoire()
                fourmi.detecter_nourriture(Spawn_Bouffe)
        elif fourmi.mission() == "Retour au nid":
            fourmi.deposer_pheromone()  # Déposer des phéromones pendant le retour
            if fourmi.retour_au_nid():
                print("Fourmi de retour au nid, retourne à la nourriture")
        elif fourmi.mission() == "Retour à la nourriture":
            fourmi.retour_vers_nourriture()

        pygame.draw.circle(screen, Fourmi_Couleur, (int(fourmi.position[0]), int(fourmi.position[1])), Fourmi_Taille)

    # Mettre à jour l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()


