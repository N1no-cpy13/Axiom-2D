# axm/module_loader.py 

import os
from .lexer import lex 
from .parser import parse 
from .ast import Import 
from .signals import ReturnSignal

class ModuleLoader:
    def __init__(self, runtime):
        self.runtime = runtime 
        self.loaded_modules = {} # {module_name: Module} 
        self.loading = set() # Circular check 
    
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
        
        # Execute (in new scope)
        module_name = os.path.splitext(os.path.basename(resolved_path))[0]
        module = Module(module_name)
        
        # Save state 
        old_globals = self.runtime.globals 
        old_functions = self.runtime.functions 
        old_pc = self.runtime.pc 
        
        self.runtime.globals = {}
        self.runtime.functions = {}
        
        # Mark loading 
        self.loading.add(resolved_path)
        
        try:
            # Execute all nodes 
            for node in ast:
                if isinstance(node, Import):
                    mod = self.load(node.path, base_dir=os.path.dirname(resolved_path)) # Recursive 
                    mod_name = node.path.replace(".axc", "").split("/")[-1].split("\\")[-1]
                    
                    self.runtime.globals[mod_name] = mod 
                else:
                    self.runtime.execute_node(node)
                
            # Save module 
            module.globals = self.runtime.globals.copy()
            module.functions = self.runtime.functions.copy()
        finally:
            # Restore 
            self.runtime.globals = old_globals 
            self.runtime.functions = old_functions
            self.runtime.pc = old_pc 
            self.loading.discard(resolved_path)
        
        self.loaded_modules[resolved_path] = module 
        return module 

class BoundModuleFunction:
    def __init__(self, module, name, runtime):
        self.module = module 
        self.name = name 
        self.runtime = runtime 
    
    def call(self, args):
        funcdef = self.module.functions[self.name]
        
        # Save state 
        old_globals = self.runtime.globals 
        old_functions = self.runtime.functions 
        
        # Set module context 
        self.runtime.globals = self.module.globals 
        self.runtime.functions = self.module.functions 
        
        try:
            # Execute functions
            self.runtime.push_scope({})
            try:
                for i, param in enumerate(funcdef.params):
                    if i < len(args):
                        self.runtime.current_scope()[param.name] = args[i]
                
                for stmt in funcdef.body:
                    result = self.runtime.execute_node(stmt)
                    if isinstance(result, ReturnSignal):
                        return result.value 
                return None 
            finally:
                self.runtime.pop_scope()
        finally:
            self.runtime.globals = old_globals 
            self.runtime.functions = old_functions


class Module:
    def __init__(self, name):
        self.name = name 
        self.globals = {}
        self.functions = {}
    
    def __repr__(self):
        return f"<Module {self.name}>"