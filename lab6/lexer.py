
import argparse
import re
from pathlib import Path

from hash_table import HashTable
from automata import (
    LETTERS,
    DIGITS,
    create_identifier_fa,
    create_integer_fa,
    create_decimal_fa,
    create_string_fa
)


KEYWORDS = {
    "destinations", "input", "output", "if", "else", "end",
    "for", "in", "and", "or", "true", "false"
}

TOKEN_CODES = {
    "KEYWORD": 1,
    "IDENTIFIER": 2,
    "CONSTANT": 3,
    "OPERATOR": 4,
    "DELIMITER": 5
}


IDENTIFIER_FA = create_identifier_fa()
INTEGER_FA = create_integer_fa()
DECIMAL_FA = create_decimal_fa()
STRING_FA = create_string_fa()


IDENTIFIER_CHARS = LETTERS | DIGITS | {"_"}
NUMBER_CHARS = IDENTIFIER_CHARS | {"."}


OPERATOR_RE = re.compile(r"==|!=|>=|<=|[=+\-<>?.]")
DELIMITER_RE = re.compile(r"[()\[\]{},:]")


def lex(source):
    tokens = []
    errors = []

    pos = 0
    line = 1
    col = 1

    while pos < len(source):
        ch = source[pos]

        if ch.isspace():
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1

            pos += 1
            continue

        if ch == "#":
            while pos < len(source) and source[pos] != "\n":
                pos += 1
                col += 1

            continue

        start_line = line
        start_col = col

        category = None
        lexeme = None

        if ch == '"':
            end = pos + 1

            while (
                end < len(source)
                and source[end] != '"'
                and source[end] != "\n"
            ):
                end += 1

            if end >= len(source) or source[end] == "\n":
                errors.append(
                    (line, col, "Unterminated string literal")
                )

                col += end - pos
                pos = end
                continue

            candidate = source[pos:end + 1]

            if STRING_FA.accepts(candidate):
                category = "CONSTANT"
                lexeme = candidate
            else:
                errors.append(
                    (line, col, f"Invalid string literal {candidate!r}")
                )

                pos += len(candidate)
                col += len(candidate)
                continue

        elif ch in DIGITS:
            end = pos

            while (
                end < len(source)
                and source[end] in NUMBER_CHARS
            ):
                end += 1

            candidate = source[pos:end]

            if INTEGER_FA.accepts(candidate) or DECIMAL_FA.accepts(candidate):
                category = "CONSTANT"
                lexeme = candidate
            else:
                errors.append(
                    (line, col, f"Malformed numeric token {candidate!r}")
                )

                pos = end
                col += len(candidate)
                continue

        elif ch in LETTERS or ch == "_":
            end = pos

            while (
                end < len(source)
                and source[end] in IDENTIFIER_CHARS
            ):
                end += 1

            candidate = source[pos:end]

            if IDENTIFIER_FA.accepts(candidate):
                category = (
                    "KEYWORD"
                    if candidate in KEYWORDS
                    else "IDENTIFIER"
                )
                lexeme = candidate
            else:
                errors.append(
                    (line, col, f"Invalid identifier {candidate!r}")
                )

                pos = end
                col += len(candidate)
                continue

        else:
            match = OPERATOR_RE.match(source, pos)

            if match:
                category = "OPERATOR"
                lexeme = match.group()

            else:
                match = DELIMITER_RE.match(source, pos)

                if match:
                    category = "DELIMITER"
                    lexeme = match.group()

                else:
                    errors.append(
                        (line, col, f"Invalid character {ch!r}")
                    )

                    pos += 1
                    col += 1
                    continue

        tokens.append({
            "category": category,
            "lexeme": lexeme,
            "line": start_line,
            "column": start_col,
            "code": TOKEN_CODES[category]
        })

        pos += len(lexeme)
        col += len(lexeme)

    return tokens, errors


def build_symbol_table(tokens):
    symbol_table = HashTable(capacity=101)

    for token in tokens:
        if token["category"] in ("IDENTIFIER", "CONSTANT"):
            key = (token["category"], token["lexeme"])
            symbol_table.insert(key)

    return symbol_table


def write_outputs(tokens, errors, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)

    symbol_table = build_symbol_table(tokens)

    # Generate PIF
    with (out_dir / "pif.txt").open(
        "w", encoding="utf-8"
    ) as f:

        f.write(
            "TOKEN_CODE\tTOKEN\tST_POSITION\tLINE\tCOLUMN\n"
        )

        for token in tokens:
            if token["category"] in ("IDENTIFIER", "CONSTANT"):
                key = (token["category"], token["lexeme"])
                st_position = symbol_table.get(key)
            else:
                st_position = (-1, -1)

            f.write(
                f'{token["code"]}\t'
                f'{token["lexeme"]}\t'
                f'{st_position}\t'
                f'{token["line"]}\t'
                f'{token["column"]}\n'
            )

    # Generate Symbol Table
    with (out_dir / "st.txt").open(
        "w", encoding="utf-8"
    ) as f:

        f.write(
            "BUCKET\tPOSITION_IN_BUCKET\tCATEGORY\tLEXEME\n"
        )

        for bucket_index, position, key in symbol_table.get_entries():
            category, lexeme = key

            f.write(
                f"{bucket_index}\t"
                f"{position}\t"
                f"{category}\t"
                f"{lexeme}\n"
            )

    # Generate lexical errors
    with (out_dir / "errors.txt").open(
        "w", encoding="utf-8"
    ) as f:

        if not errors:
            f.write("No lexical errors.\n")
        else:
            for ln, cl, message in errors:
                f.write(
                    f"Line {ln}, column {cl}: {message}\n"
                )

    # Generate tokens
    with (out_dir / "tokens.txt").open(
        "w", encoding="utf-8"
    ) as f:

        for token in tokens:
            f.write(
                f'{token["category"]}\t'
                f'{token["lexeme"]}\t'
                f'{token["line"]}\t'
                f'{token["column"]}\n'
            )


def main():
    parser = argparse.ArgumentParser(
        description="FA-based lexer for Travel Plan DSL"
    )

    parser.add_argument(
        "source",
        help="Source text file (.txt)"
    )

    parser.add_argument(
        "--out",
        default="output",
        help="Output directory"
    )

    args = parser.parse_args()

    source_path = Path(args.source)
    out_dir = Path(args.out)

    source = source_path.read_text(encoding="utf-8")

    tokens, errors = lex(source)

    write_outputs(tokens, errors, out_dir)

    print(f"Tokens recognized: {len(tokens)}")
    print(f"Lexical errors: {len(errors)}")
    print(f"Output files written to: {out_dir.resolve()}")
    print("  pif.txt, st.txt, errors.txt, tokens.txt")


if __name__ == "__main__":
    main()
