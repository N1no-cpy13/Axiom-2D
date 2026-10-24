# IMPORT Statement

How to import `.axc` modules in AXM.

---

## Syntax

    IMPORT "path/to/module.axc"

---

## Path Resolution

**Main script** (`main.axm`):

    IMPORT "axm/modules/math.axc"    // relative to root
    IMPORT "utils.axc"               // relative to root

**Module** (`axm/modules/advanced.axc`):

    IMPORT "math.axc"                // relative to axm/modules/
    IMPORT "axm/modules/math.axc"    // relative to root (works too)

---

## Module Name

Module name = file name (without `.axc`):

    IMPORT "axm/modules/math.axc"    // module name: math
    IMPORT "utils.axc"               // module name: utils

Access:

    math.PI
    utils.Add(1, 2)

---

## Circular Import

**File**: `a.axc`

    IMPORT "b.axc"
    VAR a_var = "a"

**File**: `b.axc`

    IMPORT "a.axc"
    VAR b_var = "b"

**Error**:

    Circular import detected: a.axc

---

## File Not Found

    IMPORT "nonexistent.axc"

**Error**:

    Module not found: nonexistent.axc

---

## Member Not Found

    IMPORT "math.axc"
    SAYF "{math.nonexistent}"

**Error**:

    Module 'math' has no attribute 'nonexistent'

---

## Multiple Import

Same import is **cached** — not re-loaded:

    IMPORT "math.axc"
    IMPORT "math.axc"    // cached, not re-loaded