# AXC Syntax

`.axc` files use the same AXM syntax — the only difference is the
export rules.

---

## What Gets Exported

Only **global variables** and **functions** are exported:

    VAR name = "utils"          // ✅ exported
    VAR version = "1.0"         // ✅ exported

    FUN Add(a, b)               // ✅ exported
      RETURN a + b

    IF TRUE                     // ❌ not exported (block)
      VAR temp = "hidden"       // ❌ not exported (local)

    FUN Test()                  // ✅ exported
      VAR local = "secret"      // ❌ not exported (local)
      RETURN local

---

## Access Rules

**Global variable**:

    utils.version               // ✅ works
    utils.name                  // ✅ works

**Function**:

    utils.Add(1, 2)             // ✅ works

**Local variable** (inside function):

    utils.local                 // ❌ error — not exported

---

## Import Statement

    IMPORT "path/to/module.axc"

- Path relative to **current file** (for nested import)
- Path relative to **root** (for main script)
- File must exist — error if not found
- Circular import — error

---

## Nested Import

**File**: `axm/modules/advanced.axc`

    IMPORT "math.axc"           // relative to axm/modules/
    VAR name = "advanced"
    FUN CircleArea(r)
      RETURN math.PI * math.Square(r)

**File**: `main.axm`

    IMPORT "axm/modules/advanced.axc"
    SAYF "{advanced.CircleArea(2)}"

---

## Limitations

- Only `.axc` files can be imported (not `.axm`)
- No `AS` alias (module name = file name)
- No `EXPORT` keyword (all globals auto-exported)
- No `PRIVATE` (all globals accessible)