import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load(f"sprites/{name}.png")
        self.image = self.get_image(0, 0)
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect()
        self.position = [x, y]
        self.change_image = 0
        self.images = {
            "bottom": lambda i: self.get_image(i * 32, 0),
            "left": lambda i: self.get_image(i * 32, 32),
            "right": lambda i:  self.get_image(i * 32, 64),
            "top": lambda i: self.get_image(i * 32, 96)
        }

        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()
        self.speed = 2

    def save_location(self): self.old_position = self.position.copy()

    def change_animation(self, name):
        if self.change_image >= 3:
            self.change_image = 0
        self.image = self.images[name](int(self.change_image))
        self.change_image += 0.1
        self.image.set_colorkey([0, 0, 0])


    def move_top(self):
        self.position[1] -= self.speed
        self.change_animation("top")

    def move_bottom(self):
        self.position[1] += self.speed
        self.change_animation("bottom")

    def move_left(self):
        self.position[0] -= self.speed
        self.change_animation("left")

    def move_right(self):
        self.position[0] += self.speed
        self.change_animation("right")

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def get_image(self, x, y):
        image = pygame.Surface([32, 32])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image
    
class Player(Entity):
    def __init__(self):
        super().__init__("player", 0, 0)

class NPC(Entity):
    def __init__(self, name, nb_points, dialog):
        super().__init__(name, 0, 0)
        self.name = name
        self.nb_points = nb_points
        self.dialog = dialog
        self.points = []
        self.current_point = 0
        self.speed = 1

    def move(self):
        current_point = self.current_point
        target_point = self.current_point + 1

        if target_point >= self.nb_points:
            target_point = 0
        current_rect = self.points[current_point]
        target_rect = self.points[target_point]

        if current_rect.y < target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_bottom()
        elif current_rect.y > target_rect.y and abs(current_rect.x - target_rect.x) < 3:
            self.move_top()
        elif current_rect.x > target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_left()
        elif current_rect.x < target_rect.x and abs(current_rect.y - target_rect.y) < 3:
            self.move_right()

        if self.rect.colliderect(target_rect):
            self.current_point = target_point

    def teleport_spawn(self):
        location = self.points[self.current_point]
        self.position[0] = location.x
        self.position[1] = location.y
        self.save_location()

    def load_points(self, tmx_data):
        for i in range(1, self.nb_points + 1):
            point = tmx_data.get_object_by_name(f"{self.name}_path{i}")
            rect = pygame.Rect(point.x, point.y, point.width, point.height)
            self.points.append(rect)