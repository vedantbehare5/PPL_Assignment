import pygame
from config import *

pygame.font.init()
try:
    FONT = pygame.font.SysFont("Segoe UI", 16)
    TITLE_FONT = pygame.font.SysFont("Segoe UI", 20, bold=True)
except:
    FONT = pygame.font.SysFont("Arial", 16)
    TITLE_FONT = pygame.font.SysFont("Arial", 20, bold=True)

def draw_shadow_text(surface, text, font, color, x, y):
    shadow = font.render(text, True, (0, 0, 0))
    surface.blit(shadow, (x + 2, y + 2))
    main_text = font.render(text, True, color)
    surface.blit(main_text, (x, y))

class Button:
    def __init__(self, x, y, width, height, text, callback, color=EDGE_COLOR, hover_color=NODE_HOVER_COLOR, text_color=TEXT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        # Draw a slight drop shadow
        pygame.draw.rect(surface, (0,0,0,100), self.rect.move(2, 2), border_radius=8)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        # Outline
        if self.is_hovered:
            pygame.draw.rect(surface, (255,255,255), self.rect, 1, border_radius=8)
            
        text_surf = FONT.render(self.text, True, self.text_color)
        txt_rect = text_surf.get_rect(center=self.rect.center)
        draw_shadow_text(surface, self.text, FONT, self.text_color, txt_rect.x, txt_rect.y)
        
    def process_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                try:
                    import sounds
                    sounds.play("click")
                except: pass
                if self.callback:
                    self.callback()

class TextInput:
    def __init__(self, x, y, width, height, placeholder="", numeric_only=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.color_inactive = EDGE_COLOR
        self.color_active = NODE_COLOR
        self.numeric_only = numeric_only
        
    def draw(self, surface):
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=4)
        if self.text == "" and not self.active:
            text_surf = FONT.render(self.placeholder, True, (120, 120, 120))
        else:
            text_surf = FONT.render(self.text, True, TEXT_COLOR)
        # Handle overflowing text simply by clipping it using subsurface
        max_width = self.rect.width - 10
        if text_surf.get_width() > max_width:
            area = pygame.Rect(text_surf.get_width() - max_width, 0, max_width, text_surf.get_height())
            surface.blit(text_surf.subsurface(area), (self.rect.x + 5, self.rect.y + 6))
        else:
            surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 6))
        
    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if self.numeric_only and not event.unicode.isnumeric():
                    return
                self.text += event.unicode
                
    def get_text(self):
        return self.text
    
    def clear(self):
        self.text = ""

class Label:
    def __init__(self, x, y, text, color=TEXT_COLOR, is_title=False):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.is_title = is_title
        
    def draw(self, surface):
        f = TITLE_FONT if self.is_title else FONT
        draw_shadow_text(surface, self.text, f, self.color, self.x, self.y)
        
    def process_event(self, event):
        pass

class Panel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.elements = []
        
    def add_element(self, element):
        self.elements.append(element)
        
    def draw(self, surface):
        # Glassmorphism effect
        s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*PANEL_BG[:3], 215), s.get_rect(), border_radius=15)
        pygame.draw.rect(s, (*NODE_COLOR[:3], 100), s.get_rect(), 2, border_radius=15)
        surface.blit(s, self.rect)
        for el in self.elements:
            el.draw(surface)
            
    def process_event(self, event):
        # We process in reverse to handle overlapping if necessary, though it isn't here
        for el in reversed(self.elements):
            el.process_event(event)

class ScrollableList:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = [] # list of strings
        self.scroll_y = 0
        self.item_height = 25
        
    def set_items(self, items):
        self.items = items
        self.scroll_y = 0
        
    def process_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y -= event.y * 15
                max_scroll = max(0, len(self.items) * self.item_height - self.rect.height + 10)
                self.scroll_y = max(0, min(self.scroll_y, max_scroll))

    def draw(self, surface):
        pygame.draw.rect(surface, (18, 18, 24), self.rect, border_radius=4)
        
        # Create surface for clipping
        clip_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        y_offset = -self.scroll_y + 5
        for i, item in enumerate(self.items):
            if y_offset + self.item_height > 0 and y_offset < self.rect.height:
                if isinstance(item, tuple) and len(item) == 2:
                    text, color = item
                else:
                    text, color = item, TEXT_COLOR
                txt_surf = FONT.render(text, True, color)
                clip_surf.blit(txt_surf, (5, y_offset))
            y_offset += self.item_height
            
        surface.blit(clip_surf, (self.rect.x, self.rect.y))
        pygame.draw.rect(surface, EDGE_COLOR, self.rect, 1, border_radius=4)


class UIManager:
    def __init__(self):
        self.panels = []
        self.notifications = []
        
    def add_panel(self, panel):
        self.panels.append(panel)
        
    def draw(self, surface):
        for panel in self.panels:
            panel.draw(surface)
        
        y_offset = HEIGHT - 60
        new_notifications = []
        for text, timer in self.notifications:
            if timer > 0:
                alpha = min(255, timer * 5)
                surf = TITLE_FONT.render(text, True, NODE_COLOR)
                surf.set_alpha(alpha)
                # Drawing notification background
                bg_rect = surf.get_rect(center=(WIDTH // 2, y_offset))
                bg_rect.inflate_ip(20, 10)
                pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=8)
                pygame.draw.rect(surface, NODE_COLOR, bg_rect, 1, border_radius=8)
                surface.blit(surf, surf.get_rect(center=(WIDTH // 2, y_offset)))
                new_notifications.append((text, timer - 1))
                y_offset -= 45
        self.notifications = new_notifications
                
    def process_event(self, event):
        for panel in reversed(self.panels):
            panel.process_event(event)
            
    def notify(self, text, duration=150):
        self.notifications.append((text, duration))
