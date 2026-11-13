# axm/runtime.py
from .builtins import Builtins
import time
from .ast import *
from .signals import Signal, ReturnSignal, BreakSignal, ContinueSignal
from .module_loader import ModuleLoader

class Instance:
    def __init__(self, class_def):
        self.class_def = class_def
        self.attrs = {}
    def __repr__(self):
        return f"<Instance of {self.class_def.name}>"

class SuperProxy:
    def __init__(self, instance, parent_class, runtime):
        self.instance = instance
        self.parent_class = parent_class
        self.runtime = runtime
    def __repr__(self):
        return f"<Super of {self.instance.class_def.name}>"

class BoundMethod:
    def __init__(self, instance, method_def, runtime):
        self.instance = instance
        self.method_def = method_def
        self.runtime = runtime
    def __call__(self, *args):
        return self.runtime._call_method(self.instance, self.method_def, list(args))

class AXMRuntimeError(Exception):
    pass

class Runtime:
    def __init__(self, world):
        self.world = world
        self.globals = {}
        self.functions = {}
        
        self.classes = {}
        
        self.running = True
        self.pc = 0
        self.program = []
        
        self.scope_stack = []
        self.module_loader = ModuleLoader(self)
                
        self.builtins = Builtins(self)

    # Basic tools
    def get_entity(self, name):
        ent = self.world.get_entity_by_name(name)
        if not ent:
            raise AXMRuntimeError(f"Entity '{name}' not found")
        return ent
    
    def axm_format_bool(self, value):
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if value is None:
            return "NULL"
        return str(value)
    
    def is_truthy(self, value):
        if isinstance(value, bool):
            return value 
        if value is None:
            return False 
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value != ""
        return True 
    
    def lookup(self, name):
        # local scope first
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        # SELF attributes
        for scope in reversed(self.scope_stack):
            if "SELF" in scope:
                instance = scope["SELF"]
                if name in instance.attrs:
                    return instance.attrs[name]
                break
        # global
        if name in self.globals:
            return self.globals[name] 
        
        # suggestion 
        all_names = self._get_all_variable_name()
        suggestion = self._closest_match(name, all_names)
        
        if suggestion:
            raise AXMRuntimeError(
                f"Unknown variable or function '{name}'. Did you mean '{suggestion}'?"
            )
        else:
            raise AXMRuntimeError(f"Unknown variable or function '{name}'")
        
    def _closest_match(self, name, candidates, maxDist=3):
        if not candidates:
            return None 
        
        # Simple cases: exact match (shouldn't happen but safety)
        if name in candidates:
            return name 
        
        best_match = None 
        best_distance = maxDist + 1 
        
        for candidate in candidates:
            distance = self._levenshtein(name, candidate)
            if distance < best_distance:
                best_distance = distance 
                best_match = candidate 
        
        return best_match if best_distance <= maxDist else None 
        
    def _levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Insert, delete, substitute 
                insertions = previous_row[j + 1] + 1 
                deletions = current_row[j] + 1 
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _get_all_variable_name(self):
        names = set()
        
        # from scope_stack
        for scope in self.scope_stack:
            names.update(scope.keys())
        
        # From globals 
        names.update(self.globals.keys())
        
        # From functions 
        names.update(self.functions.keys())
        
        # From builtins 
        for name in dir(self.builtins):
            if not name.startswith('_') and callable(getattr(self.builtins, name)):
                names.add(name)
        
        return names 
    
    def get_type_name(self, val):
        if isinstance(val, str):
            return "STR"
        elif isinstance(val, bool):
            return "BOOL"
        elif isinstance(val, int):
            return "INT"
        elif isinstance(val, float):
            return "NUM"
        elif isinstance(val, list):
            return "LIST"
        return "UNKNOWN"
    
    def is_type_match(self, expected, actual):
        if expected == actual:
            return True 
        if expected == "NUM" and actual in ("INT", "NUM"):
            return True 
        if expected == "INT" and actual == "INT":
            return True
        return False 
    
    def push_scope(self, initial=None):
        self.scope_stack.append(initial or {})
    
    def pop_scope(self):
        if self.scope_stack:
            return self.scope_stack.pop()
        return None
    
    def _resolve_class_ref(self, ref):
        if ref is None:
            return None
        if isinstance(ref, ClassDef):
            return ref
        if isinstance(ref, str):
            return self.classes.get(ref)
        if isinstance(ref, Attribute):
            obj = self.eval(ref.obj)
            from .module_loader import Module
            if isinstance(obj, Module):
                return obj.classes.get(ref.attr)
        return None
    
    def _find_method(self, class_def, name):
        cur = class_def
        while cur is not None:
            if not isinstance(cur, ClassDef):
                cur = self._resolve_class_ref(cur)
                continue
            for stmt in cur.body:
                if isinstance(stmt, FunctionDef) and stmt.name == name:
                    return stmt
            cur = cur.parent  # sudah ClassDef atau None
        return None
    
    def _call_method(self, instance, method_def, args):
        self.push_scope({})
        scope = self.current_scope()
        scope["SELF"] = instance
        scope["__CLASS__"] = getattr(method_def, 'owner_class', instance.class_def)
        # bind parameter 
        for i, param in enumerate(method_def.params):
            if i < len(args):
                scope[param.name] = args[i]
            elif param.default is not None:
                scope[param.name] = self.eval(param.default)
            else:
                self.pop_scope()
                raise AXMRuntimeError(f"Missing parameter '{param.name}' for method '{method_def.name}'")
        try:
            for stmt in method_def.body:
                result = self.execute_node(stmt)
                if isinstance(result, ReturnSignal):
                    return result.value
            return None
        finally:
            self.pop_scope()
            
    
    def current_scope(self):
        return self.scope_stack[-1] if self.scope_stack else None
    
    def load(self, ast):
        self.program = ast 
        self.pc = 0

    # =========================
    # EXPRESSION EVALUATOR
    # =========================
    def eval(self, expr):
        if isinstance(expr, Number):
            return expr.value 
        elif isinstance(expr, String):
            return expr.value 
        elif isinstance(expr, Boolean):
            return expr.value 
        elif isinstance(expr, Null):
            return None
        elif isinstance(expr, NewExpr):
            # resolve class 
            if isinstance(expr.class_name, str):
                class_def = self.classes.get(expr.class_name)
            else:
                # Attribute: module.Class
                obj = self.eval(expr.class_name.obj)
                from .module_loader import Module
                if isinstance(obj, Module):
                    class_def = obj.classes.get(expr.class_name.attr)
                else:
                    obj = self.eval(expr.class_name.obj)
                    from .module_loader import Module
                    if isinstance(obj, Module):
                        class_def = obj.classes.get(expr.class_name.attr)
                    else:
                        class_def = None
            if class_def is None:
                raise AXMRuntimeError(f"Class '{expr.class_name}' not found")
            
            instance = Instance(class_def)
            
            # deep copy default attrs from class and its parents
            import copy
            chain = []
            cur = class_def
            while cur is not None:
                if not isinstance(cur, ClassDef):
                    cur = self._resolve_class_ref(cur)
                    continue
                chain.append(cur)
                cur = cur.parent
            for cd in reversed(chain):
                for stmt in cd.body:
                    if isinstance(stmt, Var):
                        val = self.eval(stmt.value)
                        instance.attrs[stmt.name] = copy.deepcopy(val)
            
            # Call __init__ if exist
            init_method = self._find_method(class_def, "__init__")
            if init_method:
                args = [self.eval(a) for a in expr.args]
                self._call_method(instance, init_method, args)
            
            return instance
        
        elif isinstance(expr, SelfExpr):
            # SELF only valid inside method
            if not self.scope_stack:
                raise AXMRuntimeError("SELF used outside method")
            for scope in reversed(self.scope_stack):
                if "SELF" in scope:
                    return scope["SELF"]
            raise AXMRuntimeError("SELF not found in scope")
            
        elif isinstance(expr, SuperExpr):
            if not self.scope_stack:
                raise AXMRuntimeError("SUPER used outside method")
            for scope in reversed(self.scope_stack):
                if "SELF" in scope:
                    instance = scope["SELF"]
                    owner_class = scope.get("__CLASS__")
                    if owner_class is None or owner_class.parent is None:
                        raise AXMRuntimeError("SUPER used in class without parent")
                    return SuperProxy(instance, owner_class.parent, self)
            raise AXMRuntimeError("SUPER not found in scope")
            
        elif isinstance(expr, Variable):
            return self.lookup(expr.name)
            return val
                
        elif isinstance(expr, EntityRef):
            return self.get_entity(expr.name)
        
        elif isinstance(expr, Attribute):            
            obj = self.eval(expr.obj)
            attr_name = expr.attr
            
            # Dict attribute access (player.name -> player["name"])
            if isinstance(obj, dict):
                if attr_name not in obj:
                    raise AXMRuntimeError(f"Dict key '{attr_name}' not found")
                return obj[attr_name]
            
            if isinstance(obj, Instance):
                if attr_name in obj.attrs:
                    return obj.attrs[attr_name]
                # search method
                method = self._find_method(obj.class_def, attr_name)
                if method:
                    return BoundMethod(obj, method, self)
                raise AXMRuntimeError(f"Instance of '{obj.class_def.name}' has no attribute '{attr_name}'")
                
            # SuperProxy handling
            if isinstance(obj, SuperProxy):
                method = self._find_method(obj.parent_class, attr_name)
                if method:
                    return BoundMethod(obj.instance, method, self)
                raise AXMRuntimeError(f"Parent class has no attribute '{attr_name}'")
            
            # Module handling
            from .module_loader import Module, BoundModuleFunction 
            if isinstance(obj, Module):
                if attr_name in obj.globals:
                    return obj.globals[attr_name]
                if attr_name in obj.functions:
                    return BoundModuleFunction(obj, attr_name, self)
                raise AXMRuntimeError(f"Module '{obj.name}' has no attribute '{attr_name}'")
            
            # Entity handling 
            from engine.Entity import Entity 
            if not isinstance(obj, Entity):
                obj_name = getattr(expr.obj, 'name', '?')
                raise AXMRuntimeError(
                    f"'{obj_name}' is not an entity. Use @{obj_name}"
                )
            
            if not hasattr(obj, attr_name):
                raise AXMRuntimeError(
                    f"Entity '{obj.name}' has no attribute '{attr_name}'"
                )
            
            value = getattr(obj, attr_name)
            return value 
    
        elif isinstance(expr, BinaryOp):
            left = self.eval(expr.left)
            right = self.eval(expr.right)
            op = expr.op 
        
            if op == "+":
                return left + right 
            elif op == "-":
                return left - right 
            elif op == "*":
                return left * right 
            elif op == "/":
                if right == 0:
                    raise AXMRuntimeError("Division by zero")
                return left / right 
            elif op == "==":
                return left == right 
            elif op == ">":
                return left > right 
            elif op == "<":
                return left < right 
            elif op == "!=":
                return left != right 
            elif op == ">=":
                return left >= right 
            elif op == "<=":
                return left <= right
            else:
                raise AXMRuntimeError(f"Unsupported operator: {op}")
        
        elif isinstance(expr, LogicalOp):
            left = self.eval(expr.left)
            
            if expr.op == "NOT":
                # convert to bool first 
                left_bool = bool(left)
                return not left_bool
            
            right = self.eval(expr.right)
            
            # Convert to bool 
            left_bool = bool(left)
            right_bool = bool(right)
            
            if expr.op == "AND":
                return left_bool and right_bool
            elif expr.op == "OR":
                return left_bool or right_bool
            else:
                raise AXMRuntimeError(f"Unknown logical operator: {expr.op}")
             
        elif isinstance(expr, FunctionCall):
            return self.execute_node(expr)
            
        elif isinstance(expr, MethodCall):
            obj = self.eval(expr.obj)
            
            if isinstance(obj, Instance):
                method = self._find_method(obj.class_def, expr.method)
                if method is None:
                    raise AXMRuntimeError(f"Instance of '{obj.class_def.name}' has no method '{expr.method}'")
                args = [self.eval(a) for a in expr.args]
                return self._call_method(obj, method, args)
            if isinstance(obj, SuperProxy):
                method = self._find_method(obj.parent_class, expr.method)
                if method is None:
                    raise AXMRuntimeError(f"Parent class has no method '{expr.method}'")
                args = [self.eval(a) for a in expr.args]
                return self._call_method(obj.instance, method, args)
            
            # Module bound function
            from .module_loader import BoundModuleFunction
            if isinstance(obj, BoundModuleFunction):
                args = [self.eval(arg) for arg in expr.args]
                return obj.call(args)
            
            # bound method (from Attribute eval on Entity)
            if callable(obj) and not isinstance(obj, type):
                args = [self.eval(arg) for arg in expr.args]
                return obj(*args)
            
            method_name = expr.method 
            args = [self.eval(arg) for arg in expr.args]
            
            if not hasattr(obj, method_name):
                raise AXMRuntimeError(f"'{type(obj).__name__}' has no method '{method_name}'")
            
            method = getattr(obj, method_name)
            if not callable(method):
                raise AXMRuntimeError(f"'{method_name}' is not callable")
            
            return method(*args)
            
        elif isinstance(expr, ListLiteral):
            return [self.eval(e) for e in expr.elements]
        elif isinstance(expr, DictLiteral):
            result = {}
            for key_expr, value_expr in expr.pairs:
                key = self.eval(key_expr)
                value = self.eval(value_expr)
                result[key] = value 
            return result
        elif isinstance(expr, IndexAccess):
            target = self.eval(expr.target)
            index = self.eval(expr.index)
            
            # Dict indexing (any key type)
            if isinstance(target, dict):
                if index not in target:
                    raise AXMRuntimeError(f"Dict key '{index}' not found")
                
                return target[index]
            
            if not isinstance(index, int):
                raise AXMRuntimeError(f"Index must be integer, got {type(index).__name__}")
            
            # Support string indexing 
            if isinstance(target, str):
                try:
                    return target[index] 
                except IndexError:
                    raise AXMRuntimeError(f"String index {index} out of range (length {len(target)})")
           
            # Support list indexing 
            if isinstance(target, list):
                try:
                    return target[index]
                except IndexError:
                    raise AXMRuntimeError(f"List index {index} out of range (length {len(target)})")
            
            raise AXMRuntimeError(f"Cannot index type: {type(target).__name__}")
            
        else:
            raise AXMRuntimeError(f"Cannot evaluate expression: {expr}")
        

    # =========================
    # EXECUTION
    # =========================
    def execute(self, ast_nodes):
        self.program = ast_nodes
        self.pc = 0 
        self.running = True 
    
    def execute_block(self, body):
        for stmt in body:
            result = self.execute_node(stmt)
         
            if isinstance(result, Signal):
                return result 
                
        return None  
    
    def tick(self):
        if not self.running:
            return
        
        while self.running and self.pc < len(self.program):
            node = self.program[self.pc]
            
            is_yield = isinstance(node, (Move, Damage, Heal))
            
            result = self.execute_node(node)
            
            if isinstance(result, ReturnSignal):
                self.running = False 
                return 
            
            if isinstance(result, BreakSignal):
                self.pc += 1
                return 
            
            self.pc+=1
            
            if is_yield:
                return 
            
            if self.pc >= len(self.program):
                self.running = False 

    def execute_node(self, node):

        # SAY
        if isinstance(node, Say):
            value = self.eval(node.expr)
            text = self.axm_format_bool(value)
            self.builtins.SAY(text)

        # SAYF
        elif isinstance(node, SayF):
            text = ""
            for part in node.parts:
                val = self.eval(part)
                text += self.axm_format_bool(val)
            self.builtins.SAYF(text)

        # MOVE
        elif isinstance(node, Move):
            entity = self.eval(node.entity)
            
            from engine.Entity import Entity 
            if not isinstance(entity, Entity):
                raise AXMRuntimeError("MOVE target is not an entity. use @entity")
            
            amount = self.eval(node.amount)
            direction = self.eval(node.direction)
            self.builtins.MOVE(entity, amount, direction)

        # SLEEP
        elif isinstance(node, Sleep):
            duration = self.eval(node.duration)
            unit = self.eval(node.unit)
            
            if unit == "MS":
                seconds = duration / 1000
            elif unit == "SEC":
                seconds = duration 
            elif unit == "MINUTE":
                seconds = duration * 60 
            else:
                raise AXMRuntimeError(f"Invalid time unit: {unit}")
            
            if seconds > 0:
                time.sleep(seconds)
                
        # DAMAGE
        elif isinstance(node, Damage):
            entity = self.eval(node.entity)
            amount = self.eval(node.amount)
            self.builtins.DAMAGE(entity, amount)
        
        # HEAL 
        elif isinstance(node, Heal):
            entity = self.eval(node.entity)
            amount = self.eval(node.amount)
            self.builtins.HEAL(entity, amount)

        # FOR
        elif isinstance(node, For):
            iterable = self.eval(node.times)
            
            if isinstance(iterable, int):
                # FOR i IN 5 - range 0..4 
                items = range(iterable)
            elif isinstance(iterable, list):
                # FOR item IN [1, 2, 3] - iterate list 
                items = iterable
            elif isinstance(iterable, str):
                # FOR char IN "abc" - iterate string 
                items = iterable
            else:
                raise AXMRuntimeError(f"FOR loop requires int, list, or string, got {type(iterable).__name__}")
            
            self.push_scope()
            
            try:
                for item in items:
                    self.current_scope()[node.var_name] = item 
                    
                    result = self.execute_block(node.body)
                    if isinstance(result, BreakSignal):
                        break 
                    if isinstance(result, ContinueSignal):
                        continue 
                    if isinstance(result, ReturnSignal):
                        return result 
            finally:
                self.pop_scope()
                    
                    


        # VAR DECL
        elif isinstance(node, Var):
            value = self.eval(node.value)
            if self.scope_stack:
                self.current_scope()[node.name] = value 
            else:
                # Top-Level -> global 
                self.globals[node.name] = value 
        
        # Var Assignment 
        elif isinstance(node, Assignment):
            value = self.eval(node.value)
            
            # Index Assignment (list or dict)
            if isinstance(node.name, IndexAccess):
                target = self.eval(node.name.target)
                index = self.eval(node.name.index)
                
                # Dict assignment (any key type)
                if isinstance(target, dict):
                    target[index] = value 
                    return value
                
                if not isinstance(target, list):
                    raise AXMRuntimeError(f"Cannot assign to index of non-list: {type(target).__name__}")
                if not isinstance(index, int):
                    raise AXMRuntimeError(f"List index must be integer, got {type(index).__name__}")
                
                try:
                    target[index] = value 
                except IndexError:
                    raise AXMRuntimeError(f"List index {index} out of range (length {len(target)})")
                
                return value 
           
            # Dict/entity attribute assignment (obj.attr = value)
            elif isinstance(node.name, Attribute):
                obj = self.eval(node.name.obj)
                attr_name = node.name.attr 
                
                if isinstance(obj, Instance):
                    obj.attrs[attr_name] = value
                    return value
                
                # Dict attribute assignment
                if isinstance(obj, dict):
                    obj[attr_name] = value 
                    return value 
                
                # Entity attribute assignment
                from engine.Entity import Entity 
                if isinstance(obj, Entity):
                    if not hasattr(obj, attr_name):
                        raise AXMRuntimeError(f"Entity '{obj.name}' has no attribute '{attr_name}'")
                    setattr(obj, attr_name, value)
                    return value
                
                raise AXMRuntimeError(f"Cannot assign attribute to {type(obj).__name__}")
           
            # Regular assignment 
            elif isinstance(node.name, str):
                var_name = node.name
               
                found = False 
                for scope in reversed(self.scope_stack):
                    if var_name in scope:
                        scope[var_name] = value 
                        found = True 
                        break 
                        
                if not found:
                    # Check SELF
                    for scope in reversed(self.scope_stack):
                        if "SELF" in scope:
                            instance = scope["SELF"]
                            if var_name in instance.attrs:
                                instance.attrs[var_name] = value
                                found = True
                                break
               
                if not found:
                    if var_name in self.globals:
                        self.globals[var_name] = value 
                    else:
                        raise AXMRuntimeError(f"Undefined variable '{var_name}'")
               
                return value 
           
            else:
                raise AXMRuntimeError(f"Invalid assignment target: {type(node.name).__name__}")
           
        # FunctionDef
        elif isinstance(node, FunctionDef):
            # Save func def
            self.functions[node.name] = node 
        
        # FunctionCall
        elif isinstance(node, FunctionCall):
            # get func def
            funcdef = self.functions.get(node.name)
            if not funcdef:
                # Try builtins 
                builtinf = getattr(self.builtins, node.name, None)
                if builtinf and callable(builtinf):
                    arg_vals = [self.eval(arg) for arg in node.args]
                    return builtinf(*arg_vals)
                
                                # Try SELF method
                for scope in reversed(self.scope_stack):
                    if "SELF" in scope:
                        instance = scope["SELF"]
                        method = self._find_method(instance.class_def, node.name)
                        if method:
                            args = [self.eval(arg) for arg in node.args]
                            return self._call_method(instance, method, args)
                        break
                
                # Suggestion for function 
                all_names = self._get_all_variable_name()
                suggestion = self._closest_match(node.name, all_names)
                if suggestion:
                    raise AXMRuntimeError(
                        f"Function '{node.name}' not defined. Did you mean '{suggestion}'?"
                    )
                else:
                    raise AXMRuntimeError(f"Function '{node.name}' not defined")
            
            if not isinstance(funcdef, FunctionDef):
                raise AXMRuntimeError(f"'{node.name}' is not a function")
            
            # Evaluate args 
            args = [self.eval(arg) for arg in node.args]
            
            # create new scope for function 
            self.push_scope({})
            # Get the scope we just pushed 
            func_scope = self.current_scope()
            
            # Bind params with args 
            for i, param in enumerate(funcdef.params):
                if i < len(args):
                    arg_value = args[i]
                    
                    # Type checking 
                    if param.param_type:
                        expected_type = param.param_type
                        actual_type = self.get_type_name(arg_value)
                        if not self.is_type_match(expected_type, actual_type):
                            self.pop_scope()
                            raise AXMRuntimeError(
                                f"Parameter '{param.name}' expects {expected_type}, got {actual_type}"
                            )
                    
                    func_scope[param.name] = arg_value
                
                elif param.default is not None:
                    # Use default value 
                    defaultval = self.eval(param.default)
                    func_scope[param.name] = defaultval
                else:
                    self.pop_scope()
                    raise AXMRuntimeError(
                        f"Missing required parameter '{param.name}' for function '{node.name}'"
                    )
            
            # Execute function body 
            try:
                for stmt in funcdef.body:
                    result = self.execute_node(stmt)
                    if isinstance(result, ReturnSignal):
                        return result.value 
            finally:
                self.pop_scope()
            
            return None 
        
        # MethodCall
        elif isinstance(node, MethodCall):
            return self.eval(node)
                    
        elif isinstance(node, Return):
            value = self.eval(node.value) if node.value else None 
            return ReturnSignal(value)

        # BREAK
        elif isinstance(node, Break):
            return BreakSignal()
        
        # CONTINUE
        elif isinstance(node, Continue):
            return ContinueSignal()
        
        # IF
        elif isinstance(node, If):
            # IF 
            if self.is_truthy(self.eval(node.condition)):
                self.push_scope({})
                try:
                    result = self.execute_block(node.body)
                    if isinstance(result, Signal):
                        return result 
                finally:
                    self.pop_scope()
                return None
            
            # ELIF(s)
            for elif_cond, elif_body in node.elifs:
                if self.is_truthy(self.eval(elif_cond)):
                    self.push_scope({})
                    try:
                        result = self.execute_block(elif_body)
                        if isinstance(result, Signal):
                            return result 
                    finally:
                        self.pop_scope()
                    return None 
            
            # ELSE 
            if node.else_body:
                self.push_scope({})
                try:
                    result = self.execute_block(node.else_body)
                    if isinstance(result, Signal):
                        return result
                finally:
                    self.pop_scope()
        
        elif isinstance(node, Import):
            module = self.module_loader.load(node.path)
            module_name = node.path.replace(".axc", "").split("/")[-1].split("\\")[-1]
            self.globals[module_name] = module
            # Daftarkan class dari module ke runtime utama (jika belum ada)
            for cls_name, cls_def in module.classes.items():
                if cls_name not in self.classes:
                    self.classes[cls_name] = cls_def
        
        elif isinstance(node, ClassDef):
            # Resolve parent to ClassDef reference
            if node.parent is not None:
                resolved = self._resolve_class_ref(node.parent)
                if resolved is None:
                    raise AXMRuntimeError(f"Parent class '{node.parent}' not found")
                node.parent = resolved
            # Save owner_class for every method
            for stmt in node.body:
                if isinstance(stmt, FunctionDef):
                    stmt.owner_class = node
            self.classes[node.name] = node
        
        # WHILE
        elif isinstance(node, While):
            MAX_ITERATIONS = getattr(self, 'max_while_iterations', 10000)
            iteration = 0
            
            while self.is_truthy(self.eval(node.condition)):
                if iteration >= MAX_ITERATIONS:
                    raise AXMRuntimeError(
                        f"While loop exceeded {MAX_ITERATIONS} iterations (possible infinite loop). "
                        f"Check your condition or add BREAK."
                    )
                    
                self.push_scope({})
                try:
                    result = self.execute_block(node.body)
                finally:
                    self.pop_scope()

                if isinstance(result, BreakSignal):
                    break
                    
                if isinstance(result, ContinueSignal):
                    iteration += 1
                    
                    continue

                if isinstance(result, ReturnSignal):
                    return result
                
                iteration += 1

            return None
