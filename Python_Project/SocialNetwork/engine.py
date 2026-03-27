from collections import deque

class RecommendationEngine:
    def __init__(self, graph):
        self.graph = graph
        
    def get_recommendations(self, user_id):
        # Recommend friends based on mutual connections
        user = self.graph.get_node(user_id)
        if not user: return []
        
        scores = {}
        for friend_id in user.friends:
            friend = self.graph.get_node(friend_id)
            if not friend: continue
            for f_of_f in friend.friends:
                if f_of_f != user_id and f_of_f not in user.friends:
                    scores[f_of_f] = scores.get(f_of_f, 0) + 1
                    
        sorted_recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs

    def bfs_traversal(self, start_id):
        # Generator for step-by-step UI updates
        if start_id not in self.graph.nodes: return
        visited = {start_id}
        queue = deque([start_id])
        
        while queue:
            curr_id = queue.popleft()
            curr = self.graph.get_node(curr_id)
            yield curr_id, queue.copy() # Yield to pause in the animator
            if not curr: continue
            for neighbor_id in curr.friends:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)

    def dfs_traversal(self, start_id):
        if start_id not in self.graph.nodes: return
        visited = set()
        stack = [start_id]
        
        while stack:
            curr_id = stack.pop()
            if curr_id not in visited:
                visited.add(curr_id)
                yield curr_id, stack.copy()
                curr = self.graph.get_node(curr_id)
                if not curr: continue
                # Reverse for standard DFS ordering
                for neighbor_id in reversed(list(curr.friends)):
                    if neighbor_id not in visited:
                        stack.append(neighbor_id)
                        
    def shortest_path(self, start_id, end_id):
        if start_id not in self.graph.nodes or end_id not in self.graph.nodes:
            return []
        visited = {start_id}
        queue = deque([(start_id, [start_id])])
        
        while queue:
            curr_id, path = queue.popleft()
            if curr_id == end_id:
                return path
            curr = self.graph.get_node(curr_id)
            if not curr: continue
            for neighbor_id in curr.friends:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        return []

    def get_communities(self):
        # Connected Components
        visited = set()
        communities = []
        for node_id in self.graph.nodes:
            if node_id not in visited:
                comp = set()
                queue = deque([node_id])
                visited.add(node_id)
                while queue:
                    curr = queue.popleft()
                    comp.add(curr)
                    for n_id in self.graph.nodes[curr].friends:
                        if n_id not in visited:
                            visited.add(n_id)
                            queue.append(n_id)
                communities.append(comp)
        return communities
