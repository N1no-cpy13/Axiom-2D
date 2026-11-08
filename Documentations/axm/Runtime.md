# ⚙️ Runtime.py

Executes the AST and manages program state.

---

## Key Components

- **Scope stack** - Local variables for functions/IF/WHILE/FOR (push/pop)
- **Globals** - Global variables (top-level `VAR`)
- **Functions** - User-defined functions
- **Program counter** - Current execution position (`pc`)
- **Module loader** - Load `.axc` modules (`module_loader`)

## Execution Flow

1. `load(ast)` - Load program
2. `tick()` called from main loop:
   - Loop: execute node until yield point (`MOVE`, `DAMAGE`, `HEAL`) or program end
   - Yield points only at **top-level** (nested blocks execute immediately)
3. Statements evaluated, builtins called, entities modified
4. Control flow via `ReturnSignal`, `BreakSignal`, `ContinueSignal` (marker objects, not exceptions)

## Expression Evaluation

Handles:
- Numbers, strings, booleans, null
- Variables (scope lookup with Levenshtein suggestion)
- Entity refs (`@player`)
- Attributes (`@player.health`, `a.b.c`)
- Binary ops (`+`, `-`, `*`, `/`, `==`, `!=`, `>`, `<`, `>=`, `<=`)
- Logical ops (`AND`, `OR`, `NOT`)
- Function calls (user + builtins)
- Lists, indexing
- Method calls (`@player.damage(10)`, `obj.method(args)`)
- Module attribute (`utils.version`, `math.PI`)
- Module function (`utils.Add(1, 2)`, `math.Square(5)`)

## Scope Rules

- **Top-level** → global (`self.globals`)
- **Function** → local scope (push/pop)
- **`IF`/`WHILE`/`FOR`** → local scope per block/iteration (push/pop)
- **`VAR`** → local if inside block, global if top-level
- **`Assignment`** (`x = 5`) → search scope first (inner → outer), then global
- **Module** → isolated scope (`Module.globals`, `Module.functions`)

## Loop Control

- **`BREAK`** → `BreakSignal` → exit loop
- **`CONTINUE`** → `ContinueSignal` → skip iteration, continue to next

### FOR Loop

`FOR` loop handdles multiple iterable types:

- **Integer**: `FOR i IN 5` → loop `0, 1, 2, 3, 4`
- **List**: `FOR item IN [1, 2, 3]` → loop `1, 2, 3`
- **String**: `FOR char IN "Abc"` → loop 'a', 'b', 'c'

## While Guard

- Max iterations: `MAX_WHILE_ITERATIONS` (default 10000)
- Raises `AXMRuntimeError` if exceeded (prevent infinite loop)

## Sleep (Blocking)

- `SLEEP duration unit` → `time.sleep(seconds)` (blocking)
- No yield — script pauses for specified duration

## Errors

- `AXMRuntimeError`: unknown variable/function, type mismatch, division by zero, invalid entity, etc.
- `ImportError`: circular import, module not found
- Suggestion via Levenshtein distance (`Did you mean 'x'?`)