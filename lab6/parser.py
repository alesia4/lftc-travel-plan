
import ply.yacc as yacc

tokens = (
    "INPUT", "OUTPUT", "DESTINATIONS",
    "IF", "ELSE", "END", "FOR", "IN",
    "AND", "OR", "TRUE", "FALSE",
    "IDENTIFIER", "INTEGER", "DECIMAL", "STRING",
    "ASSIGN", "EQ", "NE", "GE", "LE", "GT", "LT",
    "PLUS", "MINUS", "QUESTION", "DOT",
    "LPAREN", "RPAREN",
    "LBRACKET", "RBRACKET",
    "LBRACE", "RBRACE",
    "COMMA", "COLON"
)

precedence = (
    ("left", "QUESTION"),
    ("left", "OR"),
    ("left", "AND"),
    ("nonassoc", "EQ", "NE", "GE", "LE", "GT", "LT"),
    ("left", "PLUS", "MINUS"),
    ("right", "UMINUS"),
    ("left", "DOT"),
)

class SyntaxNode:
    def __init__(self, production, children=None):
        self.production = production
        self.children = children or []

    def get_productions(self):
        result = [self.production]

        for child in self.children:
            if isinstance(child, SyntaxNode):
                result.extend(child.get_productions())

        return result

def make_node(p):
    left = p.slice[0].type
    right = [symbol.type for symbol in p.slice[1:]]

    production = f"{left} -> {' '.join(right)}"

    children = [
        value for value in p[1:]
        if isinstance(value, SyntaxNode)
    ]

    p[0] = SyntaxNode(production, children)

def p_program(p):
    "program : statements"
    make_node(p)

def p_statements_multiple(p):
    "statements : statements statement"
    make_node(p)

def p_statements_single(p):
    "statements : statement"
    make_node(p)

def p_statement(p):
    """statement : input_statement
                 | output_statement
                 | assignment
                 | destinations_statement
                 | if_statement
                 | for_statement"""
    make_node(p)

def p_input_statement(p):
    "input_statement : INPUT IDENTIFIER"
    make_node(p)

def p_output_statement(p):
    "output_statement : OUTPUT expression"
    make_node(p)

def p_assignment(p):
    "assignment : IDENTIFIER ASSIGN expression"
    make_node(p)

def p_destinations_statement(p):
    "destinations_statement : DESTINATIONS IDENTIFIER ASSIGN expression"
    make_node(p)

def p_if_statement(p):
    """if_statement : IF expression COLON statements END
                    | IF expression COLON statements ELSE COLON statements END"""
    make_node(p)

def p_for_statement(p):
    "for_statement : FOR IDENTIFIER IN expression COLON statements END"
    make_node(p)

def p_expression_binary(p):
    """expression : expression OR expression
                  | expression AND expression
                  | expression EQ expression
                  | expression NE expression
                  | expression GE expression
                  | expression LE expression
                  | expression GT expression
                  | expression LT expression
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression QUESTION expression
                  | expression DOT IDENTIFIER"""
    make_node(p)

def p_expression_unary(p):
    "expression : MINUS expression %prec UMINUS"
    make_node(p)

def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    make_node(p)

def p_expression_literal(p):
    """expression : IDENTIFIER
                  | INTEGER
                  | DECIMAL
                  | STRING
                  | TRUE
                  | FALSE
                  | list_literal
                  | object_literal"""
    make_node(p)

def p_list_literal(p):
    """list_literal : LBRACKET elements RBRACKET
                    | LBRACKET RBRACKET"""
    make_node(p)

def p_elements_multiple(p):
    "elements : elements COMMA expression"
    make_node(p)

def p_elements_single(p):
    "elements : expression"
    make_node(p)

def p_object_literal(p):
    """object_literal : LBRACE fields RBRACE
                      | LBRACE RBRACE"""
    make_node(p)

def p_fields_multiple(p):
    "fields : fields COMMA field"
    make_node(p)

def p_fields_single(p):
    "fields : field"
    make_node(p)

def p_field(p):
    "field : IDENTIFIER COLON expression"
    make_node(p)

def p_error(p):
    if p is None:
        raise SyntaxError("Unexpected end of input")

    raise SyntaxError(
        f"Unexpected token {p.type} ({p.value!r}) "
        f"at line {p.lineno}"
    )

def create_parser():
    return yacc.yacc(
        start="program",
        debug=False,
        write_tables=False
    )