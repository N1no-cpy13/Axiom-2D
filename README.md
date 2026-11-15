Oke, ini `README.md` yang sudah dimodifikasi dengan tambahan `SWITCH/CASE/DEFAULT` dan beberapa perbaikan.

```markdown
# Axiom-2D
# Tick-Based Game Engine

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow)

**Axiom 2D** is a lightweight tick-based game engine written in Python, featuring a custom scripting language called **AXM**. The engine separates game logic (Python core) from gameplay scripting (AXM) for maximum flexibility.

> **Core Concept**: World ticks → Entities move → AXM scripts react

---

## Quick Features

- **3D World Space** (x, y, z coordinates) with 2D gameplay
- **Tick-based Loop** - Configurable interval (default 0.01s)
- **Entity System** - Health, position, velocity, collision, tags, teleport, heal
- **World Queries** - Find by role, tag, radius, nearest
- **AXM Scripting Language** - Custom syntax with lexer, parser, runtime
- **Object-Oriented** - `CLASS`, `NEW`, `SELF`, `SUPER`, inheritance, method override
- **Control Flow** - `IF/ELIF/ELSE`, `WHILE`, `FOR`, `SWITCH/CASE/DEFAULT`
- **AXC Module System** - Import `.axc` modules, namespaces, nested imports
- **Dict, List, NULL** - `{"key": value}`, `[1, 2, 3]`, `NULL` keyword
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

## Object-Oriented Programming

AXM supports classes, inheritance, and method overriding.

```axm
CLASS Animal
  VAR name = "Animal"
  VAR sound = "..."
  
  TASK __init__(name)
    SELF.name = name
  
  TASK speak()
    RETURN name + " says " + sound

CLASS Dog EXTENDS Animal
  TASK __init__(name)
    SUPER().__init__(name)
    SELF.sound = "Woof"
  
  TASK speak()
    RETURN "Dog: " + SUPER().speak()

VAR d = NEW Dog("Rex")
SAYF "d.speak(): {d.speak()}"
# Output: Dog: Rex says Woof
```

**Features:**
- `CLASS` declaration with `VAR` (attributes) and `TASK` (methods)
- `NEW` to instantiate
- `SELF` for instance reference
- `SUPER()` for parent method/constructor access
- Single inheritance with `EXTENDS`
- Method overriding
- Deep copy of default attributes
- Dynamic attribute access (`instance[key]`)
- `to_string()` automatically called on `SAY instance`

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

**Features:**

- Access: `module_name.variable`, `module_name.Function()`, `module_name.ClassName`
- Circular check: prevents circular imports
- Class in module: `NEW module.ClassName(...)`
- Inheritance from module: `CLASS Child EXTENDS module.Parent`

---

## Dict & List

**Dict** — key-value storage:

```axm
VAR d1 = {"a": 1}
VAR d2 = {"b": 2}
SAY HAS_KEY(d1, "a")               // TRUE
SAY GET_KEY(d1, "z", 0)            // 0
SAY SET_KEY(d1, "c", 3)
SAY DELETE_KEY(d1, "a")
SAY KEYS(d1)                       // ['c']
SAY VALUES(d1)                     // [3]
VAR merged = MERGE(d1, d2)
SAY CLEAR(d1)
```

---

## Switch / Case

```axm
VAR x = 2

SWITCH x
  CASE 1
    SAY "one"
  CASE 2
    SAY "two"
  CASE 3
    SAY "three"
  DEFAULT
    SAY "other"

// Output: two
```

**Notes:**
- Each `CASE` auto-break (no fall-through).
- `DEFAULT` optional.
- `CASE` can use expressions: `CASE score >= 90`.
- Nested `SWITCH` supported.

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
├── vector.axc        — Vector math (Vec2, Vec3, Add, Dot, Distance, dll)
├── color.axc         — Color utilities (RGB, Mix, Lighten, Invert, ToHex, dll)
├── validation.axc    — Validation (IsEmpty, IsNumeric, IsEmail, dll)
├── colorama.axc      — ANSI color for terminal
├── inventory.axc     — Inventory & item management
└── timer.axc         — Timer, Cooldown, Stopwatch
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

## 🐛 Recent Changes (v1.0.0)

### 🚀 New Features

- **`SWITCH`/`CASE`/`DEFAULT`**: auto-break, expressions in case, nested switch
- **Object-Oriented Programming**: `CLASS`, `NEW`, `SELF`, `SUPER`, inheritance, method override
- **Dynamic attribute access**: `instance[key]` for get/set
- **`to_string()`** automatically called on `SAY instance`
- **Instance as dict key**
- **`NEW` multi-line arguments**

---

### 🐛 Bug Fixes

- **`CLASS`**: fix `SUPER()` resolution (owner class, not instance class)
- **Module**: fix class registration in `.axc` modules
- **`LEN`**: support `dict`
- **Lexer**: bracket for parentheses (multi-line function/new args)

---

**License**

This project is licensed under the `MIT License` - see the `LICENSE` file.