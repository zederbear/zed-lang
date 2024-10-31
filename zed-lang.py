import re

# Step 1: Lexer
token_patterns = [
    (r'\bfunc\b', 'FUNC'),
    (r'\bend\b', 'END'),
    (r'\breturn\b', 'RETURN'),
    (r'\bstring\b', 'TYPE'),  # Currently supports 'string' type
    (r'\bprint\b', 'PRINT'),
    (r'[a-zA-Z_]\w*', 'IDENTIFIER'),  # For variable and function names
    (r'\(', 'LPAREN'),
    (r'\)', 'RPAREN'),
    (r':', 'COLON'),
    (r'\'[^\']*\'|\"[^\"]*\"', 'STRING'),  # Matches a string enclosed in single quotes
    (r'\s+', None),  # Ignore whitespace
]

def lex(code):
    tokens = []
    while code:
        match = None
        for pattern, token_type in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(code)
            if match:
                text = match.group(0)
                if token_type:  # Skip None (whitespace)
                    tokens.append((token_type, text))
                code = code[len(text):]
                break
        if not match:
            raise SyntaxError(f"Unexpected character: {code[0]}")
    return tokens

# Step 2: Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type):
        token = self.current_token()
        if token and token[0] == expected_type:
            self.pos += 1
            return token
        else:
            raise SyntaxError(f"Expected {expected_type} but got {token}")

    def parse_function(self):
        self.consume('FUNC')
        func_name = self.consume('IDENTIFIER')[1]
        self.consume('LPAREN')
        self.consume('RPAREN')
        return_type = self.consume('TYPE')[1]

        # Parse function body (handling only return statements for now)
        body = []
        while self.current_token() and self.current_token()[0] != 'END':
            token = self.current_token()
            if token and token[0] == 'RETURN':
                self.consume('RETURN')
                return_value = self.consume('STRING')[1]
                body.append(('RETURN', return_value))
            elif token and token[0] == 'PRINT':
                self.consume('PRINT')
                print_value = self.consume('STRING')[1]
                body.append(('PRINT', print_value))
            else:
                raise SyntaxError(f"Unexpected Token: {token}")
        
        self.consume('END')
        return {
            'type': 'function',
            'name': func_name,
            'return_type': return_type,
            'body': body
        }
    def parse_statement(self):
        token = self.current_token()
        if token[0] == 'FUNC':
            return self.parse_function()
        elif token[0] == 'PRINT':
            self.consume('PRINT')
            print_value = self.consume('STRING')[1]
            return ('PRINT', print_value)
        elif token[0] == 'IDENTIFIER':
            func_name = self.consume('IDENTIFIER')[1]
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ('CALL', func_name)
        else:
            raise SyntaxError(f"Unexpected token: {token}")
    
    def parse(self):
        statements = []
        while self.current_token():
            statements.append(self.parse_statement())
        return statements
# Step 3: Interpreter
class Interpreter:
    def __init__(self):
        self.functions = {}

    def define_function(self, func_ast):
        # Store the function AST in a dictionary
        func_name = func_ast['name']
        self.functions[func_name] = func_ast
    
    def call_function(self, func_name):
        # Retrieve the function AST and evaluate it
        if func_name not in self.functions:
            raise NameError(f"Function '{func_name}' is not defined.")
        func_ast = self.functions[func_name]
        self.evaluate_function(func_ast)
    
    def evaluate_function(self, func_ast):
        for stmt in func_ast['body']:
            if stmt[0] == 'PRINT':
                print(stmt[1])
            elif stmt[0] == 'RETURN':
                return_value = stmt[1][1:-1]
                print(f"Executing {func_ast['name']}: returns {return_value}")
                break
    
    def interpret(self, statements):
        for stmt in statements:
            if stmt[0] == 'PRINT':
                print(stmt[1][1:-1])
            elif stmt[0] == 'CALL':
                self.call_function(stmt[1])
            elif stmt[0] == 'function':
                self.define_function(stmt)

# Putting It All Together
code = open("hello.zed", "r").read()
tokens = lex(code)              # Lexing

parser = Parser(tokens)         # Parsing
statements = parser.parse()

interpreter = Interpreter()     # Interpreting
interpreter.interpret(statements)

