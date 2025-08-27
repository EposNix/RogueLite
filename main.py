import pygame
import sys
from game import Game

def main():
    pygame.init()
    
    # Game constants
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    FPS = 60
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("No Turns, Only Vibes - Simultaneous Deckbuilder")
    clock = pygame.time.Clock()
    
    game = Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
        
        game.update(dt)
        game.draw()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()