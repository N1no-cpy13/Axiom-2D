
# Axiom-2D
# Tick-Based Game Engine

![Version](https://img.shields.io/badge/version-0.5.0--alpha-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow)

**Axiom 2D** is a lightweight tick-based game engine written in Python, featuring a custom scripting language called **AXM**. The engine separates game logic (Python core) from gameplay scripting (AXM) for maximum flexibility.

> **Core Concept**: World ticks → Entities move → AXM scripts react

---

## Quick Features

- **3D World Space** (x, y, z coordinates) with 2D gameplay
- **Tick-based Loop** - Configurable interval (default 0.01s)
- **Entity System** - Health, position, velocity, collision
- **AXM Scripting Language** - Custom syntax with lexer, parser, runtime
- **AXC Module System** - Import `.axc` modules, namespaces, nested imports
- **Dict & List** - `{"key": value}`, `[1, 2, 3]`, nested, chained
- **Deprecation System** - Warn user about old syntax (configurable)
- **JSON Configuration** - Easy world setup
- **No Dependencies** - Pure Python standard library

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/N1no-cpy13/Axiom-2D.git
cd Axiom-2D

# Run with default configuration
python axiom.py
```

## Hello World in AXM
Create a file `hello.axm`:

```axm
SAY "Hello, Axiom 2D!"
```

Edit `GAME_CONFIG.json`:

```json
{
  "WORLD_NAME": "MyWorld",
  "WORLD_TICK": 0.01,
  "AXM_FILE_TO_RUN": "hello.axm",
  "DEBUG": false,
  "WORLD_ENTITY": {}
}
```

Run:

```bash
python axiom.py
# Output: [AXIOM] Hello, Axiom 2D!
```

---

## Module System (AXC)

**AXC** (AXIOM Class) — module system for AXM.

**File**: `utils.axc`

```axm
VAR version = "1.0"
TASK Add(a, b)
  RETURN a + b
```

**File**: `main.axm`

```axm
IMPORT "utils.axc"
SAYF "version: {utils.version}"
SAYF "1 + 2 = {utils.Add(1, 2)}"
```

**Output**:

```
[AXIOM] version: 1.0
[AXIOM] 1 + 2 = 3
```

**Features**:

- Import: `IMPORT "path/to/module.axc"`
- Access: `module_name.variable`, `module_name.Function()`
- Scope: only global variables & functions exported
- Nested import: modules can import other modules
- Circular check: prevents circular imports

---

## Dict & List

**Dict** — key-value storage:

```axm
VAR player = {"name": "Bro", "health": 100, "level": 5}

SAYF "{player.name}"           // Bro
SAYF "{player['health']}"      // 100
player.health = 90
player['gold'] = 50

// Nested
VAR config = {"player": {"name": "Bro"}}
SAYF "{config.player.name}"    // Bro

// Dict functions
HAS_KEY(player, "gold")        // TRUE
GET_KEY(player, "exp", 0)      // 0
SET_KEY(player, "atk", 15)
DELETE_KEY(player, "level")
KEYS(player)                   // ['name', 'health', 'gold', 'atk']
VALUES(player)                 // ['Bro', 90, 50, 15]
MERGE(dict1, dict2)
CLEAR(dict)
```

**List** — ordered collection:

```axm
VAR items = [1, 2, 3, 4, 5]
SAYF "{items[0]}"              // 1
SAYF "{LEN(items)}"            // 5
APPEND(items, 6)
SAYF "{items}"                 // [1, 2, 3, 4, 5, 6]
```

---

## Deprecation System

Deprecated syntax still works, but warns user.

**Config** (`GAME_CONFIG.json`):

```json
"DEPRECATION_MODE": "warn"
```

| Mode | Behavior |
|------|----------|
| `"warn"` | Print warning, continue (default) |
| `"error"` | Raise `SyntaxError`, stop script |
| `"ignore"` | No warning, continue |

**Deprecated**:

- `FUN` → **use `TASK`** (still works, warns user)

**Example**:

```axm
// Deprecated (warns)
FUN add(a, b)
  RETURN a + b

// New (no warning)
TASK add(a, b)
  RETURN a + b
```

---

## Example Modules

```
axm/modules/
├── math.axc          — Math utilities (PI, Square, Sqrt, Distance, dll)
├── string.axc        — String utilities (Upper, Lower, Join, Replace, dll)
├── array.axc         — Array utilities (Sum, Average, Max, Min, Reverse, dll)
├── random.axc        — Random utilities (Bool, Choice, Shuffle, Dice, dll)
├── vector.axc        — Vector math (Add, Dot, Distance, Rotate2D, dll)
├── color.axc         — Color utilities (RGB, Mix, Lighten, Invert, ToHex, dll)
└── validation.axc    — Validation (IsEmpty, IsNumeric, IsEmail, dll)
```

**Usage**:

```axm
IMPORT "axm/modules/math.axc"
SAYF "PI = {math.PI}"
SAYF "Square(5) = {math.Square(5)}"
```

---

## Documentation
For detailed documentation, see the `Documentations` folder:

```text
Documentations/
├── ARCHITECTURE.md
├── engine/
│   ├── Entity.md
│   └── World.md
├── axm/
│   ├── Builtins.md
│   ├── Parser.md
│   ├── runtime.md
│   ├── Lexer.md
│   ├── Signals.md
│   ├── ModuleLoader.md
│   └── Deprecation.md
├── axc/
│   ├── README.md
│   ├── syntax.md
│   ├── IMPORT.md
│   └── examples.md
├── Usage Guide/
│   ├── started.md
│   └── axm_syntax.md
└── testsuite/
    ├── basic.axm
    ├── entities.axm
    ├── functions.axm
    ├── if_else.axm
    ├── lists.axm
    └── while.axm
```

---

## Configuration
Edit `GAME_CONFIG.json`:

```json
{
  "WORLD_NAME": "TestWorld",
  "WORLD_TICK": 0.01,
  "AXM_FILE_TO_RUN": "test1.axm",
  "DEBUG": true,
  "MAX_WHILE_ITERATIONS": 10000,
  "DEPRECATION_MODE": "warn",
  "WORLD_BOUNDS": {
    "min_x": 0,
    "max_x": 10,
    "min_y": 0,
    "max_y": 10
  },
  "WORLD_ENTITY": {
    "player": {
      "ROLE": "ENTITY",
      "HEALTH": 100,
      "X": 0,
      "Y": 0
    },
    "enemy": {
      "ROLE": "ENTITY",
      "HEALTH": 100,
      "X": 5,
      "Y": 0
    }
  }
}
```

**Notes**:

- `WORLD_BOUNDS` **optional** — if not set, world is infinite
- `MIN_Z`/`MAX_Z` **optional** — if not set, z-axis is infinite
- `MAX_WHILE_ITERATIONS` **optional** — default 10000 (prevent infinite loop)
- `DEBUG` **optional** — default false (print `[TICK]` logs if true)
- `DEPRECATION_MODE` **optional** — default `"warn"` (`"warn"`, `"error"`, `"ignore"`)

---

## 🐛 Recent Changes (v0.5.0-alpha)

### 🚀 New Features

- **`DICT`**: `{"key": value}`, dot/bracket access, nested, chained
- **8 dict functions**: `HAS_KEY`, `GET_KEY`, `SET_KEY`, `DELETE_KEY`, `KEYS`, `VALUES`, `MERGE`, `CLEAR`

### 🐛 Bug Fixes

- `math.axc`: `Power` use `POW()` instead of `**`

---

**License**

This project is licensed under the `MIT License` - see the `LICENSE` file.