import pygame

# Colors
BG_COLOR = (10, 10, 26) # Deep dark blue/purple
NODE_COLOR = (0, 243, 255) # Cyan
NODE_HOVER_COLOR = (255, 0, 127) # Neon Pink
EDGE_COLOR = (60, 60, 90) # Dark gray-blue
EDGE_NEW_COLOR = (57, 255, 20) # Neon Green
TEXT_COLOR = (240, 240, 250)
PANEL_BG = (18, 18, 30) # For alpha blending
RECOMMEND_COLOR = (255, 215, 0) # Bright Gold
TRAVERSAL_COLOR = (255, 0, 127) # Pink 
PATH_COLOR = (57, 255, 20)

# Physics Constants
SPRING_LENGTH = 160
SPRING_K = 0.05
REPULSION_K = 60000
DAMPING = 0.85
MAX_VELOCITY = 15

# Screen
WIDTH, HEIGHT = 1400, 850
FPS = 60
NODE_RADIUS = 25
