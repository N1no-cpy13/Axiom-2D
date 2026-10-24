# AXC Module System

AXC (AXIOM Class) is a module system for AXM — allows splitting code
into separate files and importing them.

---

## Overview

- Module file: `.axc` (AXIOM Class)
- Import: `IMPORT "path/to/module.axc"`
- Access: `module_name.variable`, `module_name.Function()`
- Scope: only global variables & functions are exported
- Nested import: modules can import other modules
- Circular check: prevents circular imports

---

## Quick Example

**File**: `utils.axc`

    VAR version = "1.0"
    FUN Add(a, b)
      RETURN a + b

**File**: `main.axm`

    IMPORT "utils.axc"
    SAYF "version: {utils.version}"
    SAYF "1 + 2 = {utils.Add(1, 2)}"

**Output**:

    [AXIOM] version: 1.0
    [AXIOM] 1 + 2 = 3

---

## File Structure

    project/
    ├── main.axm
    └── axm/
        └── modules/
            ├── math.axc
            ├── string.axc
            └── utils.axc

**Import**:

    IMPORT "axm/modules/math.axc"

---

## See Also

- `syntax.md` — AXC syntax
- `IMPORT.md` — How to import
- `examples.md` — Module examples