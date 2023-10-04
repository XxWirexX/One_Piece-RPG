import pickle
import sys

import pygame
import pytmx
import pyscroll

from player import Player
from dialog import DialogBox
from map import MapManager

class Game:
    def __init__(self):
        # Démarrage
        self.running = True
        self.map = "world"

        # Affichage de la fenêtre
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("BasiqueGame")

        self.player = Player()
        self.map_manager = MapManager(self.screen, self.player)
        self.dialog_box = DialogBox()

    def handle_input(self):
        pressed = pygame.key.get_pressed()

        if (pressed[pygame.K_UP]):
            self.player.move_top()
        elif (pressed[pygame.K_DOWN]):
            self.player.move_bottom()
        elif (pressed[pygame.K_LEFT]):
            self.player.move_left()
        elif (pressed[pygame.K_RIGHT]):
            self.player.move_right()

    def update(self):
        self.map_manager.update()

    def save_game_data(self, datas={}):
        with open("./saves/save", "wb") as file:
            pickle.dump(datas, file)

    def load_game_data(self):
        try:
            with open("./saves/save", "rb") as file:
                datas = int(pickle.load(file))
                return datas
        except FileNotFoundError:
            return None

    def quit(self):
        #self.save_game_data({
        #    "world": self.map_manager.get_map(),
        #    "position": [self.player.position[0], self.player.position[1]]
        #})
        pygame.quit()
        sys.exit()

    def run(self):
        clock = pygame.time.Clock()

        # Clock
        while self.running:
            self.player.save_location()
            self.handle_input()
            self.update()
            self.map_manager.draw()
            self.dialog_box.render(self.screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.map_manager.check_npc_collision(self.dialog_box)

                if event.type == pygame.QUIT:
                    self.running = False

            clock.tick(60)

        self.quit()