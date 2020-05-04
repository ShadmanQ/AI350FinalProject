from AIs import BasicAI
import pygame

class Human(BasicAI.BasicAI):

    def get_move(self,state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            keys = pygame.key.get_pressed()
            print(keys)

            for key in keys:
                if keys[pygame.K_LEFT]:
                    return 'LEFT'

                elif keys[pygame.K_RIGHT]:
                    return 'RIGHT'

                elif keys[pygame.K_UP]:
                    return 'UP'

                elif keys[pygame.K_DOWN]:
                    return 'DOWN'
        return ''
