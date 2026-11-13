# axm/module_loader.py 

import os
from .lexer import lex 
from .parser import parse 
from .ast import Import 
from .signals import ReturnSignal

class ModuleLoader:
    def __init__(self, runtime):
        self.runtime = runtime 
        self.loaded_modules = {}  # {path: Module}
        self.loading = set()      # circular check
    
    def load(self, path, base_dir=None):
        # Resolve relative path to base_dir 
        if base_dir and not os.path.isabs(path):
            resolved_path = os.path.join(base_dir, path)
        else:
            resolved_path = path 
        
        # Check circular 
        if resolved_path in self.loading:
            raise ImportError(f"Circular import detected: {resolved_path}")
        
        # Check already loaded
        if resolved_path in self.loaded_modules:
            return self.loaded_modules[resolved_path]
        
        # Check file exist 
        if not os.path.exists(resolved_path):
            raise ImportError(f"Module not found: {resolved_path}")
        
        # Load file 
        with open(resolved_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Parse 
        tokens = lex(code)
        ast = parse(tokens)
        
        # Execute in new scope
        module_name = os.path.splitext(os.path.basename(resolved_path))[0]
        module = Module(module_name)
                
        # Save runtime state
        old_globals = self.runtime.globals 
        old_functions = self.runtime.functions 
        old_classes = self.runtime.classes
        old_pc = self.runtime.pc 
        
        # Reset runtime state for module execution
        self.runtime.globals = {}
        self.runtime.functions = {}
        self.runtime.classes = {}
        
        # Mark loading (circular check)
        self.loading.add(resolved_path)
        
        try:
            # Execute all nodes in module
            for node in ast:
                if isinstance(node, Import):
                    # Recursive import (relative to module directory)
                    self.load(node.path, base_dir=os.path.dirname(resolved_path))
                else:
                    self.runtime.execute_node(node)
            
            # Save module's globals, functions, classes
            module.globals = self.runtime.globals.copy()
            module.functions = self.runtime.functions.copy()
            module.classes = dict(self.runtime.classes)
            
        finally:
            # Restore runtime state
            self.runtime.globals = old_globals 
            self.runtime.functions = old_functions
            self.runtime.classes = old_classes
            self.runtime.pc = old_pc 
            self.loading.discard(resolved_path)
        
        # Cache module
        self.loaded_modules[resolved_path] = module 
        return module 


class BoundModuleFunction:
    def __init__(self, module, name, runtime):
        self.module = module 
        self.name = name 
        self.runtime = runtime 
    
    def call(self, args):
        funcdef = self.module.functions[self.name]
        
        # Save runtime state
        old_globals = self.runtime.globals 
        old_functions = self.runtime.functions 
        old_classes = self.runtime.classes
        
        # Set module context
        self.runtime.globals = self.module.globals 
        self.runtime.functions = self.module.functions 
        self.runtime.classes = self.module.classes
        
        try:
            # Execute function
            self.runtime.push_scope({})
            try:
                # Bind parameters
                for i, param in enumerate(funcdef.params):
                    if i < len(args):
                        self.runtime.current_scope()[param.name] = args[i]
                    elif param.default is not None:
                        self.runtime.current_scope()[param.name] = self.runtime.eval(param.default)
                    else:
                        raise Exception(f"Missing parameter '{param.name}'")
                
                # Execute body
                for stmt in funcdef.body:
                    result = self.runtime.execute_node(stmt)
                    if isinstance(result, ReturnSignal):
                        return result.value 
                return None 
            finally:
                self.runtime.pop_scope()
        finally:
            # Restore runtime state
            self.runtime.globals = old_globals 
            self.runtime.functions = old_functions
            self.runtime.classes = old_classes


class Module:
    def __init__(self, name):
        self.name = name 
        self.globals = {}
        self.functions = {}
        self.classes = {}
    
    def __repr__(self):
        return f"<Module {self.name}>"