from collections import defaultdict
from tabulate import tabulate
from grammar_utils import compute_terminals, compute_first, compute_follow, print_first_follow, print_grammar
from table_utils import create_fancy_table, TableColors, color_text


class SyntaxAnalyzer:  # antes era SLRParser
    def __init__(self, productions, start_symbol):
        self.productions = {k: [tuple(p) for p in v] for k, v in productions.items()}
        self.original_start_symbol = start_symbol
        self.start_symbol = start_symbol
        self.non_terminals = set(self.productions.keys())
        self.terminals = compute_terminals(self.productions, self.non_terminals)  
        self._augment_grammar()
        self.states = []
        self.transitions = {}
        self._build_states()
        self.first = compute_first(self.productions, self.non_terminals)         
        self.follow = compute_follow(self.productions, self.non_terminals, self.start_symbol, self.first)

    def _augment_grammar(self):
        augmented_start = self.start_symbol + "'"
        self.productions[augmented_start] = [(self.start_symbol,)]
        self.start_symbol = augmented_start
        self.non_terminals.add(augmented_start)

    def _closure(self, items):
        closure_set = set(items)
        added = True
        while added:
            added = False
            new_items = set()
            for lhs, rhs, dot in closure_set:
                if dot < len(rhs):
                    symbol = rhs[dot]
                    if symbol in self.non_terminals:
                        for prod in self.productions[symbol]:
                            item = (symbol, prod, 0)
                            if item not in closure_set:
                                new_items.add(item)
            if new_items:
                closure_set.update(new_items)
                added = True
        return frozenset(closure_set)

    def _goto(self, state, symbol):
        goto_set = set()
        for lhs, rhs, dot in state:
            if dot < len(rhs) and rhs[dot] == symbol:
                goto_set.add((lhs, rhs, dot + 1))
        return self._closure(goto_set) if goto_set else None

    def _build_states(self):
        start_item = (self.start_symbol, self.productions[self.start_symbol][0], 0)
        start_closure = self._closure({start_item})
        self.states.append(start_closure)
        state_map = {start_closure: 0}

        i = 0
        while i < len(self.states):
            state = self.states[i]
            symbols = {rhs[dot] for (lhs, rhs, dot) in state if dot < len(rhs)}

            for symbol in symbols:
                next_state = self._goto(state, symbol)
                if next_state:
                    if next_state not in state_map:
                        self.states.append(next_state)
                        state_map[next_state] = len(self.states) - 1
                    self.transitions[(i, symbol)] = state_map[next_state]
            i += 1

    def print_states(self):
        print("\n" + color_text("STATES", TableColors.YELLOW, bold=True))
        state_data = []
        for idx, state in enumerate(self.states):
            state_items = []
            for lhs, rhs, dot in state:
                before_dot = ' '.join(rhs[:dot])
                after_dot = ' '.join(rhs[dot:])
                state_items.append(f"{lhs} → {before_dot} • {after_dot}")
            state_data.append([f"State {idx}", '\n'.join(state_items)])
        
        print(create_fancy_table(state_data, ["State", "Items"], "STATE INFORMATION"))

    def _get_prod_number(self, lhs, rhs):
        index = 1
        for nt, prods in self.productions.items():
            for prod in prods:
                if nt == lhs and prod == rhs:
                    return index
                index += 1
        raise ValueError(f"Production not found for {lhs} -> {rhs}")

    def print_reductions(self):
        reductions = []
        for state_id, state in enumerate(self.states):
            for lhs, rhs, dot in state:
                if dot == len(rhs) and lhs != self.start_symbol:
                    prod_num = self._get_prod_number(lhs, rhs)
                    reductions.append([
                        state_id,
                        f"{lhs} → {' '.join(rhs)}",
                        f"r{prod_num}"
                    ])
        
        print("\n" + create_fancy_table(reductions, 
                                      ["State", "Production", "Reduction"],
                                      "REDUCTION INFORMATION"))

    def build_slr_table(self):
        table = {}
        for state_id, state in enumerate(self.states):
            table[state_id] = {}

            #Shift and GO_TO
            for (src, symbol), tgt in self.transitions.items():
                if src == state_id:
                    if symbol in self.terminals:
                        table[state_id][symbol] = f"s{tgt}"
                    elif symbol in self.non_terminals:
                        table[state_id][symbol] = f"{tgt}"

            #Direct reductions
            for lhs, rhs, dot in state:
                if dot == len(rhs):
                    if lhs == self.start_symbol:
                        table[state_id]['$'] = 'acc'
                        continue
                    prod_num = self._get_prod_number(lhs, rhs)
                    for follow_sym in self.follow[lhs]:
                        if follow_sym not in table[state_id]:
                            table[state_id][follow_sym] = f"r{prod_num}"

            #Reductions by empty: if a non-terminal symbol with production ε is expected
            for lhs, rhs, dot in state:
                if dot < len(rhs):
                    next_symbol = rhs[dot]
                    if next_symbol in self.non_terminals:
                        for prod in self.productions[next_symbol]:
                            if prod == ('e',):  # Si next_symbol → ε
                                prod_num = self._get_prod_number(next_symbol, prod)
                                for follow_sym in self.follow[next_symbol]:
                                    if follow_sym not in table[state_id]:
                                        table[state_id][follow_sym] = f"r{prod_num}"
        return table

    def is_slr1(self):
        table = self.build_slr_table()
        conflicts = []

        for state_id, state in enumerate(self.states):
            #Check for shift-reduce and reduce-reduce conflicts
            shift_symbols = set()
            reduce_symbols = defaultdict(list)

            #Search for displacement and reduction actions in the current state
            for lhs, rhs, dot in state:
                if dot < len(rhs):  # Ítem con punto antes del final
                    next_symbol = rhs[dot]
                    if next_symbol in self.terminals:
                        shift_symbols.add(next_symbol)
                else:  # Ítem de reducción
                    if lhs != self.start_symbol:
                        prod_num = self._get_prod_number(lhs, rhs)
                        for follow_sym in self.follow[lhs]:
                            reduce_symbols[follow_sym].append((lhs, rhs, prod_num))

            #Check shift-reduce conflicts
            for sym in shift_symbols:
                if sym in reduce_symbols:
                    conflicts.append(
                        f"Shift-reduce conflict in state {state_id} for the symbol '{sym}': "
                        f"It can be moved or reduced with {reduce_symbols[sym]}"
                    )

            #Check reduce-reduce conflicts
            for sym, prods in reduce_symbols.items():
                if len(prods) > 1:
                    conflicts.append(
                        f"Reduce-reduce conflict in state {state_id} for the symbol '{sym}': "
                        f"Multiple reductions possible: {prods}"
                    )

        if not conflicts:
            print("✅ The grammar is SLR(1) (no conflicts).")
            return True
        else:
            print("❌ The grammar is NOT SLR(1) due to the following conflicts:")
            for conflict in conflicts:
                print(f"  - {conflict}")
            return False

    def print_slr_table(self):
        table = self.build_slr_table()
        headers = ["State"] + list(sorted((self.terminals | self.non_terminals | {'$'}) - {self.start_symbol}))
        rows = []
        for state_id, actions in sorted(table.items()):
            row = [state_id] + [actions.get(sym, "") for sym in headers[1:]]
            rows.append(row)
        print("\n" + create_fancy_table(rows, headers, "SLR PARSING TABLE"))

    
    def validate_input(self, input_string):
        table = self.build_slr_table()
        stack = [0]  # Stack de estados
        symbols = []  # Stack de símbolos
        input_string += '$'
        pointer = 0
        
        steps = []
        print(f"\n{color_text('Analyzing Input:', TableColors.BLUE, bold=True)} {color_text(input_string[:-1], TableColors.CYAN)}")
        
        while True:
            state = stack[-1]
            current = input_string[pointer]
            
            # Formar la representación del stack para mostrar
            stack_symbols = ''.join(symbols)
            stack_str = f"{stack_symbols} {state}"
            
            action = table.get(state, {}).get(current, '')
            steps.append([
                color_text(str(len(steps)+1), TableColors.MAGENTA),
                color_text(stack_str, TableColors.CYAN),
                color_text(input_string[pointer:], TableColors.GREEN),
                color_text(action, TableColors.YELLOW)
            ])
            
            if not action:
                print(create_fancy_table(steps, 
                    ["STEP", "STACK", "INPUT", "ACTION"], 
                    "PARSING STEPS"))
                print(f"\n{color_text('❌ NO', TableColors.RED, bold=True)} - Syntax Error")
                return False
                
            if action == 'acc':
                print(create_fancy_table(steps, 
                    ["STEP", "STACK", "INPUT", "ACTION"], 
                    "PARSING STEPS"))
                print(f"\n{color_text('✓ YES', TableColors.GREEN, bold=True)} - Input Accepted")
                return True
                
            if action.startswith('s'):  # Shift
                next_state = int(action[1:])
                stack.append(next_state)
                symbols.append(current)
                pointer += 1
                
            elif action.startswith('r'):  # Reduce
                prod_num = int(action[1:])
                # Encontrar la producción correspondiente
                found = False
                for nt, prods in self.productions.items():
                    for prod in prods:
                        prod_num -= 1
                        if prod_num == 0:
                            # Reducir usando esta producción
                            if prod != ('e',):
                                for _ in range(len(prod)):
                                    stack.pop()
                                    symbols.pop()
                            # Ir al siguiente estado
                            goto_state = table[stack[-1]].get(nt, '')
                            if goto_state:
                                stack.append(int(goto_state))
                                symbols.append(nt)
                            found = True
                            break
                    if found:
                        break

def load_grammar(file):
    with open(file) as f:
        lines = [l.strip() for l in f if l.strip()]

    num_rules = int(lines[0])
    prods = defaultdict(list)
    start = None

    for i in range(1, num_rules + 1):
        if '->' in lines[i]:
            lhs, rhs = lines[i].split('->')
            lhs = lhs.strip()
            rhs_parts = rhs.strip().split()  #Separation by spaces

            for alt in rhs_parts:
                if alt == 'e':
                    prods[lhs].append(('e',))
                else:
                    filtered = alt.replace('e', '')
                    if filtered:  
                        prods[lhs].append(tuple(filtered))
                    else:  
                        prods[lhs].append(('e',))

            if start is None:
                start = lhs

    input_strings = lines[num_rules + 1:]
    return prods, start, input_strings

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python S.py g.txt")
        sys.exit(1)

    prods, start, cadenas = load_grammar(sys.argv[1])
    parser = SyntaxAnalyzer(prods, start)
    print_grammar(parser.productions)
    parser.print_states()
    print_first_follow(parser.productions, parser.non_terminals, parser.start_symbol)
    parser.print_slr_table()
    parser.print_reductions()
    parser.is_slr1()  

    print(f"\nStrings to parse from the file: {cadenas}")
    for cadena in cadenas:
        parser.validate_input(cadena)