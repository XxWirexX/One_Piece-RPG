from dataclasses import dataclass

import pygame, pytmx, pyscroll

from src.player import NPC


@dataclass
class Portal:
    default_world: str
    origin_point: str
    target_world: str
    teleport_point: str

@dataclass
class Map:
    name: str
    walls: list[pygame.Rect]
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]
    npcs: list[NPC]

class MapManager:
    def __init__(self, screen, player):
        self.maps = dict()
        self.screen = screen
        self.player = player
        self.current_map = "world"

        self.register_map("world", portals=[
            Portal(default_world="world", origin_point="enter_house", target_world="house", teleport_point="spawn_house"),
            Portal(default_world="world", origin_point="enter_house2", target_world="house2", teleport_point="spawn_house"),
            Portal(default_world="world", origin_point="enter_dungeon", target_world="dungeon", teleport_point="spawn_dungeon"),
        ], npcs=[
            NPC("paul", nb_points = 4, dialog=[
                "Salut, je m'appelle Paul",
                "Comment vas tu ?"
            ]),
            NPC("robin", nb_points=2, dialog=[
                "Salut, je m'appelle Robin",
                "Bonne aventure !"
            ]),
        ])
        self.register_map("house", portals=[
            Portal(default_world="house", origin_point="exit_house", target_world="world", teleport_point="enter_house_exit")
        ])

        self.register_map("house2", portals=[
            Portal(default_world="house2", origin_point="exit_house", target_world="world", teleport_point="exit_house2")
        ])

        self.register_map("dungeon", portals=[
            Portal(default_world="dungeon", origin_point="exit_dungeon", target_world="world", teleport_point="exit_dungeon_spawn"),
            Portal(default_world="dungeon", origin_point="grotte_finale", target_world="dungeon",
                   teleport_point="spawn_final"),
            Portal(default_world="dungeon", origin_point="grotte", target_world="dungeon",
                   teleport_point="spawn_grotte")
        ], npcs=[
            NPC("boss", nb_points=6, dialog=[]),
        ])

        self.teleport_player("spawn")
        self.teleport_npcs()

    def check_npc_collision(self, dialog_box):
        for sprite in self.get_group().sprites():
            if sprite.feet.colliderect(self.player.rect) and type(sprite) is NPC:
                dialog_box.execute(sprite.dialog )

    def check_collision(self):
        for portal in self.get_map().portals:
            if portal.default_world == self.current_map:
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)

                if self.player.feet.colliderect(rect):
                    copy_portal = portal
                    self.current_map = portal.target_world
                    self.teleport_player(copy_portal.teleport_point)

        for sprite in self.get_group().sprites():
            if type(sprite) is NPC:
                if sprite.feet.colliderect(self.player.rect):
                    sprite.speed = 0
                else:
                    sprite.speed = 1

            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()

    def teleport_player(self, name):
        point = self.get_object(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location()

    def register_map(self, name, portals=[], npcs=[]):
        tmx_data = pytmx.util_pygame.load_pygame(f"map/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2

        walls = []

        for obj in tmx_data.objects:
            if obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=5)
        group.add(self.player)

        for npc in npcs:
            group.add(npc)

        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs)

    def get_map(self): return self.maps[self.current_map]

    def get_group(self): return self.get_map().group

    def get_walls(self): return self.get_map().walls

    def get_object(self, name): return self.get_map().tmx_data.get_object_by_name(name)

    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs

            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()

    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)

    def update(self):
        self.get_group().update()
        self.check_collision()

        for npc in self.get_map().npcs:
            npc.move()