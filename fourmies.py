import random
import pygame

pygame.init()

longueur, largeur = 1920, 1080
Bg_Couleur = (181, 101, 29)
Bouffe_Couleur = (0, 255, 0)
Nbr_Bouffe = 5
Bouffe_Taille = 10
Nid_Couleur = (101, 67, 33)
Nid_Taille = 30
Fourmi_Taille = 4
Fourmi_Couleur = (0, 0, 0)  
Nbr_Fourmi = 10


screen = pygame.display.set_mode((longueur, largeur))
pygame.display.set_caption("Simulation de Colonies de Fourmis - MVP")


class Fourmi:
    def __init__(self, position):
        self.position = position
        self.nourriture_en_stock = 0 

    def mission(self):
        if self.nourriture_en_stock == 1:
            return "Retour au nid"
        else:
            return "Recherche"
    def deplacement_aleatoire(self):
        dx = random.randint(-5, 5)
        dy = random.randint(-5, 5)
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        new_x = max(0, min(new_x, longueur))
        new_y = max(0, min(new_y, largeur))

        self.position = (new_x, new_y)


Spawn_Bouffe = []
for i in range(Nbr_Bouffe):
    bx = random.randint(0, longueur)
    by = random.randint(0, largeur)
    ressource = random.randint(10, 50)
    Spawn_Bouffe.append({"position": (bx, by), "ressources": ressource})

Nid_Position = (random.randint(0, longueur), random.randint(0, largeur))

Spawn_Fourmis = []
for i in range(Nbr_Fourmi):
    fx = random.randint(-Nid_Taille, Nid_Taille)
    fy = random.randint(-Nid_Taille, Nid_Taille)
    position = (Nid_Position[0] + fx, Nid_Position[1] + fy)
    fourmi = Fourmi(position)  
    Spawn_Fourmis.append(fourmi)

running = True
while running:
    # Gérer les événements (fermeture de fenêtre)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Remplir l'arrière-plan
    screen.fill(Bg_Couleur)

    # Dessiner le nid
    pygame.draw.circle(screen, Nid_Couleur, Nid_Position, Nid_Taille)

    # Dessiner les points de nourriture
    for bouffe in Spawn_Bouffe:
        pos = bouffe["position"]
        pygame.draw.circle(screen, Bouffe_Couleur, pos, Bouffe_Taille)

    # Dessiner les fourmis autour du nid
    for fourmi in Spawn_Fourmis:
        if fourmi.mission() == "Recherche":
            fourmi.deplacement_aleatoire()
        pygame.draw.circle(screen, Fourmi_Couleur, fourmi.position, Fourmi_Taille)

    # Mettre à jour l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
