
import argparse
import csv
from pathlib import Path
from types import SimpleNamespace

from lexer import lex, write_outputs
from parser import create_parser

KEYWORD_TYPES = {
    "input": "INPUT",
    "output": "OUTPUT",
    "destinations": "DESTINATIONS",
    "if": "IF",
    "else": "ELSE",
    "end": "END",
    "for": "FOR",
    "in": "IN",
    "and": "AND",
    "or": "OR",
    "true": "TRUE",
    "false": "FALSE"
}

SYMBOL_TYPES = {
    "=": "ASSIGN",
    "==": "EQ",
    "!=": "NE",
    ">=": "GE",
    "<=": "LE",
    ">": "GT",
    "<": "LT",
    "+": "PLUS",
    "-": "MINUS",
    "?": "QUESTION",
    ".": "DOT",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
    ",": "COMMA",
    ":": "COLON"
}

def get_token_type(category, lexeme):
    if category == "KEYWORD":
        return KEYWORD_TYPES[lexeme]

    if category == "IDENTIFIER":
        return "IDENTIFIER"

    if category == "CONSTANT":
        if lexeme.startswith('"'):
            return "STRING"

        if "." in lexeme:
            return "DECIMAL"

        return "INTEGER"

    if category in ("OPERATOR", "DELIMITER"):
        return SYMBOL_TYPES[lexeme]

    raise ValueError(f"Unknown token: {category} {lexeme}")

def read_pif(pif_path):
    tokens = []

    with pif_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(
            f,
            delimiter="\t",
            quoting=csv.QUOTE_NONE
        )

        for row in reader:
            category_code = int(row["TOKEN_CODE"])
            lexeme = row["TOKEN"]

            categories = {
                1: "KEYWORD",
                2: "IDENTIFIER",
                3: "CONSTANT",
                4: "OPERATOR",
                5: "DELIMITER"
            }

            category = categories[category_code]
            token_type = get_token_type(category, lexeme)

            token = SimpleNamespace(
                type=token_type,
                value=lexeme,
                lineno=int(row["LINE"]),
                lexpos=0
            )

            tokens.append(token)

    return tokens

class PIFLexer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def token(self):
        if self.position >= len(self.tokens):
            return None

        token = self.tokens[self.position]
        self.position += 1
        return token

def write_productions(productions, output_path):
    with output_path.open("w", encoding="utf-8") as f:
        for index, production in enumerate(productions, start=1):
            f.write(f"{index}. {production}\n")

def main():
    argument_parser = argparse.ArgumentParser(
        description="Travel Plan DSL syntax analyzer"
    )

    argument_parser.add_argument(
        "source",
        help="Source program (.txt)"
    )

    argument_parser.add_argument(
        "--out",
        default="output",
        help="Output directory"
    )

    args = argument_parser.parse_args()

    source_path = Path(args.source)
    output_dir = Path(args.out)

    source = source_path.read_text(encoding="utf-8")

    tokens, lexical_errors = lex(source)

    write_outputs(tokens, lexical_errors, output_dir)

    productions_path = output_dir / "productions.txt"

    if lexical_errors:
        productions_path.write_text(
            "Parsing skipped because lexical errors were found.\n",
            encoding="utf-8"
        )

        print("Lexical analysis failed.")
        print(f"Lexical errors: {len(lexical_errors)}")
        print(f"See: {output_dir / 'errors.txt'}")
        return

    pif_tokens = read_pif(output_dir / "pif.txt")

    parser = create_parser()
    lexer = PIFLexer(pif_tokens)

    try:
        syntax_tree = parser.parse(lexer=lexer)

        if syntax_tree is None:
            raise SyntaxError("No syntax tree was generated")

        productions = syntax_tree.get_productions()

        write_productions(productions, productions_path)

        print("Lexical analysis: SUCCESS")
        print("Syntax analysis: SUCCESS")
        print(f"Productions: {len(productions)}")
        print(f"Output directory: {output_dir.resolve()}")

    except SyntaxError as error:
        productions_path.write_text(
            f"Syntax error: {error}\n",
            encoding="utf-8"
        )

        print("Lexical analysis: SUCCESS")
        print("Syntax analysis: FAILED")
        print(error)

if __name__ == "__main__":
    main()