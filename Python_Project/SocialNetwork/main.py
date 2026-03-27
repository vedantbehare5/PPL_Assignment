import pygame
pygame.init()

from config import *
from graph import SocialGraph
from engine import RecommendationEngine
from ui import UIManager, Panel, Button, TextInput, Label, ScrollableList
from animator import Animator
import sounds

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NeoSocial - Friend Recommendation Engine")
clock = pygame.time.Clock()

sounds.init_sounds()

graph = SocialGraph()
engine = RecommendationEngine(graph)
ui_manager = UIManager()
animator = Animator(graph, screen)

# UI Elements
left_panel = Panel(20, 20, 290, HEIGHT - 40)
ui_manager.add_panel(left_panel)

left_panel.add_element(Label(35, 30, "M A N A G E  U S E R S", is_title=True))

name_input = TextInput(40, 70, 250, 35, "Enter user name")
left_panel.add_element(name_input)
def add_user_cmd():
    name = name_input.get_text()
    if name:
        u = graph.add_user(name)
        ui_manager.notify(f"User {u.name} (ID: {u.id}) joined the network!")
        name_input.clear()
left_panel.add_element(Button(40, 115, 250, 35, "Add User", add_user_cmd))

# Connections
id1_input = TextInput(40, 170, 120, 35, "User 1 ID", numeric_only=True)
id2_input = TextInput(170, 170, 120, 35, "User 2 ID", numeric_only=True)
left_panel.add_element(id1_input)
left_panel.add_element(id2_input)

def connect_cmd():
    try:
        id1 = int(id1_input.get_text())
        id2 = int(id2_input.get_text())
        if graph.get_node(id1) and graph.get_node(id2):
            if id1 != id2:
                graph.add_connection(id1, id2)
                ui_manager.notify(f"Connected {id1} and {id2}!")
                sounds.play("connect")
                id1_input.clear()
                id2_input.clear()
        else:
            ui_manager.notify("Invalid IDs!", 100)
    except: ...
left_panel.add_element(Button(40, 215, 250, 35, "Add Connection", connect_cmd))

# Engine Controls
left_panel.add_element(Label(35, 270, "E N G I N E", is_title=True))
target_node_input = TextInput(40, 310, 250, 35, "Target Node ID", numeric_only=True)
left_panel.add_element(target_node_input)

rec_list = ScrollableList(40, 480, 250, 200)
left_panel.add_element(rec_list)

def show_recommendations():
    try:
        tid = int(target_node_input.get_text())
        if not graph.get_node(tid): return
        recs = engine.get_recommendations(tid)
        out = []
        for rec_id, count in recs:
            name = graph.get_node(rec_id).name
            out.append((f"{name} ({count} mutuals)", RECOMMEND_COLOR))
        if out:
            ui_manager.notify(f"Found {len(out)} recommendations")
            sounds.play("recommend")
            rec_list.set_items(out)
            # Highlight nodes
            animator.highlighted_nodes = {r[0] for r in recs}
            animator.highlighted_nodes.add(tid)
        else:
            ui_manager.notify("No recommendations available.")
            rec_list.set_items([])
            animator.highlighted_nodes = {tid}
    except: ...

left_panel.add_element(Button(40, 355, 250, 35, "Recommend Friends", show_recommendations, hover_color=RECOMMEND_COLOR, text_color=(0,0,0)))

active_generator = None
anim_timer = 0
ANIM_DELAY = 12 # frames between steps

def start_bfs():
    global active_generator
    try:
        tid = int(target_node_input.get_text())
        active_generator = engine.bfs_traversal(tid)
        ui_manager.notify(f"Starting BFS from {tid}...")
        animator.highlighted_nodes.clear()
        animator.highlighted_edges.clear()
    except: ...
        
def start_dfs():
    global active_generator
    try:
        tid = int(target_node_input.get_text())
        active_generator = engine.dfs_traversal(tid)
        ui_manager.notify(f"Starting DFS from {tid}...")
        animator.highlighted_nodes.clear()
        animator.highlighted_edges.clear()
    except: ...

left_panel.add_element(Button(40, 400, 120, 35, "Run BFS", start_bfs, hover_color=TRAVERSAL_COLOR, text_color=(0,0,0)))
left_panel.add_element(Button(170, 400, 120, 35, "Run DFS", start_dfs, hover_color=TRAVERSAL_COLOR, text_color=(0,0,0)))

# Graph ops
def generate_random():
    graph.clear()
    for i in range(15):
        graph.add_user(f"User_{i+1}")
    import random
    nodes = list(graph.nodes.keys())
    for _ in range(20):
        a,b = random.sample(nodes, 2)
        graph.add_connection(a,b)
    ui_manager.notify("Random Graph Generated")
        
left_panel.add_element(Button(40, HEIGHT - 130, 120, 35, "Randomize", generate_random, hover_color=(0, 200, 100)))

def clear_all():
    graph.clear()
    animator.highlighted_nodes.clear()
    animator.highlighted_edges.clear()
    rec_list.set_items([])
left_panel.add_element(Button(170, HEIGHT - 130, 120, 35, "Clear Graph", clear_all, hover_color=(255, 50, 50)))

def save_graph():
    if graph.export_json():
        ui_manager.notify("Graph exported to graph_data.json")
left_panel.add_element(Button(40, HEIGHT - 80, 120, 35, "Save Graph", save_graph))

def load_graph():
    if graph.import_json():
        ui_manager.notify("Graph loaded from graph_data.json")
left_panel.add_element(Button(170, HEIGHT - 80, 120, 35, "Load Graph", load_graph))

generate_random()

running = True
while running:
    screen.fill(BG_COLOR)
    
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False
        ui_manager.process_event(e)
        
        # Node interaction
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if e.pos[0] > 320: # not in panel
                for p in graph.nodes.values():
                    import math
                    if math.hypot(p.x - e.pos[0], p.y - e.pos[1]) < NODE_RADIUS:
                        animator.selected_node = p
                        break
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            animator.selected_node = None
        elif e.type == pygame.MOUSEMOTION:
            if animator.selected_node:
                animator.selected_node.x = e.pos[0]
                animator.selected_node.y = e.pos[1]
                animator.selected_node.vx = 0
                animator.selected_node.vy = 0

    if active_generator:
        anim_timer += 1
        if anim_timer >= ANIM_DELAY:
            anim_timer = 0
            try:
                curr_id, queue_or_stack = next(active_generator)
                animator.highlighted_nodes = set(queue_or_stack)
                animator.highlighted_nodes.add(curr_id)
                ui_manager.notify(f"Traversing node {curr_id}", 30)
            except StopIteration:
                active_generator = None
                animator.highlighted_nodes.clear()
                ui_manager.notify("Traversal Complete!")

    animator.update_physics()
    animator.draw()
    ui_manager.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
