from collections import defaultdict


def compute_terminals(productions, non_terminals):
    terminals = set()
    for rhs_list in productions.values():
        for rhs in rhs_list:
            for symbol in rhs:
                if symbol != 'e' and symbol not in non_terminals:
                    if symbol == 'e':
                        raise ValueError("Error: 'e' is not allowed as a terminal symbol")
                    terminals.add(symbol)
    return terminals


def compute_first(productions, non_terminals):
    first = {nt: set() for nt in non_terminals}
    for nt in non_terminals:
        for prod in productions[nt]:
            if prod == ['e'] or prod == ('e',):
                first[nt].add('e')

    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            for prod in productions[nt]:
                i, can_derive_e = 0, True
                while i < len(prod) and can_derive_e:
                    symbol = prod[i]
                    if symbol in non_terminals:
                        before = len(first[nt])
                        first[nt].update(first[symbol] - {'e'})
                        changed |= len(first[nt]) != before
                        can_derive_e = 'e' in first[symbol]
                    else:
                        before = len(first[nt])
                        if symbol != 'e':
                            first[nt].add(symbol)
                        changed |= len(first[nt]) != before
                        can_derive_e = False
                    i += 1
                if can_derive_e and i == len(prod):
                    before = len(first[nt])
                    first[nt].add('e')
                    changed |= len(first[nt]) != before
    return first


def compute_follow(productions, non_terminals, start_symbol, first):
    follow = {nt: set() for nt in non_terminals}
    follow[start_symbol].add('$')

    changed = True
    while changed:
        changed = False
        for nt in non_terminals:
            for prod in productions[nt]:
                # For each symbol in the output
                for i, symbol in enumerate(prod):
                    if symbol in non_terminals:
                        # Get the rest of the output after this symbol
                        rest = prod[i + 1:]

                        if rest:
                            # There are symbols after, calculate FIRST from the remainder
                            j = 0
                            all_derive_epsilon = True

                            while j < len(rest) and all_derive_epsilon:
                                next_symbol = rest[j]
                                if next_symbol in non_terminals:
                                    # Add FIRST(next_symbol) - {e} to FOLLOW(symbol)
                                    before = len(follow[symbol])
                                    follow[symbol].update(first[next_symbol] - {'e'})
                                    if len(follow[symbol]) != before:
                                        changed = True
                                    # If next_symbol cannot derive epsilon, stop
                                    if 'e' not in first[next_symbol]:
                                        all_derive_epsilon = False
                                else:
                                    # It is a terminal, add it to FOLLOW(symbol)
                                    if next_symbol != 'e':
                                        before = len(follow[symbol])
                                        follow[symbol].add(next_symbol)
                                        if len(follow[symbol]) != before:
                                            changed = True
                                    all_derive_epsilon = False
                                j += 1

                            # If all the following symbols can derive epsilon
                            if all_derive_epsilon:
                                before = len(follow[symbol])
                                follow[symbol].update(follow[nt])
                                if len(follow[symbol]) != before:
                                    changed = True
                        else:
                            # No symbols after, add FOLLOW(nt)
                            before = len(follow[symbol])
                            follow[symbol].update(follow[nt])
                            if len(follow[symbol]) != before:
                                changed = True
    return follow

def print_grammar(productions):
    print("\n***** GRAMMAR *****")
    for nt in sorted(productions.keys()):
        rules = []
        for prod in productions[nt]:
            if isinstance(prod, tuple):
                rules.append(' '.join(prod) if prod != ('e',) else 'e')
            else:
                rules.append(' '.join(prod) if prod != ['e'] else 'e')
        print(f"{nt} → {' '.join(rules)}")


def print_first_follow(productions, non_terminals, start_symbol):
    first = compute_first(productions, non_terminals)
    follow = compute_follow(productions, non_terminals, start_symbol, first)
    print("\nFIRST SETS:")
    for nt in sorted(non_terminals):
        print(f"  FIRST({nt}) = {sorted(first[nt])}")
    print("\nFOLLOW SETS:")
    for nt in sorted(non_terminals):
        print(f"  FOLLOW({nt}) = {sorted(follow[nt])}")