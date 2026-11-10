# engine/World.py

from .Entity import Entity


class World:
    def __init__(self, name="UnnamedWorld"):
        self.world_name = name
        self.entities = {}
        self.entity_names = {}
        self.bounds = None
        self.debug = False
    
    def add_entity(self, name, role, health, x, y, z=0):
        if name in self.entity_names:
            old = self.entity_names[name]
            self.remove_entity(old.id)
        
        entity = Entity(name, role, health, x, y, z)
        self.entities[entity.id] = entity 
        self.entity_names[entity.name] = entity 
        return entity 
    
    def remove_entity(self, entity_id):
        ent = self.entities.pop(entity_id, None)
        if ent:
            self.entity_names.pop(ent.name, None)
    
    def cleanup_dead_entities(self):
        dead_ids = []
        for entity_id, entity in self.entities.items():
            if entity.IsDead:
                dead_ids.append(entity_id)
        
        for entity_id in dead_ids:
            self.remove_entity(entity_id)
        
        return len(dead_ids)
    
    def get_entity(self, entity_id):
        return self.entities.get(entity_id)
    
    def get_entity_by_name(self, name):
        return self.entity_names.get(name)
    
    def get_entities(self):
        return list(self.entities.values())
    
    # NEW: get entities by role
    def get_entities_by_role(self, role):
        return [e for e in self.entities.values() if e.role == role]
    
    # NEW: find entities by tag
    def find_by_tag(self, tag):
        return [e for e in self.entities.values() if tag in e.tags]
    
    # NEW: get entities in radius
    def get_entities_in_radius(self, x, y, r):
        result = []
        r2 = r * r
        for e in self.entities.values():
            dx = e.x - x
            dy = e.y - y
            if dx*dx + dy*dy <= r2:
                result.append(e)
        return result
    
    # NEW: get nearest entity
    def get_nearest_entity(self, x, y):
        best = None
        best_dist = float("inf")
        for e in self.entities.values():
            dx = e.x - x
            dy = e.y - y
            d = dx*dx + dy*dy
            if d < best_dist:
                best_dist = d
                best = e
        return best
    
    # NEW: count by role
    def count_by_role(self, role):
        return sum(1 for e in self.entities.values() if e.role == role)
    
    # NEW: clear all entities
    def clear_entities(self):
        self.entities.clear()
        self.entity_names.clear()
    
    # NEW: get world size (number of entities)
    def size(self):
        return len(self.entities)
    
    # game tick 
    def tick(self):
        for entity in list(self.entities.values()):
            entity.update(self)
        self.cleanup_dead_entities()
    
    def is_adjacent(self, e1, e2):
        x1, y1, z1 = e1.position 
        x2, y2, z2 = e2.position 
        return abs(x1 - x2) + abs(y1 - y2) == 1 and z1 == z2 
        
    def _in_bounds(self, pos):
        if self.bounds is None:
            return True 
        
        x, y, z = pos 
        
        min_x = self.bounds.get("min_x", float("-inf")) 
        max_x = self.bounds.get("max_x", float("inf"))
        min_y = self.bounds.get("min_y", float("-inf"))
        max_y = self.bounds.get("max_y", float("inf"))
        min_z = self.bounds.get("min_z", float("-inf"))
        max_z = self.bounds.get("max_z", float("inf"))
        
        return (min_x <= x <= max_x and 
                min_y <= y <= max_y and 
                min_z <= z <= max_z)
    
    def try_move(self, entity, dx, dy, dz=0):
        ex, ey, ez = entity.position
        
        # Determine step dir (normalize)
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        step_z = 0 if dz == 0 else (1 if dz > 0 else -1)
        
        steps = max(abs(dx), abs(dy), abs(dz))
        
        # Move step by step, stop if blocked
        blocker = None 
        moved = 0
        
        for s in range(steps):
            next_x = ex + step_x
            next_y = ey + step_y
            next_z = ez + step_z
            target = (next_x, next_y, next_z)
            
            # Check bounds 
            if self.bounds is not None and not self._in_bounds(target):
                blocker = None
                break 
            
            # Check collision 
            blocked = False 
            for other in self.entities.values():
                if other is entity:
                    continue 
                if other.position == target:
                    blocked = True 
                    blocker = other 
                    break 
            
            if blocked:
                break 
            
            # Move one step 
            ex, ey, ez = next_x, next_y, next_z
            moved += 1
        
        # Apply final position         
        if moved > 0:
            entity._position = [ex, ey, ez]
        
        return moved > 0, blocker
    
    def __repr__(self):
        return f"World(name='{self.world_name}', entities={len(self.entities)}, bounds={self.bounds})"