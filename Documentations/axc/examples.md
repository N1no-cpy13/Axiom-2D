# AXC Examples

Example `.axc` modules you can use.

---

## Math Module

**File**: `axm/modules/math.axc`

    VAR PI = 3.14159
    VAR E = 2.71828

    FUN Square(x)
      RETURN x * x

    FUN CircleArea(r)
      RETURN PI * r * r

    FUN Distance2D(x1, y1, x2, y2)
      VAR dx = x2 - x1
      VAR dy = y2 - y1
      RETURN SQRT(dx * dx + dy * dy)

**Usage**:

    IMPORT "axm/modules/math.axc"
    SAYF "PI = {math.PI}"
    SAYF "Square(5) = {math.Square(5)}"
    SAYF "CircleArea(2) = {math.CircleArea(2)}"

---

## String Module

**File**: `axm/modules/string.axc`

    FUN Join(lst, sep)
      VAR result = ""
      FOR i IN LEN(lst)
        IF i > 0
          result = result + sep
        result = result + lst[i]
      RETURN result

    FUN Repeat(s, n)
      VAR result = ""
      FOR i IN n
        result = result + s
      RETURN result

**Usage**:

    IMPORT "axm/modules/string.axc"
    SAYF "{string.Join(["a", "b", "c"], ", ")}"
    SAYF "{string.Repeat("ha", 3)}"

---

## Utils Module

**File**: `axm/modules/utils.axc`

    VAR VERSION = "1.0.0"

    FUN Clamp(value, minv, maxv)
      IF value < minv
        RETURN minv
      IF value > maxv
        RETURN maxv
      RETURN value

    FUN Lerp(a, b, t)
      RETURN a + (b - a) * t

**Usage**:

    IMPORT "axm/modules/utils.axc"
    SAYF "version: {utils.VERSION}"
    SAYF "Clamp(15, 0, 10) = {utils.Clamp(15, 0, 10)}"
    SAYF "Lerp(0, 100, 0.5) = {utils.Lerp(0, 100, 0.5)}"

---

## Nested Import

**File**: `axm/modules/game.axc`

    IMPORT "math.axc"
    IMPORT "utils.axc"

    FUN SpawnPosition(angle, radius)
      VAR x = math.CircleArea(radius)
      VAR y = utils.Lerp(0, 100, 0.5)
      RETURN x + y

**Usage**:

    IMPORT "axm/modules/game.axc"
    SAYF "{game.SpawnPosition(45, 10)}"