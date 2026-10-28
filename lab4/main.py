from automata import (
    create_identifier_fa,
    create_integer_fa,
    create_decimal_fa,
    create_string_fa
)


def test_automaton(name, automaton, examples):
    print(f"\n===== {name} =====")

    print("\nFinite Automaton:")
    print("States:", sorted(automaton.states))
    print("Initial state:", automaton.initial_state)
    print("Final states:", sorted(automaton.final_states))

    print("\nString validation:")

    for example in examples:
        result = automaton.accepts(example)
        status = "ACCEPTED" if result else "REJECTED"
        print(f"  {example!r}: {status}")

    print("\nEquivalent Regular Grammar:")

    grammar = automaton.to_regular_grammar()
    grammar.display()


def main():
    identifier_fa = create_identifier_fa()
    integer_fa = create_integer_fa()
    decimal_fa = create_decimal_fa()
    string_fa = create_string_fa()

    test_automaton(
        "IDENTIFIERS", identifier_fa, ["place", "max_budget", "travel1", "1place", "_place", "place-name"]
    )

    test_automaton("INTEGER CONSTANTS", integer_fa, ["0", "10", "250", "01", "-5", "12a"]
    )

    test_automaton("DECIMAL CONSTANTS", decimal_fa, ["4.7", "0.5", "12.50", "4.", ".5", "04.5"]
    )

    test_automaton("STRING CONSTANTS", string_fa, ['"Paris"', '"New York"', '"Trip 2026"',
                                                   '""', '"Paris', 'Paris"', '"Hello@World"']
    )


if __name__ == "__main__":
    main()