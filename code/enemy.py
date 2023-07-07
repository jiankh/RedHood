import pygame
from tiles import AnimatedTile
from random import randint

class Enemy(AnimatedTile):
    def __init__(self,size,x,y):
        super().__init__(size,x,y, '../graphics/enemy/boar' )
        self.speed = randint(1,2)
        
    def move(self):
        self.rect.x += self.speed

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def reverse(self):
        self.speed *= -1 

    def update(self, x_shift):
        self.rect.x += x_shift
        self.animate() #THIS from inherited animated tile. we overide update, must add it again
        self.reverse_image()
        self.move()