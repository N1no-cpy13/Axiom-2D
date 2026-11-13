
# axm/ast.py

class Node:
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

# ========== Statements ==========
class Say(Node):
    def __init__(self, expr): 
        self.expr = expr
    def __repr__(self):
        return f'Say("{self.expr}")'

class SayF(Node):
    def __init__(self, parts):  # parts = list of Expr
        self.parts = parts
    def __repr__(self):
        return f'SayF({self.parts})'

class Move(Node):
    def __init__(self, entity, amount, direction):
        self.entity = entity      # Expr
        self.amount = amount      # Expr
        self.direction = direction  # Expr
    def __repr__(self):
        return f"Move({self.entity}, {self.amount}, {self.direction})"
 

class Sleep(Node):
    def __init__(self, duration, unit: str):
        self.duration = duration  # Expr
        self.unit = unit          # Expr
    def __repr__(self):
        return f"Sleep({self.duration}, {self.unit})"

class For(Node):
    def __init__(self, var_name, times, body):
        self.var_name = var_name
        self.times = times        # Expr
        self.body = body
    def __repr__(self):
        return f"For({self.var_name} range {self.times})"

class If(Node):
    def __init__(self, condition, body, elifs, else_body=None):
        self.condition = condition
        self.body = body
        self.elifs = elifs 
        self.else_body = else_body if else_body is not None else []
    def __repr__(self):
        return f"If(cond={self.condition}, body={self.body}, elifs={self.elifs}, else={self.else_body})"

class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self._index = 0
    def __repr__(self):
        return f"While({self.condition}, body={self.body})"

class Damage(Node):
    def __init__(self, entity, amount):
        self.entity = entity      # Expr
        self.amount = amount      # Expr
    def __repr__(self):
        return f'Damage({self.entity}, {self.amount})'

class Heal(Node):
    def __init__(self, entity, amount):
        self.entity = entity # Expr (EntityRef)
        self.amount = amount # Expr (Number)
    def __repr__(self):
        return f'Heal({self.entity}, {self.amount})'

class Var(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value        # Expr
    def __repr__(self):
        return f"Var({self.name} = {self.value})"

class Assignment(Node):
    def __init__(self, name, value):
        self.name = name 
        self.value = value
    def __repr__(self):
        return f"Assignment({self.name} = {self.value})"

class DictAssignment(Node):
    def __init__(self, target, key, value):
        self.target = target # Expr (dict)
        self.key = key # Expr (key)
        self.value = value # Expr (value)
    def __repr__(self):
        return f"DictAssignment({self.target}[{self.key}] = {self.value})"

class ListLiteral(Node):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"List({self.elements})"

class IndexAccess(Node):
    def __init__(self, target, index):
        self.target = target
        self.index = index

    def __repr__(self):
        return f"Index({self.target}[{self.index}])"
        
class Parameter(Node):
    def __init__(self, name, param_type=None, default=None):
        self.name = name 
        self.param_type = param_type
        self.default = default
    
    def __repr__(self):
        type_str = f": {self.param_type}" if self.param_type else ""
        default_str = f" = {self.default}" if self.default is not None else ""
        
        return f"Parameter({self.name}{type_str}{default_str})"

class FunctionDef(Node):
    def __init__(self, name, params, body):
        self.name = name 
        self.params = params # list of Parameter objects
        self.body = body # list of statements
        self.owner_class = None
    
    def __repr__(self):
        params_str = ', '.join([str(p) for p in self.params])
        return f"FunctionDef({self.name}({params_str}))"
     
class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name 
        self.args = args 
    def __repr__(self):
        return f"FunctionCall({self.name}({self.args}))"

class MethodCall(Node):
    def __init__(self, obj, method, args):
        self.obj = obj # Expr
        self.method = method 
        self.args = args 
    def __repr__(self):
        return f"MethodCall({self.obj}.{self.method}({self.args}))"

class Return(Node):
    def __init__(self, value):
        self.value = value    # Expr or None
    def __repr__(self):
        return f"Return({self.value})"

class Break(Node):
    def __repr__(self):
        return "Break"

class Continue(Node):
    def __repr__(self):
        return "Continue"

class Import(Node):
    def __init__(self, path):
        self.path = path  # string 
    def __repr__(self):
        return f'Import("{self.path}")'

class ClassDef(Node):
    def __init__(self, name, parent, body):
        self.name = name 
        self.parent = parent # None or Expr or str 
        self.body = body # List of Var and FunctionDef 
    def __repr__(self):
        return f"ClassDef({self.name}, parent={self.parent})"

# ========== Expressions ==========
class Expr(Node):
    pass

class BinaryOp(Expr):
    def __init__(self, left, op, right):
        self.left = left   
        self.op = op       
        self.right = right 
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.op} {self.right})"

class LogicalOp(Expr):
    def __init__(self, left, op, right=None):
        self.left = left    
        self.op = op        
        self.right = right  
    def __repr__(self):
        if self.op == 'NOT':
            return f"LogicalOp(NOT {self.left})"
        return f"LogicalOp({self.left} {self.op} {self.right})"

class Number(Expr):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Number({self.value})"

class String(Expr):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'String("{self.value}")'

class Boolean(Expr):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Boolean({self.value})"

class Variable(Expr):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Variable({self.name})"

class EntityRef(Expr):
    def __init__(self, name):
        self.name = name 
    def __repr__(self):
        return f"EntityRef(@{self.name})"

class Null(Expr):
    def __init__(self):
        pass 
    def __repr__(self):
        return "Null()"

class Attribute(Expr):
    def __init__(self, obj, attr):
        self.obj = obj      # Expr (usually Variable)
        self.attr = attr    # string
    def __repr__(self):
        return f"Attribute({self.obj}.{self.attr})"

class ListLiteral(Expr):
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"List({self.elements})"

class IndexAccess(Expr):
    def __init__(self, target, index):
        self.target = target
        self.index = index
    def __repr__(self):
        return f"Index({self.target}[{self.index}])"

class DictLiteral(Expr):
    def __init__(self, pairs):
        self.pairs = pairs
    def __repr__(self):
        return f"Dict({self.pairs})"

class DictAccess(Expr):
    def __init__(self, target, key):
        self.target = target
        self.key = key
    def __repr__(self):
        return f"DictAccess({self.target}[{self.key}])"

class NewExpr(Expr):
    def __init__(self, class_name, args):
        self.class_name = class_name  # str atau Expr (Attribute)
        self.args = args
    def __repr__(self):
        return f"New({self.class_name}, {self.args})"

class SelfExpr(Expr):
    def __repr__(self):
        return "Self()"

class SuperExpr(Expr):
    def __repr__(self):
        return "Super()"