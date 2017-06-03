import ast
import operator
import datetime
from collections.abc import Mapping
from src.Methods import GetMethod


class Operators(Mapping):
    def __init__(self, *args, **kwargs):
        self._ops = args[0]
        super()

    def __getitem__(self, key):
        return next(v for k, v in self._ops.items() if isinstance(key, k))

    def __iter__(self):
        return iter(self._ops)

    def __len__(self):
        return len(self)


class Rule:
    """."""

    def __init__(self, *args, **kwargs):
        """."""
        self.operators = Operators({ast.Add: operator.add,
                                    ast.Sub: operator.sub,
                                    ast.Mult: operator.mul,
                                    ast.Div: operator.truediv,
                                    ast.Pow: operator.pow,
                                    ast.BitXor: operator.xor,
                                    ast.USub: operator.neg,
                                    ast.UAdd: operator.pos,
                                    ast.Eq: operator.eq,
                                    ast.Lt: operator.lt})

        self.valid_funcs = {'time': datetime.time,
                            'date': datetime.date,
                            'count': len}
        self.method_getter = GetMethod(parent_id=kwargs['parent_id'],
                                       db_name=kwargs['db_name'])
        self.keywordargs = {}
        self.name = kwargs['name']
        self.conditions = kwargs['conditions']
        self.rule = kwargs['rule']
        self.award = kwargs['award']
        self.name_space = self.create_rule_function()

    # def __getnewargs_ex__(self):
    #    return ({'callattr': callattr})

    def __call__(self):
        return self.func()

    def func(self):
        return eval(self.rule, self.name_space)

    def create_rule_function(self):
        name_space = {}
        for name, cond in self.conditions.items():
            pars_obj = ast.parse(cond)
            body = pars_obj.body[0]
            expr = body.value

            right = expr.comparators[0]
            left = expr.left
            try:
                op = expr.op
            except AttributeError:
                op = expr.ops[0]
            name_space[name] = self.create_cond_function(left, op, right)

        return name_space

# Ask in stack: most optimized way for pickling a AST obejct (evaluating the constants and function calls but let the methd access to be addressed dinamically)
    def create_cond_function(self, left, op, right):
        """Perform the operator on left and right side of the operation."""
        return self.operators[op](self.parser(left),
                                  self.parser(right))

    def parser(self, expr):
        """."""
        # Two sides of an expression in general can be one of the followings:
        # Call, BinOp, Attribute, values (Str, Num, etc)
        generic_types = (ast.UnaryOp, ast.Str, ast.Num, ast.Set, ast.List)
        if isinstance(expr, generic_types):
            return self.__parse_generic_types(expr)
        elif isinstance(expr, ast.BinOp):
            return self.__parse_binary_operation(expr)
        elif isinstance(expr, ast.Call):
            return self.__parse_callable_types(expr)
        elif isinstance(expr, ast.Attribute):
            attrs = self.__parse_attr(expr)
            return attrs

        else:
            raise Exception('')

    def __parse_binary_operation(self, expr):
        left = expr.left
        op = expr.op
        right = expr.right
        return self.operators[op](self.parser(left), self.parser(right))

    def __parse_generic_types(self, expr):
        if isinstance(expr, ast.UnaryOp):
            return self.operators[expr.op](expr.operand)
        elif isinstance(expr, ast.Str):
            return expr.s
        elif isinstance(expr, ast.Num):
            return expr.n
        elif isinstance(expr, ast.Set):
            return {self.__parse_generic_types(i) for i in expr.elts}
        elif isinstance(expr, ast.List):
            return [self.__parse_generic_types(i) for i in expr.elts]
        elif isinstance(expr, ast.Attribute):
            return self.__parse_attr(expr)

    def __parse_callable_types(self, expr):
        name = expr.func.id
        keywords = {i.arg: self.__parse_attr(i.value) if isinstance(i.value, ast.Attribute) else self.__parse_generic_types(i.value) for i in expr.keywords}
        args = [self.__parse_attr(i.value) if isinstance(i.value, ast.Attribute) else self.__parse_generic_types(i.value) for i in expr.args]
        return self.valid_funcs[name](*args, **keywords)

    def __parse_attr(self, expr):
        def get_attrs(expr):
            while True:
                try:
                    yield expr.attr
                except:
                    yield expr.id
                    break
                else:
                    expr = expr.value

        attrs = list(get_attrs(expr))[::-1]
        attr_name = '.'.join(attrs)
        self.keywordargs[attr_name] = attrs
        return self.method_getter[attrs]
        # return self.methods[attr_name]
