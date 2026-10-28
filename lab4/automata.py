from finite_automaton import FiniteAutomaton
import string


LETTERS = set(string.ascii_letters)
DIGITS = set(string.digits)
NONZERO_DIGITS = set("123456789")


def create_identifier_fa():
    states = {"q0", "q1"}
    alphabet = LETTERS | DIGITS | {"_"}
    transitions = {}

    for letter in LETTERS:
        transitions[("q0", letter)] = {"q1"}

    for character in alphabet:
        transitions[("q1", character)] = {"q1"}

    return FiniteAutomaton(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state="q0",
        final_states={"q1"}
    )


def create_integer_fa():
    states = {"q0", "q1", "q2"}
    alphabet = DIGITS
    transitions = {}

    transitions[("q0", "0")] = {"q1"}

    for digit in NONZERO_DIGITS:
        transitions[("q0", digit)] = {"q2"}

    for digit in DIGITS:
        transitions[("q2", digit)] = {"q2"}

    return FiniteAutomaton(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state="q0",
        final_states={"q1", "q2"}
    )


def create_decimal_fa():
    states = {"q0", "q1", "q2", "q3", "q4"}
    alphabet = DIGITS | {"."}
    transitions = {}

    transitions[("q0", "0")] = {"q1"}

    for digit in NONZERO_DIGITS:
        transitions[("q0", digit)] = {"q2"}

    for digit in DIGITS:
        transitions[("q2", digit)] = {"q2"}

    transitions[("q1", ".")] = {"q3"}
    transitions[("q2", ".")] = {"q3"}

    for digit in DIGITS:
        transitions[("q3", digit)] = {"q4"}
        transitions[("q4", digit)] = {"q4"}

    return FiniteAutomaton(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state="q0",
        final_states={"q4"}
    )

def create_string_fa():
    states = {"q0", "q1", "q2"}

    allowed_characters = LETTERS | DIGITS | {
        " ", "_", "-", ".", ",", "!", "?", ":"
    }

    alphabet = allowed_characters | {'"'}
    transitions = {}

    transitions[("q0", '"')] = {"q1"}

    for character in allowed_characters:
        transitions[("q1", character)] = {"q1"}

    transitions[("q1", '"')] = {"q2"}

    return FiniteAutomaton(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state="q0",
        final_states={"q2"}
    )