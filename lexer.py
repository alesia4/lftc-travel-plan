
import argparse
import re
from pathlib import Path

KEYWORDS = {
    "destinations", "input", "output", "if", "else", "end",
    "for", "in", "and", "or", "true", "false"
}
TOKEN_CODES = {"KEYWORD": 1, "IDENTIFIER": 2, "CONSTANT": 3, "OPERATOR": 4, "DELIMITER": 5}

TOKEN_RE = re.compile(
    r'(?P<WHITESPACE>[ \t\r\n]+)'
    r'|(?P<COMMENT>\#[^\n]*)'
    r'|(?P<STRING>"(?:[A-Za-z0-9 .,\'-])*")'
    r'|(?P<DECIMAL>(?:0|[1-9][0-9]*)\.[0-9]+)'
    r'|(?P<INTEGER>0|[1-9][0-9]*)'
    r'|(?P<IDENTIFIER>[A-Za-z][A-Za-z0-9_]*)'
    r'|(?P<OPERATOR>==|!=|>=|<=|[=+\-<>?.])'
    r'|(?P<DELIMITER>[()\[\]{},:])'
)

def lex(source):
    tokens, errors = [], []
    pos, line, col = 0, 1, 1
    while pos < len(source):
        match = TOKEN_RE.match(source, pos)
        if not match:
            ch = source[pos]
            if ch == '"':
                end_quote = source.find('"', pos + 1)
                newline = source.find("\n", pos + 1)
                if end_quote == -1 or (newline != -1 and newline < end_quote):
                    errors.append((line, col, "Unterminated string literal"))
                    skip_to = newline if newline != -1 else len(source)
                    col += skip_to - pos
                    pos = skip_to
                    continue
            malformed = re.match(r"[0-9]+(?:\.[0-9]*)?[A-Za-z_][A-Za-z0-9_]*", source[pos:])
            if malformed:
                bad = malformed.group()
                errors.append((line, col, f"Malformed numeric token {bad!r}"))
                pos += len(bad)
                col += len(bad)
                continue
            errors.append((line, col, f"Invalid character {ch!r}"))
            if ch == "\n":
                line, col = line + 1, 1
            else:
                col += 1
            pos += 1
            continue

        kind, lexeme = match.lastgroup, match.group()
        start_line, start_col = line, col
        newlines = lexeme.count("\n")
        if newlines:
            line += newlines
            col = len(lexeme.rsplit("\n", 1)[-1]) + 1
        else:
            col += len(lexeme)
        pos = match.end()
        if kind in ("WHITESPACE", "COMMENT"):
            continue

        if kind == "IDENTIFIER":
            category = "KEYWORD" if lexeme in KEYWORDS else "IDENTIFIER"
        elif kind in ("STRING", "INTEGER", "DECIMAL"):
            category = "CONSTANT"
        elif kind == "OPERATOR":
            category = "OPERATOR"
        else:
            category = "DELIMITER"

        tokens.append({
            "category": category, "lexeme": lexeme,
            "line": start_line, "column": start_col,
            "code": TOKEN_CODES[category]
        })
    return tokens, errors

def build_symbol_table(tokens):
    positions = {}
    entries = []
    for token in tokens:
        if token["category"] not in ("IDENTIFIER", "CONSTANT"):
            continue
        key = (token["category"], token["lexeme"])
        if key not in positions:
            position = len(entries)
            positions[key] = position
            entries.append({
                "position": position,
                "category": token["category"],
                "lexeme": token["lexeme"]
            })
    return positions, entries

def write_outputs(tokens, errors, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    positions, entries = build_symbol_table(tokens)

    with (out_dir / "pif.txt").open("w", encoding="utf-8") as f:
        f.write("TOKEN_CODE\tTOKEN\tST_POSITION\tLINE\tCOLUMN\n")
        for token in tokens:
            key = (token["category"], token["lexeme"])
            st_position = positions[key] if token["category"] in ("IDENTIFIER", "CONSTANT") else -1
            f.write(f'{token["code"]}\t{token["lexeme"]}\t{st_position}\t{token["line"]}\t{token["column"]}\n')

    with (out_dir / "st.txt").open("w", encoding="utf-8") as f:
        f.write("POSITION\tCATEGORY\tLEXEME\n")
        for entry in entries:
            f.write(f'{entry["position"]}\t{entry["category"]}\t{entry["lexeme"]}\n')

    with (out_dir / "errors.txt").open("w", encoding="utf-8") as f:
        if not errors:
            f.write("No lexical errors.\n")
        else:
            for ln, cl, message in errors:
                f.write(f"Line {ln}, column {cl}: {message}\n")

    with (out_dir / "tokens.txt").open("w", encoding="utf-8") as f:
        for token in tokens:
            f.write(f'{token["category"]}\t{token["lexeme"]}\t{token["line"]}\t{token["column"]}\n')

def main():
    parser = argparse.ArgumentParser(description="Regex-based lexer for Travel Plan DSL")
    parser.add_argument("source", help="source text file (.txt)")
    parser.add_argument("--out", default="output", help="Output directory (default: output)")
    args = parser.parse_args()
    source_path, out_dir = Path(args.source), Path(args.out)
    tokens, errors = lex(source_path.read_text(encoding="utf-8"))
    write_outputs(tokens, errors, out_dir)
    print(f"Tokens recognized: {len(tokens)}")
    print(f"Lexical errors: {len(errors)}")
    print(f"Output files written to: {out_dir.resolve()}")
    print("  pif.txt, st.txt, errors.txt, tokens.txt")

if __name__ == "__main__":
    main()
