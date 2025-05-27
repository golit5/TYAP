import sys
from enum import Enum, auto

# Типы токенов
class TokenType(Enum):
    PROGRAM = auto()
    VAR = auto()
    BEGIN = auto()
    END = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    FOR = auto()
    TO = auto()
    DO = auto()
    WHILE = auto()
    READ = auto()
    WRITE = auto()
    ASS = auto()  # оператор присваивания
    ID = auto()
    INTEGER = auto()    # %
    FLOAT = auto()  # !
    BOOLEAN = auto()    # $
    LITERAL = auto()
    SEMICOLON = auto()  # ;
    COLON = auto()     # :
    COMMA = auto()     # ,
    DOT = auto()       # .
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    # Операции
    OP_REL = auto()    # < > = <= >=
    OP_ADD = auto()    # + - or
    OP_MUL = auto()    # * / and
    OP_UN = auto()     # not
    EOF = auto()

# Класс токена
class Token:
    def __init__(self, type: TokenType, value: int | str | None =None ):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

# Лексический анализатор
class Lexer:
    def __init__(self, text : str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def error(self):
        raise Exception(self.current_char, "Недопустимый символ")
    
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        while self.current_char != '}' and self.current_char is not None:
            self.advance()
        if self.current_char == '}':
            self.advance()
    
    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            result += '.'
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token(TokenType.LITERAL, float(result))
        return Token(TokenType.LITERAL, int(result))
    
    def _id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Ключевые слова
        keywords = {
            'program': TokenType.PROGRAM,
            'var': TokenType.VAR,
            'begin': TokenType.BEGIN,
            'end': TokenType.END,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'for': TokenType.FOR,
            'to': TokenType.TO,
            'do': TokenType.DO,
            'while': TokenType.WHILE,
            'read': TokenType.READ,
            'write': TokenType.WRITE,
            'ass': TokenType.ASS,
            'or': TokenType.OP_ADD,
            'and': TokenType.OP_MUL,
            'not': TokenType.OP_UN,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN
        }
        
        return Token(keywords.get(result.lower(), TokenType.ID), result)
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';')
            
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':')
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',')
            
            if self.current_char == '.':
                self.advance()
                return Token(TokenType.DOT, '.')
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')
            
            if self.current_char == '%':
                self.advance()
                return Token(TokenType.INTEGER, '%')
            
            if self.current_char == '!':
                self.advance()
                return Token(TokenType.FLOAT, '!')
            
            if self.current_char == '$':
                self.advance()
                return Token(TokenType.BOOLEAN, '$')

            # Операции отношения
            if self.current_char in ('<', '>', '='):
                prev_char = self.current_char
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.OP_REL, prev_char + '=')
                return Token(TokenType.OP_REL, prev_char)
            
            # Операции сложения
            if self.current_char in ('+', '-'):
                char = self.current_char
                self.advance()
                return Token(TokenType.OP_ADD, char)
            
            # Операции умножения
            if self.current_char in ('*', '/'):
                char = self.current_char
                self.advance()
                return Token(TokenType.OP_MUL, char)
            
            self.error()
        
        return Token(TokenType.EOF, None)

class Symbol:
    def __init__(self, name, type_, value=None):
        self.name = name
        self.type = type_  # %, ! или $
        self.value = value
    
    def __repr__(self):
        return f"Symbol(name={self.name}, type={self.type}, value={self.value})"

class SymbolTable:
    def __init__(self):
        self.symbols = {}  # Просто словарь для хранения Symbol объектов
    
    def define(self, symbol):
        if symbol.name in self.symbols:
            raise NameError(f"Переменная {symbol.name} уже объявлена")
        self.symbols[symbol.name] = symbol
    
    def lookup(self, name):
        return self.symbols.get(name)

# Абстрактное синтаксическое дерево
class AST:
    pass

class Program(AST):
    def __init__(self, declarations , compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Compound(AST):
    def __init__(self):
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class If(AST):
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Literal(AST):
    def __init__(self, token):
        self.token = token
        if token.type == TokenType.BOOLEAN:
            if token.value == 'true':
                self.value = True
            else:
                self.value = False
        else:
            self.value = token.value

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class NoOp(AST):
    pass

class Write(AST):
    def __init__(self, expressions):
        self.expressions = expressions

# Парсер
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self):
        raise Exception("Синтаксическая ошибка")
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def program(self):
        """program : PROGRAM VAR (variable_declaration SEMICOLON)+ BEGIN compound_statement END DOT"""
        self.eat(TokenType.PROGRAM)
        self.eat(TokenType.VAR)
        declarations = []
        
        while self.current_token.type == TokenType.ID:
            var_decl = self.variable_declaration()
            declarations.extend(var_decl)
            self.eat(TokenType.SEMICOLON)
        
        self.eat(TokenType.BEGIN)
        compound_statement = self.compound_statement()
        self.eat(TokenType.END)
        self.eat(TokenType.DOT)
        
        return Program(declarations, compound_statement)
    
    def variable_declaration(self):
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token)]
        self.eat(TokenType.ID)
        
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(TokenType.ID)
        
        self.eat(TokenType.COLON)
        
        type_node = self.type_spec()
        return [VarDecl(var_node, type_node) for var_node in var_nodes]
    
    def type_spec(self):
        """type_spec : % | ! | $"""
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
        elif token.type == TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
        else:
            self.error()
        return Type(token)
    
    def compound_statement(self):
        """compound_statement : statement (SEMICOLON statement)*"""
        compound = Compound()
        compound.children.append(self.statement())
        
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            compound.children.append(self.statement())
        
        return compound
    
    def statement(self):
        if self.current_token.type == TokenType.BEGIN:
            return self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            return self.assignment_statement()
        elif self.current_token.type == TokenType.IF:
            return self.if_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.for_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.while_statement()
        elif self.current_token.type == TokenType.READ:
            return self.read_statement()
        elif self.current_token.type == TokenType.WRITE:
            return self.write_statement()
        else:
            return self.empty()

    def if_statement(self):
        self.eat(TokenType.IF)
        condition = self.expr()
        self.eat(TokenType.THEN)
        true_branch = self.statement()
        
        false_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            false_branch = self.statement()
        
        return If(condition, true_branch, false_branch)

    def assignment_statement(self):
        """assignment_statement : variable ASS expr"""
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASS)
        right = self.expr()  # Вот ключевое изменение - используем expr() вместо statement()
        return Assign(left, token, right)

    def expr(self):
        """expr : simple_expr ((< | = | > | <= | >=) simple_expr)?"""
        node = self.simple_expr()
        
        while self.current_token.type == TokenType.OP_REL:
            token = self.current_token
            self.eat(TokenType.OP_REL)
            node = BinOp(left=node, op=token, right=self.simple_expr())
        
        return node

    def simple_expr(self):
        """simple_expr : term ((+ | - | or) term)*"""
        node = self.term()
        
        while self.current_token.type == TokenType.OP_ADD:
            token = self.current_token
            self.eat(TokenType.OP_ADD)
            node = BinOp(left=node, op=token, right=self.term())
        
        return node

    def term(self):
        """term : factor ((* | / | and) factor)*"""
        node = self.factor()
        
        while self.current_token.type == TokenType.OP_MUL:
            token = self.current_token
            self.eat(TokenType.OP_MUL)
            node = BinOp(left=node, op=token, right=self.factor())
        
        return node

    def factor(self):
        """factor : (+ | - | not) factor | variable | literal | ( expr )"""
        token = self.current_token
        
        if token.type == TokenType.OP_ADD and token.value in ('+', '-'):
            self.eat(TokenType.OP_ADD)
            return UnaryOp(op=token, expr=self.factor())
        elif token.type == TokenType.OP_UN:
            self.eat(TokenType.OP_UN)
            return UnaryOp(op=token, expr=self.factor())
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.ID:
            return self.variable()
        elif token.type == TokenType.LITERAL:
            return self.literal()
        elif token.type == TokenType.BOOLEAN:
            return self.literal()

        else:
            self.error()
    
    def literal(self):
        node = Literal(self.current_token)
        self.eat(TokenType.LITERAL)
        return node
    
    def variable(self):
        """variable : ID"""
        node = Var(self.current_token)
        self.eat(TokenType.ID)
        return node
    
    def write_statement(self):
        """write_statement : WRITE LPAREN expr (COMMA expr)* RPAREN"""
        self.eat(TokenType.WRITE)
        self.eat(TokenType.LPAREN)
        
        # Собираем все выражения для вывода
        expressions = []
        expressions.append(self.expr())
        
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            expressions.append(self.expr())
        
        self.eat(TokenType.RPAREN)
        return Write(expressions)

    def empty(self):
        return NoOp()
    
    def parse(self):
        node = self.program()
        print(node)
        if self.current_token.type != TokenType.EOF:
            self.error()
        return node

    def for_statement(self):
        self.eat(TokenType.FOR)
        assign = self.assignment_statement()
        self.eat(TokenType.TO)
        final_value = self.expr()
        self.eat(TokenType.DO)
        body = self.statement()
        return (assign, final_value, body)

    def while_statement(self):
        self.eat(TokenType.WHILE)
        condition = self.expr()
        self.eat(TokenType.DO)
        body = self.statement()
        return (condition, body)
    
    def read_statement(self):
        self.eat(TokenType.READ)
        self.eat(TokenType.LPAREN)
        vars = [self.variable()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            vars.append(self.variable())
        self.eat(TokenType.RPAREN)
        return vars




# Интерпретатор
class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.symtab = SymbolTable()
    
    def interpret(self):
        tree = self.parser.parse()
        self.visit(tree)
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception(f'Нет метода visit_{type(node).__name__}')
    
    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compound_statement)
    
    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        var_type = node.type_node.value
        
        if self.symtab.lookup(var_name) is not None:
            raise NameError(f"Переменная '{var_name}' уже объявлена")
        
        if var_type == '%':
            default_value = 0
        elif var_type == '!':
            default_value = 0.0
        elif var_type == '$':
            default_value = False
        else:
            raise TypeError(f"Неизвестный тип '{var_type}'")
        
        self.symtab.define(Symbol(var_name, var_type, default_value))
    
    def visit_Type(self, node):
        pass
    
    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)
    
    def visit_Assign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        symbol = self.symtab.lookup(var_name)
        if symbol is None:
            raise NameError(f"Переменная '{var_name}' не объявлена")
        symbol.value = value  # Просто присваиваем значение напрямую

    def visit_Var(self, node):
        var_name = node.value
        symbol = self.symtab.lookup(var_name)
        if symbol is None:
            raise NameError(f"Идентификатор не найден: {var_name}")
        return symbol.value
    
    def visit_Literal(self, node):
        return node.value
    
    def visit_Write(self, node):
        results = []
        for expr in node.expressions:
            value = self.visit(expr)
            results.append(str(value))
        print(' '.join(results))

    def visit_BinOp(self, node):
        """Обработка бинарных операций"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Проверка типов (можно вынести в отдельный метод)
        if isinstance(left, bool) or isinstance(right, bool):
            if node.op.type != TokenType.OP_MUL or node.op.value != 'and':
                if node.op.type != TokenType.OP_ADD or node.op.value != 'or':
                    raise TypeError("Логические операции поддерживают только 'and' и 'or'")
        
        # Операции группы умножения (*, /, and)
        if node.op.type == TokenType.OP_MUL:
            if node.op.value == '*':
                return left * right
            elif node.op.value == '/':
                if right == 0:
                    raise ZeroDivisionError("Деление на ноль")
                return left / right
            elif node.op.value == 'and':
                return left and right
        
        # Операции группы сложения (+, -, or)
        elif node.op.type == TokenType.OP_ADD:
            if node.op.value == '+':
                return left + right
            elif node.op.value == '-':
                return left - right
            elif node.op.value == 'or':
                return left or right
        
        # Операции группы отношения (<, >, =, <=, >=)
        elif node.op.type == TokenType.OP_REL:
            if node.op.value == '<':
                return left < right
            elif node.op.value == '<=':
                return left <= right
            elif node.op.value == '>':
                return left > right
            elif node.op.value == '>=':
                return left >= right
            elif node.op.value == '=':
                return left == right
        
        raise ValueError(f"Неизвестный бинарный оператор: {node.op.value}")

    def visit_NoOp(self, node):
        pass

    def visit_If(self, node):
        condition = self.visit(node.condition)
        if condition:
            self.visit(node.true_branch)
        elif node.false_branch is not None:
            self.visit(node.false_branch)

    def visit_tuple(self, node):
        if len(node) == 3:
            # for: (assign, final_value, body)
            assign, final_value_expr, body = node
            self.visit(assign)
            var_name = assign.left.value
            final_value = self.visit(final_value_expr)
            while self.symtab.lookup(var_name).value <= final_value:
                self.visit(body)
                self.symtab.lookup(var_name).value += 1
        elif len(node) == 2:
            # while: (condition, body)
            condition, body = node
            while self.visit(condition):
                self.visit(body)

    def visit_list(self, node):
        for var in node:
            var_name = var.value
            symbol = self.symtab.lookup(var_name)
            if symbol is None:
                raise NameError(f"Переменная '{var_name}' не объявлена")
            # тестово присваиваем 1
            symbol.value = 1

    

def main():
    # Создадим файл с тестовыми программами
    test_programs = """
    program var
        a, b, c: %;
    begin
        a ass 5;
        b ass 3;
        c ass (a + b) * 2;
        write(c)
    end.

    program var
        a, b: %;
    begin
        a ass 10;
        b ass 20;
        if a < b then
            write(a)
        else
            write(b)
    end.

    program var
        flag1, flag2: $;
    begin
        flag1 ass true;
        flag2 ass not flag1;
        write(flag2)
    end.

    program var
        x, y: %, result: $;
    begin
        x ass 5;
        y ass 10;
        result ass (x < y) and (y > 0);
        write(result)
    end.

    program var
        a, b, c: $;
    begin
        a ass true;
        b ass false;
        c ass a or b;
        write(c)
    end.

    program var
        a, b, c: !;
    begin
        a ass 10.0;
        b ass 3.0;
        c ass a / b;
        write(c)
    end.

    program var
        i, sum: %;
    begin
        sum ass 0;
        for i ass 1 to 5 do
            sum ass sum + i;
        write(sum)
    end.

    program var
        a: %;
    begin
        a ass 5;
        while a > 0 do
            a ass a - 1;
        write(a)
    end.

    program var
        a, b: %, c: $;
    begin
        a ass 10;
        b ass 20;
        c ass a <= b;
        write(c)
    end.

    program var
        a, b: %;
    begin
        a ass 10;
        b ass 20;
        if a < b then
            if a = 10 then
                write(100)
            else
                write(200)
        else
            write(300)
    end.

    program var
        a, b: %, c: !;
    begin
        a ass 10;
        b ass 0;
        c ass a / b;
        write(c)
    end.

    program var
        a: %;
    begin
        a ass 5;
        b ass 10;
        write(a)
    end.

    program var
        a: %;
        a: %;
    begin
        a ass 5;
        write(a)
    end.

    program var
        a, b: %;
    begin
        read(a, b);
        a ass a + b;
        write(a)
    end.
    """


    # Запишем в файл
    with open('./test_programs.tyap', 'w') as f:
        f.write(test_programs)


    # Функция для тестирования программы на синтаксический разбор
    def test_syntax(text):
        try:
            lexer = Lexer(text)
            parser = Parser(lexer)
            parser.parse()
            return "OK"
        except Exception as e:
            return str(e)
    
    def test_exec(text):
        try:
            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            interpreter.interpret()
            return "OK"
        except Exception as e:
            return str(e)

    # Разделим по программам (по вхождениям 'program var')
    program_list = test_programs.strip().split("program var")
    program_list = ["program var" + p for p in program_list if p.strip()]

    # Проверим каждую
    results = [test_syntax(p) for p in program_list]
    print(results)

    results1 = [test_exec(p) for p in program_list]
    print(results1)


if __name__ == '__main__':
    main()
