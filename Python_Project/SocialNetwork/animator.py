import pygame
import math
from config import *

class Animator:
    def __init__(self, graph, screen):
        self.graph = graph
        self.screen = screen
        self.particles = []
        self.highlighted_nodes = set()
        self.highlighted_edges = set() # tuples of (id1, id2)
        self.node_colors = {} # id -> color
        self.selected_node = None
        self.time = 0
        
    def draw_background_grid(self):
        # Subtle moving grid
        spacing = 40
        offset_x = (self.time * 0.5) % spacing
        offset_y = (self.time * 0.5) % spacing
        
        # Determine grid color
        grid_color = (25, 25, 45)
        for x in range(0, WIDTH + spacing, spacing):
            pygame.draw.line(self.screen, grid_color, (x + offset_x, 0), (x + offset_x, HEIGHT))
        for y in range(0, HEIGHT + spacing, spacing):
            pygame.draw.line(self.screen, grid_color, (0, y + offset_y), (WIDTH, y + offset_y))
        
    def update_physics(self):
        nodes = list(self.graph.nodes.values())
        
        # Reset forces
        for node in nodes:
            node.fx = 0
            node.fy = 0
            
        # Repulsion
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                dx = n1.x - n2.x
                dy = n1.y - n2.y
                dist_sq = dx*dx + dy*dy
                if dist_sq == 0: dist_sq = 0.01
                force = REPULSION_K / dist_sq
                dist = math.sqrt(dist_sq)
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                n1.fx += fx
                n1.fy += fy
                n2.fx -= fx
                n2.fy -= fy
                
        # Attraction (Spring)
        for node in nodes:
            for friend_id in node.friends:
                if friend_id > node.id: # Process each edge once
                    friend = self.graph.get_node(friend_id)
                    if not friend: continue
                    dx = friend.x - node.x
                    dy = friend.y - node.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist == 0: dist = 0.01
                    # Logarithmic spring scaling for smoother interaction
                    force = SPRING_K * (dist - SPRING_LENGTH)
                    fx = (dx / dist) * force
                    fy = (dy / dist) * force
                    node.fx += fx
                    node.fy += fy
                    friend.fx -= fx
                    friend.fy -= fy
                    
        # Apply forces and update positions
        for node in nodes:
            if node == self.selected_node:
                continue # Skip physics for selected node
                
            node.vx = (node.vx + node.fx) * DAMPING
            node.vy = (node.vy + node.fy) * DAMPING
            
            # Limit velocity
            speed = math.sqrt(node.vx**2 + node.vy**2)
            if speed > MAX_VELOCITY:
                node.vx = (node.vx / speed) * MAX_VELOCITY
                node.vy = (node.vy / speed) * MAX_VELOCITY
                
            node.x += node.vx
            node.y += node.vy
            
            # Keep within bounds (padding for panels)
            node.x = max(350, min(WIDTH - 50, node.x))
            node.y = max(50, min(HEIGHT - 50, node.y))
        
        self.time += 1
            
    def draw_glow(self, surface, color, pos, radius):
        # Create a surface with alpha for glowing
        glow_surf = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            alpha = int(255 * (0.15 / i))
            pygame.draw.circle(glow_surf, (*color[:3], alpha), (radius*2, radius*2), radius * i * 0.9)
        surface.blit(glow_surf, (pos[0] - radius*2, pos[1] - radius*2))

    def draw(self):
        self.draw_background_grid()
        nodes = list(self.graph.nodes.values())
        
        # Draw edges
        for node in nodes:
            for friend_id in node.friends:
                if friend_id > node.id:
                    friend = self.graph.get_node(friend_id)
                    if not friend: continue
                    edge_tuple = tuple(sorted((node.id, friend_id)))
                    
                    color = PATH_COLOR if edge_tuple in self.highlighted_edges else EDGE_COLOR
                    width = 4 if edge_tuple in self.highlighted_edges else 2
                    
                    if width > 2:
                        pygame.draw.line(self.screen, color, (node.x, node.y), (friend.x, friend.y), width)
                    else:
                        pygame.draw.aaline(self.screen, color, (node.x, node.y), (friend.x, friend.y))
                    
        # Draw nodes
        for node in nodes:
            pos = (int(node.x), int(node.y))
            color = self.node_colors.get(node.id, NODE_COLOR)
            
            # Subtle pulse effect for all nodes
            base_radius = NODE_RADIUS + math.sin(self.time * 0.05 + node.id) * 1.5
            
            if node.id in self.highlighted_nodes:
                base_radius += 3
                self.draw_glow(self.screen, RECOMMEND_COLOR, pos, base_radius)
                color = RECOMMEND_COLOR
            elif node == self.selected_node:
                base_radius += 2
                self.draw_glow(self.screen, NODE_HOVER_COLOR, pos, base_radius)
                color = NODE_HOVER_COLOR
                
            pygame.draw.circle(self.screen, color, pos, int(base_radius))
            
            # Outline
            pygame.draw.circle(self.screen, (255, 255, 255), pos, int(base_radius), 2)
            
            # Text
            try:
                font = pygame.font.SysFont("Segoe UI", 13, bold=True)
            except:
                font = pygame.font.SysFont("Arial", 13, bold=True)
                
            text_surf = font.render(str(node.id), True, (0, 0, 0))
            self.screen.blit(text_surf, text_surf.get_rect(center=pos))
            
            name_surf = font.render(node.name, True, TEXT_COLOR)
            name_x = pos[0] - name_surf.get_width()//2
            name_y = pos[1] + int(base_radius) + 5
            
            # Shadow for name
            shadow = font.render(node.name, True, (0, 0, 0))
            self.screen.blit(shadow, (name_x + 1, name_y + 1))
            self.screen.blit(name_surf, (name_x, name_y))
