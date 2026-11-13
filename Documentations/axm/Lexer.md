# 🔤 Lexer.py

Converts AXM source code into tokens for the parser.

---

## Token Types

- **Keywords**: `SAY`, `SAYF`, `IF`, `ELSE`, `ELIF`, `FOR`, `WHILE`, `DO`, `BREAK`, `CONTINUE`, `TASK`, `RETURN`, `VAR`, `MOVE`, `DAMAGE`, `HEAL`, `SLEEP`, `IN`, `NOT`, `AND`, `OR`, `TRUE`, `FALSE`, `STR`, `INT`, `LIST`, `BOOL`, `NUM`, `IMPORT`, `NULL`, `CLASS`, `NEW`, `SELF`, `SUPER`, `EXTENDS`
- **Deprecated keywords**: `FUN` (use `TASK` instead)
- **Identifiers**: Variable/function names (letters, digits, underscore)
- **Literals**: Numbers (int/float), strings (`"..."` or `'...'`), booleans (`TRUE`/`FALSE`), null (`NULL`)
- **Directions**: `W`, `A`, `S`, `D`, `UP`, `DOWN`, `LEFT`, `RIGHT`, `TOP`, `BOTTOM`, `NORTH`, `SOUTH`, `EAST`, `WEST`, `UP_Z`, `DOWN_Z`, `ARROW_UP`, `ARROW_DOWN`, `ARROW_LEFT`, `ARROW_RIGHT`
- **Time units**: `MS` (millisecond), `SEC` (second), `MINUTE` (minute)
- **Operators**: `+`, `-`, `*`, `/`, `==`, `!=`, `>`, `<`, `>=`, `<=`
- **Compound operators**: `+=`, `-=`, `*=`, `/=`
- **Special**: `@` (entity ref), `.` (attr access), `(` `)` `[` `]` `{` `}` `,` `:` `=` (assign)
- **Control**: `NEWLINE`, `INDENT`, `DEDENT`, `EOF`

### Dict Tokens 

- `{` → `LBRACE`
- `}` → `RBRACE`
- `:` → `COLON`

### Deprecated Keywords 

`FUN` is deprecated - use `TASK` instead. Lexer will:
1. Emit `[AXIOM WARNING]` Deprecated syntax `FUN` - use `TASK` instead.`
2. Still tokenize `FUN` as `Token("FUN", "FUN")` (works)
3. Check `DEPRECATED_MODE` (config) - `warn`/`error`/`ignore`

See `Deprecation.md` for details. 

## Indentation

- Uses **2 spaces** per level (tabs **forbidden**, raises `LexerError`)
- Generates `INDENT`/`DEDENT` tokens
- Brackets `[...]` allow multi-line (no indent processing inside)

## Comments

- `//` starts a line comment (ignored, but not inside strings)

## Number Parsing

- Integers: `123`
- Floats: `1.5`
- Breaks on whitespace, brackets, and operators (`1+1` → `NUMBER(1)`, `OP(+)`, `NUMBER(1)`)

## NULL

- `NULL` → `Token("NULL", None)`
- Used as literal for null value (falsy)

## Errors

- `LexerError`: tab character, odd indent, unterminated string, invalid number