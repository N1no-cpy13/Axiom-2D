# 🏗️ Axiom 2D Architecture

## System Overview

    GAME_CONFIG.json ──► axiom.py ──┬─► engine/ (World + Entity)
                                    └─► axm/ (Lexer → Parser → AST → Runtime)
                                            └─► module_loader (IMPORT .axc)

---

## Game Loop

    while runtime.running:
        tick_start = time.time()
        
        world.tick()      # Update entities (movement, collision)
        runtime.tick()    # Execute AXM script until yield/program end
        
        elapsed = time.time() - tick_start
        sleep_time = world_tick - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

**Delta time**: tick rate consistent (~`WORLD_TICK`), independent of load.

---

## Component Breakdown

`engine/`

* **World.py:** Manages all entities, handles collisions, runs tick updates, optional bounds
* **Entity.py:** Game objects with position, health, velocity, debug flag

`axm/`

* **lexer.py:** Converts AXM source code → tokens
* **parser.py:** Converts tokens → AST
* **ast.py:** Defines AST node types
* **runtime.py:** Executes AST, manages scope, calls builtins, handles modules
* **builtins.py:** Built-in functions (SAY, MOVE, DAMAGE, LEN, INT, STR, BOOL, LIST, NUM, MIN, MAX, SPLIT, etc.)
* **signals.py:** Control flow signals (Return, Break) — marker objects, not exceptions
* **module_loader.py:** Loads `.axc` modules, handles nested import, circular check, namespaces

---

## Module System

**Files**: `.axc` (AXIOM Class) — modules for AXM scripts

**Import**:

    IMPORT "path/to/module.axc"

**Access**:

    module_name.variable        // global variable
    module_name.Function()      // function call

**Scope**: only global variables & functions are exported
**Nested import**: modules can import other modules
**Circular check**: prevents circular imports

---

## Tick & Yield

**Yield points** (`MOVE`, `DAMAGE`, `HEAL`) only work at **top-level**:
- ✅ Top-level → yield (wait for next tick)
- ❌ Inside `IF`/`WHILE`/`FOR`/function → execute immediately (no yield)

**Sleep**: blocking (`time.sleep`) — script pauses for specified duration.

---

## Scope

- **Top-level** → global (`self.globals`)
- **Function** → local scope (push/pop)
- **`IF`/`WHILE`/`FOR`** → local scope per block/iteration (push/pop)
- **`VAR`** → local if inside block, global if top-level
- **`Assignment`** (`x = 5`) → search scope first (inner → outer), then global
- **Module** → isolated scope (`Module.globals`, `Module.functions`)

---

## World Bounds

Optional via `WORLD_BOUNDS` in `GAME_CONFIG.json`:

    "WORLD_BOUNDS": {
      "min_x": 0, "max_x": 10,
      "min_y": 0, "max_y": 10
    }

- If not set → infinite world
- `MIN_Z`/`MAX_Z` optional → if not set, z-axis infinite
- Out-of-bounds entity blocked by `try_move`

---

## Example Modules

    axm/modules/
    ├── math.axc          — Math utilities (PI, Square, Sqrt, Distance, dll)
    ├── string.axc        — String utilities (Upper, Lower, Join, Replace, dll)
    ├── array.axc         — Array utilities (Sum, Average, Max, Min, Reverse, dll)
    ├── random.axc        — Random utilities (Bool, Choice, Shuffle, Dice, dll)
    ├── vector.axc        — Vector math (Vec2, Vec3, Add, Dot, Distance, dll)
    ├── color.axc         — Color utilities (RGB, Mix, Lighten, Invert, dll)
    └── validation.axc    — Validation (IsEmpty, IsNumeric, IsEmail, dll)

---

## Language Features

- **Variables**: `VAR x = 5`, assignment `x = 5`, compound `x += 1`
- **Control**: `IF`/`ELIF`/`ELSE`, `WHILE ... DO`, `FOR ... IN`, `BREAK`
- **Functions**: `FUN name(params)`, `RETURN`, default params, type annotation
- **Entity**: `@player`, attribute `@player.x`, method `@player.damage(10)`
- **List**: `[1, 2, 3]`, index `list[0]`, nested `[[1,2], [3,4]]`
- **String**: interpolation `SAYF "{x}"`, `'...'` or `"..."` quote
- **NULL**: `NULL` keyword (falsy)
- **Module**: `IMPORT "module.axc"`

---