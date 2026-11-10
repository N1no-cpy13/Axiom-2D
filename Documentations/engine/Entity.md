
# 🧩 Entity.py

Represents all objects in the game world.

---

## Properties

- `id` - Unique identifier (auto-increment via `_NEXT_ID`)
- `name`, `role` - Entity identity
- `health` - Hit points
- `max_health` - Maximum HP (heal cap)
- `tags` - List of tags (for filtering)
- `position` - `(x, y, z)` tuple (getter/setter, supports 2D or 3D)
- `x`, `y`, `z` - Position shortcuts (read-only)
- `vx`, `vy`, `vz` - Velocity (applied on next tick)
- `IsDead` / `IsAlive` - Status checks (property)
- `_last_move` - Last move info (`{"direction": str, "steps": int}`)

## Key Methods

- `update(world)` - Called each tick, moves entity based on velocity (debug print if `world.debug`)
- `damage(amount)` - Reduce health (clamped to 0)
- `heal(amount)` - Increase health (capped at `max_health`), returns new health
- `_move_by(dx, dy, dz)` - Internal position change (no collision check)
- `distance_to(other)` - Distance to another entity
- `distance_to_pos(x, y, z)` - Distance to a position
- `direction_to(other)` - Normalized direction vector to another entity
- `teleport(x, y, z)` - Instantly move to position (reset velocity)
- `clone()` - Create a copy of the entity
- `to_dict()` - Serialize entity to dict

## Example

```python
entity = Entity("player", "ENTITY", 100, 0, 0, 0)
entity.vx = 5
# next tick: entity.update(world) -> try_move -> position updated

entity.damage(10)  # health: 100 -> 90
entity.heal(20)    # health: 90 -> 100 (capped)

print(entity.to_dict())
# {'id': 1, 'name': 'player', 'role': 'ENTITY', 'health': 100, 'max_health': 100, 'position': [0, 0, 0], 'tags': []}
```