import sys
from collections import defaultdict
from tabulate import tabulate
from grammar_utils import compute_terminals, compute_first, compute_follow,  print_first_follow, print_grammar
from table_utils import create_fancy_table, TableColors, color_text

class LL1Analyzer:  # antes era GrammarAnalyzer
    def __init__(self, productions, start_symbol):
        self.productions = productions
        self.start_symbol = start_symbol
        self.non_terminals = set(productions.keys())
        self.terminals = compute_terminals(productions, self.non_terminals)  
        self.first = compute_first(productions, self.non_terminals)         
        self.follow = compute_follow(productions, self.non_terminals, start_symbol, self.first) 
        self.ll1_table = self._build_ll1_table()

    def is_ll1_grammar(self):
        """
        Checks if the grammar is LL(1) by identifying:
        1. Intersecting FIRST sets for productions of the same non-terminal
        2. Immediate left recursion

        Returns:
            tuple: (is_ll1, issues_found)
                - is_ll1: Boolean indicating if the grammar is LL(1)
                - issues_found: List of specific issues found
        """
        issues = []

        # Check for immediate left recursion
        for nt, productions in self.productions.items():
            for prod in productions:
                if prod and prod[0] == nt:
                    issues.append(f"Immediate left recursion found: {nt} → {' '.join(prod)}")

        # Check for FIRST set conflicts
        for nt in self.non_terminals:
            # Track which terminals are already seen for each production
            first_sets_by_prod = []

            for prod in self.productions[nt]:
                # Compute FIRST set for this production
                prod_first = set()

                # If empty production, include FOLLOW set
                if prod == ['e']:
                    continue  # We'll handle this separately

                # Calculate FIRST set for this production
                all_derive_epsilon = True
                for symbol in prod:
                    if symbol in self.non_terminals:
                        prod_first.update(self.first[symbol] - {'e'})
                        if 'e' not in self.first[symbol]:
                            all_derive_epsilon = False
                            break
                    else:  # Terminal symbol
                        prod_first.add(symbol)
                        all_derive_epsilon = False
                        break

                # If all symbols can derive epsilon, add epsilon to FIRST set
                if all_derive_epsilon:
                    prod_first.add('e')

                # Check for conflicts with previous productions
                for idx, previous_first in enumerate(first_sets_by_prod):
                    intersection = prod_first.intersection(previous_first)
                    if intersection:
                        previous_prod = self.productions[nt][idx]
                        issues.append(
                            f"FIRST set conflict for {nt}: Productions '{' '.join(previous_prod)}' and '{' '.join(prod)}' share terminals {intersection}")

                # Add this production's FIRST set to the list
                first_sets_by_prod.append(prod_first)

            # Special handling for epsilon productions
            epsilon_productions = [i for i, prod in enumerate(self.productions[nt]) if prod == ['e']]
            if epsilon_productions:
                for other_idx, other_first in enumerate(first_sets_by_prod):
                    if other_idx not in epsilon_productions:  # Skip comparing epsilon production with itself
                        follow_intersection = self.follow[nt].intersection(other_first)
                        if follow_intersection:
                            other_prod = self.productions[nt][other_idx]
                            issues.append(
                                f"Conflict between epsilon production and '{' '.join(other_prod)}' for {nt}: FOLLOW({nt}) and FIRST({' '.join(other_prod)}) share terminals {follow_intersection}")

        return len(issues) == 0, issues

    def _build_ll1_table(self):
        is_ll1, issues = self.is_ll1_grammar()
        if not is_ll1:
            return {}  # Return empty table
        table = {}
        for nt in self.non_terminals:
            for prod in self.productions[nt]:
                if prod == ['e']:
                    for follow_sym in self.follow[nt]:
                        table[(nt, follow_sym)] = prod
                    continue

                first_set = set()
                all_eps = True
                for sym in prod:
                    if sym in self.non_terminals:
                        first_set.update(self.first[sym] - {'e'})
                        if 'e' not in self.first[sym]:
                            all_eps = False
                            break
                    else:
                        first_set.add(sym if sym != 'e' else '')
                        all_eps = False
                        break

                for term in first_set:
                    if term: table[(nt, term)] = prod

                if all_eps:
                    for follow_sym in self.follow[nt]:
                        table[(nt, follow_sym)] = prod
        return table

    def validate_string(self, input_string):
        if not self.ll1_table:
            return False, "Grammar not LL(1)", []

        tokens = list(input_string.strip())
        tokens.append('$')
        stack = ['$', self.start_symbol]
        idx = 0
        steps = []

        while stack:
            top = stack[-1]
            current = tokens[idx]
            steps.append([
                color_text(str(len(steps)+1), TableColors.MAGENTA),
                color_text(' '.join(stack[::-1]), TableColors.CYAN),
                color_text(' '.join(tokens[idx:]), TableColors.GREEN)
            ])

            if top == current:
                stack.pop()
                idx += 1
            elif top in self.non_terminals and (top, current) in self.ll1_table:
                prod = self.ll1_table[(top, current)]
                stack.pop()
                if prod != ['e']:
                    stack.extend(reversed(prod))
            else:
                print(create_fancy_table(steps, 
                    ["STEP", "STACK", "INPUT"], 
                    "VALIDATION PROCESS"))
                print(f"\n{color_text('❌ NO', TableColors.RED, bold=True)} - Input Rejected")
                return False, "Syntax Error", steps

        print(create_fancy_table(steps, 
            ["STEP", "STACK", "INPUT"], 
            "VALIDATION PROCESS"))
        if idx >= len(tokens):
            print(f"\n{color_text('✓ YES', TableColors.GREEN, bold=True)} - Input Accepted")
            return True, "Valid Input", steps
        else:
            print(f"\n{color_text('❌ NO', TableColors.RED, bold=True)} - Input Rejected")
            return False, "Invalid Input", steps

def load_grammar(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    num_nt = int(lines[0])
    prods = defaultdict(list)
    start_symbol = None

    #First look for 'S' as the initial symbol
    for line in lines[1:num_nt+1]:
        if '->' in line:
            left = line.split('->')[0].strip()
            if left == 'S':
                start_symbol = 'S'
                break

   #If no 'S' was found, use the first one as before
    if start_symbol is None:
        for line in lines[1:num_nt+1]:
            if '->' in line:
                start_symbol = line.split('->')[0].strip()
                break

    for line in lines[1:num_nt+1]:
        if '->' not in line: continue
        left, right = line.split('->')
        left = left.strip()

        for alt in right.strip().split('|'):
            alt = alt.strip()
            parts = []
            token = []
            in_quote = False
            i = 0

            while i < len(alt):
                char = alt[i]
                if char == "'" and not in_quote:
                    in_quote = True
                    token.append(char)
                elif char == "'" and in_quote:
                    token.append(char)
                    parts.append(''.join(token))
                    token = []
                    in_quote = False
                elif char == ' ' and not in_quote:
                    if token:
                        parts.append(''.join(token))
                        token = []
                    if parts:
                        prods[left].append(parts)
                        parts = []
                elif in_quote:
                    token.append(char)
                else:
                    parts.append(char)
                i += 1

            if token: parts.append(''.join(token))
            if parts:
                # Handle the case when 'e' is alone in the production
                if len(parts) == 1 and parts[0] == 'e':
                    prods[left].append(['e'])
                else:
                    # Remove 'e' from the production if it appears with other symbols
                    filtered_parts = [p for p in parts if p != 'e']
                    # Only add the production if there are symbols left after filtering
                    if filtered_parts:
                        prods[left].append(filtered_parts)
                    else:
                        # If all symbols were 'e', add a single 'e' production
                        prods[left].append(['e'])

    test_strings = lines[num_nt+1:]
    return prods, start_symbol, test_strings

def print_info(analyzer):
    print("\n" + color_text("═"*50, TableColors.BLUE))
    print(color_text("GRAMMAR ANALYSIS", TableColors.YELLOW, bold=True))
    print(color_text("═"*50, TableColors.BLUE))
    
    grammar_data = []
    for nt in sorted(analyzer.productions.keys()):
        rules = []
        for prod in analyzer.productions[nt]:
            if prod == ['e']:
                rules.append('ε')
            else:
                rules.append(' '.join(prod))
        grammar_data.append([nt, '|'.join(rules)])
    
    print(create_fancy_table(grammar_data, ["Non-Terminal", "Productions"], "GRAMMAR RULES"))

    if analyzer.ll1_table:
        all_terms = sorted(analyzer.terminals) + ['$']
        table_data = []
        for nt in sorted(analyzer.non_terminals):
            row = [color_text(nt, TableColors.MAGENTA)]
            for t in all_terms:
                key = (nt, t)
                if key in analyzer.ll1_table:
                    prod = analyzer.ll1_table[key]
                    prod_str = 'ε' if prod == ['e'] else ' '.join(prod)
                    row.append(color_text(f"{nt} → {prod_str}", TableColors.GREEN))
                else:
                    row.append(color_text("-", TableColors.RED))
            table_data.append(row)
        
        print("\n" + create_fancy_table(table_data,
            [color_text("NT", TableColors.CYAN, bold=True)] + 
            [color_text(t, TableColors.BLUE, bold=True) for t in all_terms],
            "LL(1) PARSING TABLE"))

def print_parse_steps(steps):
    print("\n" + create_fancy_table(
        steps,
        ["STEP", "STACK", "INPUT"],
        "PARSING STEPS"
    ))

def main():
    if len(sys.argv) != 2:
        print("Uso: python grammar_analyzer.py <archivo_gramatica>")
        return

    try:
        prods, start, test_strings = load_grammar(sys.argv[1])
        analyzer = LL1Analyzer(prods, start)

        print_info(analyzer)

        if analyzer.ll1_table:
            print("\n***** STRING ANALYSIS *****")
            for string in test_strings:
                if not string.strip(): continue
                print(f"\nString: '{string}'")
                valid, msg, steps = analyzer.validate_string(string)
                print("\nAnalysis steps:")
                print_parse_steps(steps)
                print(f"\nResult: {msg}")
        else:
            print("\nThe grammar is not LL(1) due to conflicts")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()