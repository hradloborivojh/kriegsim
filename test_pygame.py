#!/usr/bin/env python3
"""
Simple pygame test to verify window display works
"""

import pygame
import sys
import time

def test_pygame_window():
    print("Testing pygame window display...")
    
    # Initialize pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Kriegsim Test Window")
    
    # Colors
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    
    print("✓ Window created - you should see a test window now!")
    print("The window will show:")
    print("  - Colored rectangles")
    print("  - Moving circle")
    print("  - Frame counter")
    print("Close the window to exit.")
    
    while running and frame_count < 300:  # Run for 30 seconds max
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw some test shapes
        pygame.draw.rect(screen, RED, (50, 50, 100, 100))
        pygame.draw.rect(screen, GREEN, (200, 50, 100, 100))
        pygame.draw.rect(screen, BLUE, (350, 50, 100, 100))
        
        # Draw moving circle
        circle_x = 50 + (frame_count * 2) % 700
        pygame.draw.circle(screen, WHITE, (circle_x, 300), 20)
        
        # Draw text
        font = pygame.font.Font(None, 36)
        text = font.render(f"Frame: {frame_count}", True, WHITE)
        screen.blit(text, (50, 400))
        
        # Update display
        pygame.display.flip()
        clock.tick(10)  # 10 FPS
        frame_count += 1
        
        if frame_count % 50 == 0:
            print(f"Frame {frame_count} - window should be visible")
    
    pygame.quit()
    print("✓ Test completed")

if __name__ == "__main__":
    test_pygame_window()
