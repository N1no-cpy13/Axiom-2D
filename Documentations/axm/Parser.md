# 🔧 Parser.py

Converts tokens into an Abstract Syntax Tree (AST).

---

## Grammar Overview

Supports:
- **Variables:** `VAR x = 5`, assignment `x = 5`, index assign `list[0] = 5`
- **Compound assignment:** `x += 1`, `x -= 1`, `x *= 2`, `x /= 2`
- **Conditionals:** `IF cond`, `ELIF cond`, `ELSE` (indent-based, no braces)
- **Loops:** `FOR i IN 5`, `FOR item IN list`, `FOR char IN string`, `WHILE cond DO` (indent-based)
- **Loop control:** `BREAK`, `CONTINUE`
- **Functions:** `TASK name(params)`, `RETURN`, default params `b = 0`, type annotation `a: INT`
- **Deprecated:** `FUN name(params)` (still works, warns user)
- **Entity actions:** `@player MOVE 5 "RIGHT"`, `@enemy DAMAGE 10`, `@player HEAL 10`
- **I/O:** `SAY`, `SAYF` (f-strings with `{expr}`)
- **Lists:** `[1, 2, 3]`, indexing `list[0]`
- **Dicts:** `{"key": value}`, access `dict.key`, `dict["key"]`, update `dict.key = value`
- **Attribute chain:** `a.b.c` (nested attribute access)
- **Entity ref:** `@player.x` (entity attribute)
- **Method call:** `@player.damage(10)`, `obj.method(args)`
- **Unary minus/plus:** `-5`, `3 + -2`
- **Type keywords as function:** `INT("42")`, `STR(42)`, `BOOL(1)`, `LIST(1,2,3)`, `NUM("3.14")`
- **Import:** `IMPORT "path/to/module.axc"`
- **NULL:** `NULL` literal (falsy)

## Operator Precedence

1. `OR`
2. `AND`
3. `NOT`
4. Comparison (`==`, `!=`, `>`, `<`, `>=`, `<=`)
5. `+`, `-` (addition)
6. `*`, `/` (multiplication)
7. Primary (literals, variables, calls, entity refs, lists, index)

## Special Cases

- **`@entity.action`**: `@player MOVE 5 "RIGHT"` → `Move(EntityRef("player"), Number(5), String("RIGHT"))`
- **`a.b.c`**: `Attribute(Attribute(Variable("a"), "b"), "c")`
- **`a.b()`**: `MethodCall(Attribute(Variable("a"), "b"), "b", [])`
- **`INT(...)`**: `FunctionCall("INT", [...])` (type keyword as function)
- **`FUN foo()`**: no-param function (fixed)
- **`IMPORT "utils.axc"`**: `Import("utils.axc")`
- **`x += 1`**: `Assignment("x", BinaryOp(Variable("x"), "+", Number(1)))`
- **`BREAK`**: `Break()`
- **`CONTINUE`**: `Continue()`
- **`NULL`**: `Null()`
- **`FOR ... IN`**: `FOR i IN 5` → `For("i", Number(5), body)`
- **`FOR ... IN` list**: `FOR item IN [1,2,3]` → `For("item", ListLiteral([...]), body)`
- **`FOR ... IN` string**: `FOR char IN "abc"` → `For("char", String("abc"), body)`
- **`TASK`**: `TASK add(a, b)` → `FunctionDef("add", [...], body)`
- **`FUN`** (deprecated): `FUN add(a, b)` → same, warns user
- **`{"key": value}`**: `DictLiteral([(String("key"), value)])`
- **`dict.key`**: `Attribute(Variable("dict"), "key")`
- **`dict["key"]`**: `IndexAccess(Variable("dict"), String("key"))`
- **`dict.key = value`**: `Assignment(Attribute(...), value)`
- **`dict["key"] = value`**: `Assignment(IndexAccess(...), value)`

## Errors

- `ParserError`: unexpected token, missing `)`, missing indent, invalid direction