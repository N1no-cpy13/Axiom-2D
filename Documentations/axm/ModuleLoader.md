# Module Loader

`axm/module_loader.py` — Loads `.axc` modules, handles nested imports,
circular checks, and namespaces.

---

## Classes

### ModuleLoader

Loads modules from `.axc` files.

**Methods**:

- `load(path, base_dir=None)` — Load module, return `Module` object
- `loaded_modules` — Dict `{path: Module}` (cache)
- `loading` — Set `{path}` (circular check)

**Path resolution**:

    resolved_path = os.path.join(base_dir, path) if base_dir else path

**Circular check**:

    if resolved_path in self.loading:
        raise ImportError(f"Circular import detected: {resolved_path}")

**File check**:

    if not os.path.exists(resolved_path):
        raise ImportError(f"Module not found: {resolved_path}")

**Execution**:

- Save state (`globals`, `functions`, `pc`)
- Reset state (new scope for module)
- Execute AST nodes (recursive import)
- Save module globals & functions
- Restore state

---

### Module

Module object — has `globals` & `functions`.

**Attributes**:

- `name` — Module name (from file name)
- `globals` — Dict `{var_name: value}`
- `functions` — Dict `{func_name: FunctionDef}`

**Methods**:

- `__repr__()` — `<Module name>`

---

### BoundModuleFunction

Bound function — callable from module context.

**Attributes**:

- `module` — Module object
- `name` — Function name
- `runtime` — Runtime reference

**Methods**:

- `call(args)` — Execute function in module context

**Execution**:

- Save state (`globals`, `functions`)
- Set module context
- Push scope
- Bind params
- Execute body
- Return `ReturnSignal.value`
- Restore state

---

## Flow

**Import** (`IMPORT "math.axc"`):

1. Runtime `execute_node(Import)` → `module_loader.load("math.axc")`
2. Loader resolves path → `math.axc`
3. Check circular → `math.axc` not in `loading`
4. Check cache → not in `loaded_modules`
5. Check file → exists
6. Load file → `lex` → `parse`
7. Save state → reset
8. Execute AST → for each node:
   - `Import` → recursive `load(node.path, base_dir=...)`
   - Other → `runtime.execute_node(node)`
9. Save module globals & functions
10. Restore state
11. Cache module → `loaded_modules["math.axc"] = module`
12. Return module

**Runtime** (`execute_node(Import)`):

    module = self.module_loader.load(node.path)
    module_name = node.path.replace(".axc", "").split("/")[-1].split("\\")[-1]
    self.globals[module_name] = module

**Access** (`math.PI`):

    # eval(Attribute(Variable("math"), "PI"))
    obj = self.eval(Variable("math"))  # → Module
    if isinstance(obj, Module):
        if "PI" in obj.globals:
            return obj.globals["PI"]

**Call** (`math.Add(1, 2)`):

    # eval(MethodCall(Attribute(Variable("math"), "Add"), [1, 2]))
    obj = self.eval(Attribute(Variable("math"), "Add"))  # → BoundModuleFunction
    if isinstance(obj, BoundModuleFunction):
        return obj.call([1, 2])

---

## Limitations

- Only `.axc` files can be imported
- Module name = file name (no `AS` alias)
- All globals auto-exported (no `PRIVATE`)
- No `EXPORT` keyword