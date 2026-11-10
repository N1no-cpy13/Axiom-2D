# engine/Entity.py

class Entity:
    _NEXT_ID = 1
    
    def __init__(self, name, role, health, x, y, z=0):
        self.id = Entity._NEXT_ID
        Entity._NEXT_ID += 1
        
        self.name = name
        self.role = role 
        self.health = int(health)
        self.max_health = int(health)  # NEW
        
        self.tags = []  # NEW
        
        # entity velocity 
        self.vx = 0 
        self.vy = 0 
        self.vz = 0
        
        self._last_move = None
        self._position = [x, y, z]
    
    @property 
    def position(self):
        return tuple(self._position)
    
    @position.setter 
    def position(self, value):
        if len(value) not in (2, 3):
            raise ValueError("position must be (x, y) or (x, y, z)")
        x, y = value[0], value[1]
        z = value[2] if len(value) == 3 else 0 
        self._position = [x, y, z]
    
    # axis shortcuts 
    @property
    def x(self): return self._position[0]
    
    @property
    def y(self): return self._position[1]
    
    @property
    def z(self): return self._position[2]
    
    # AXM method
    @property 
    def IsDead(self):
        return self.health <= 0
    @property 
    def IsAlive(self):
        return self.health > 0     
    
    # tick update 
    def update(self, world):
        if self.IsDead:
            return 
        
        if self.vx or self.vy or self.vz:
            if getattr(world, 'debug', False):
                print(f"[TICK] {self.name} moving with v=({self.vx},{self.vy},{self.vz}) from ({self.x},{self.y},{self.z})")
            success, blocker = world.try_move(self, self.vx, self.vy, self.vz)
            
            if success:
                if getattr(world, 'debug', False):
                    print(f"[TICK] {self.name} moved to ({self.x},{self.y},{self.z})")
            else:
                if getattr(world, 'debug', False):
                    print(f"[TICK] {self.name} collision with {blocker.name if blocker else '?'}")
            
            # reset velocity (always)
            self.vx = self.vy = self.vz = 0
    
    # actions
    def _move_by(self, dx, dy, dz=0):
        self._position[0] += dx 
        self._position[1] += dy
        self._position[2] += dz 
    
    def damage(self, amount):
        self.health = max(0, self.health - int(amount))
    
    # NEW: heal
    def heal(self, amount):
        self.health = min(self.max_health, self.health + int(amount))
        return self.health
    
    # NEW: distance to other entity
    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return (dx*dx + dy*dy + dz*dz) ** 0.5
    
    # NEW: distance to position
    def distance_to_pos(self, x, y, z=0):
        dx = self.x - x
        dy = self.y - y
        dz = self.z - z
        return (dx*dx + dy*dy + dz*dz) ** 0.5
    
    # NEW: direction to other (normalized)
    def direction_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        length = (dx*dx + dy*dy + dz*dz) ** 0.5
        if length == 0:
            return (0, 0, 0)
        return (dx/length, dy/length, dz/length)
    
    # NEW: teleport
    def teleport(self, x, y, z=0):
        self._position = [x, y, z]
        self.vx = self.vy = self.vz = 0
    
    # NEW: clone
    def clone(self):
        new = Entity(self.name + "_copy", self.role, self.health, self.x, self.y, self.z)
        new.max_health = self.max_health
        new.tags = list(self.tags)
        return new
    
    # NEW: serialize
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "health": self.health,
            "max_health": self.max_health,
            "position": list(self.position),
            "tags": list(self.tags),
        }
    
    def __repr__(self):
        return f"Entity(id={self.id}, name='{self.name}', role='{self.role}', hp={self.health}/{self.max_health}, pos={self.position})"