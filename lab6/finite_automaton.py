class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, initial_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

    def accepts(self, sequence):
        current_states = {self.initial_state}

        for character in sequence:
            if character not in self.alphabet:
                return False

            next_states = set()

            for state in current_states:
                destinations = self.transitions.get((state, character), set())
                next_states.update(destinations)

            if not next_states:
                return False

            current_states = next_states

        return bool(current_states.intersection(self.final_states))

    def to_regular_grammar(self):
        productions = {state: [] for state in self.states}

        for (source, symbol), destinations in self.transitions.items():
            for destination in sorted(destinations):
                productions[source].append(f"{symbol}{destination}")

        for state in self.final_states:
            productions[state].append("ε")

        return RegularGrammar(
            nonterminals=self.states,
            terminals=self.alphabet,
            productions=productions,
            start_symbol=self.initial_state
        )


class RegularGrammar:
    def __init__(self, nonterminals, terminals, productions, start_symbol):
        self.nonterminals = nonterminals
        self.terminals = terminals
        self.productions = productions
        self.start_symbol = start_symbol

    def display(self):
        print("Start symbol:", self.start_symbol)
        print("Productions:")

        for nonterminal in sorted(self.productions):
            rules = self.productions[nonterminal]

            if rules:
                print(f"  {nonterminal} -> {' | '.join(sorted(rules))}")