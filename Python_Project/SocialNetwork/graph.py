import random
import math
import json
from config import *

class UserNode:
    def __init__(self, user_id, name, x=None, y=None):
        self.id = user_id
        self.name = name
        self.x = x if x is not None else random.randint(300, WIDTH - 100)
        self.y = y if y is not None else random.randint(100, HEIGHT - 100)
        self.vx = 0
        self.vy = 0
        self.fx = 0
        self.fy = 0
        self.friends = set()
    
    def add_friend(self, friend_id):
        self.friends.add(friend_id)
        
    def remove_friend(self, friend_id):
        if friend_id in self.friends:
            self.friends.remove(friend_id)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "friends": list(self.friends), "x": self.x, "y": self.y}

class SocialGraph:
    def __init__(self):
        self.nodes = {} # user_id -> UserNode
        self.next_id = 1
        
    def add_user(self, name):
        user = UserNode(self.next_id, name)
        self.nodes[self.next_id] = user
        self.next_id += 1
        return user
        
    def remove_user(self, user_id):
        if user_id in self.nodes:
            user = self.nodes[user_id]
            for friend_id in list(user.friends):
                self.nodes[friend_id].remove_friend(user_id)
            del self.nodes[user_id]
            
    def add_connection(self, id1, id2):
        if id1 in self.nodes and id2 in self.nodes and id1 != id2:
            self.nodes[id1].add_friend(id2)
            self.nodes[id2].add_friend(id1)
            
    def remove_connection(self, id1, id2):
        if id1 in self.nodes and id2 in self.nodes:
            self.nodes[id1].remove_friend(id2)
            self.nodes[id2].remove_friend(id1)

    def get_node(self, user_id):
        return self.nodes.get(user_id)
        
    def clear(self):
        self.nodes.clear()
        self.next_id = 1
        
    def export_json(self, filename="graph_data.json"):
        data = [node.to_dict() for node in self.nodes.values()]
        try:
            with open(filename, 'w') as f:
                json.dump(data, f)
            return True
        except:
            return False
            
    def import_json(self, filename="graph_data.json"):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.clear()
            max_id = 0
            for item in data:
                uid = item['id']
                node = UserNode(uid, item['name'], x=item.get('x'), y=item.get('y'))
                node.friends = set(item['friends'])
                self.nodes[uid] = node
                if uid > max_id:
                    max_id = uid
            self.next_id = max_id + 1
            return True
        except Exception as e:
            print("Import failed", e)
            return False
