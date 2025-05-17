import sys
from collections import defaultdict
from tabulate import tabulate

# --- Colores ANSI ---
def color(s, code): return f"\033[{code}m{s}\033[0m"
RED, GREEN, CYAN, YELLOW, BOLD = '91', '92', '96', '93', '1'

# --- Lectura de gramática ---
def input_grammar():
    n = int(input())
    productions = defaultdict(list)
    non_terminals = []
    for _ in range(n):
        line = input().strip()
        if not line:
            continue
        nt, rhs = line.split("->")
        nt = nt.strip()
        if nt not in non_terminals:
            non_terminals.append(nt)
        # Alternativas separadas por espacios (cada una puede tener | internas)
        alternatives = rhs.strip().split()
        for alt in alternatives:
            for prod in alt.split('|'):
                symbols = [c if c != 'e' else 'ε' for c in prod.strip()]
                if not symbols: symbols = ['ε']
                productions[nt].append(symbols)
    return productions, non_terminals[0]

def get_terminals(productions):
    terms = set()
    for rhss in productions.values():
        for rhs in rhss:
            for sym in rhs:
                if sym != 'ε' and (not sym.isupper()):
                    terms.add(sym)
    terms.discard('$')
    return sorted(terms)

# --- LL(1) ---
class GrammarAnalyzerLL1:
    def __init__(self, productions, start_symbol):
        self.productions = productions
        self.start = start_symbol
        self.non_terminals = set(productions.keys())
        self.terminals = get_terminals(productions)
        self.first = self._first()
        self.follow = self._follow()
        self.table, self.is_ll1 = self._ll1_table()

    def _first(self):
        first = {nt: set() for nt in self.non_terminals}
        for t in self.terminals:
            first[t] = {t}
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for prod in self.productions[nt]:
                    i, add_epsilon = 0, True
                    while i < len(prod) and add_epsilon:
                        sym = prod[i]
                        f = first[sym] if sym in first else {sym}
                        before = len(first[nt])
                        first[nt].update(f - {'ε'})
                        if len(first[nt]) != before:
                            changed = True
                        if 'ε' not in f:
                            add_epsilon = False
                        i += 1
                    if add_epsilon:
                        if 'ε' not in first[nt]:
                            first[nt].add('ε')
                            changed = True
        return first

    def _follow(self):
        follow = {nt: set() for nt in self.non_terminals}
        follow[self.start].add('$')
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for prod in self.productions[nt]:
                    trailer = follow[nt].copy()
                    for sym in reversed(prod):
                        if sym in self.non_terminals:
                            before = len(follow[sym])
                            follow[sym].update(trailer)
                            if len(follow[sym]) != before: changed = True
                            if 'ε' in self.first[sym]:
                                trailer = trailer.union(self.first[sym] - {'ε'})
                            else:
                                trailer = self.first[sym] - {'ε'}
                        else:
                            trailer = {sym}
        return follow

    def _ll1_table(self):
        table = {}
        is_ll1 = True
        for nt in self.non_terminals:
            for prod in self.productions[nt]:
                first_set = set()
                i, all_epsilon = 0, True
                while i < len(prod) and all_epsilon:
                    sym = prod[i]
                    f = self.first[sym] if sym in self.first else {sym}
                    first_set |= (f - {'ε'})
                    if 'ε' not in f: all_epsilon = False
                    i += 1
                for t in first_set:
                    if (nt, t) in table:
                        is_ll1 = False
                    table[(nt, t)] = prod
                if all_epsilon:
                    for t in self.follow[nt]:
                        if (nt, t) in table:
                            is_ll1 = False
                        table[(nt, t)] = prod
        return table, is_ll1

    def parse(self, inp):
        if 'ε' in inp:
            print(color("Error: la cadena de entrada no debe contener 'ε'. Use una cadena vacía si corresponde.", RED))
            return False

        tokens = list(inp.strip()) + ['$']
        stack = ['$', self.start]
        i = 0
        sequence = []  # Secuencia de producciones aplicadas
        trace = []     # Traza de pasos

        print(color(f"\n{'Paso':<4} {'Pila':<20} {'Entrada':<20} {'Producción'}", CYAN))
        paso = 1

        while stack:
            pila_str = ' '.join(reversed(stack))
            entrada_str = ''.join(tokens[i:])
            top = stack.pop()
            cur = tokens[i]
            prod_str = "-"

            if top == cur:
                trace.append((paso, pila_str, entrada_str, prod_str))
                print(f"{paso:<4} {pila_str:<20} {entrada_str:<20} {prod_str}")
                i += 1
                if top == '$':
                    break
            elif top in self.non_terminals:
                prod = self.table.get((top, cur))
                if not prod:
                    print(color(f"Error: No se encontró entrada en la tabla para ({top}, {cur})", RED))
                    print(f"Pila: {color(pila_str, YELLOW)}  Entrada: {color(entrada_str, YELLOW)}")
                    return False
                # Guardar la producción en la secuencia SIEMPRE, incluso si es ε
                sequence.append((top, prod))
                prod_str = f"{top} → {' '.join(prod)}"
                trace.append((paso, pila_str, entrada_str, prod_str))
                print(f"{paso:<4} {pila_str:<20} {entrada_str:<20} {prod_str}")
                if prod != ['ε']:
                    for sym in reversed(prod):
                        stack.append(sym)
            else:
                print(color(f"Error: símbolo en pila '{top}' no coincide con entrada '{cur}'", RED))
                print(f"Pila: {color(pila_str, YELLOW)}  Entrada: {color(entrada_str, YELLOW)}")
                return False
            paso += 1

        # Validación final: pila y entrada deben estar en $
        pila_final = (stack == [])
        entrada_final = (i == len(tokens))
        if pila_final and i == len(tokens):
            print(color("\nLa cadena pertenece al lenguaje.", GREEN))
            print(color("\nSecuencia de producción utilizada:", CYAN))
            for nt, prod in sequence:
                print(color(f"{nt} → {' '.join(prod)}", YELLOW))
            return True
        elif pila_final and i == len(tokens)-1 and tokens[i-1] == '$':
            print(color("\nLa cadena pertenece al lenguaje.", GREEN))
            print(color("\nSecuencia de producción utilizada:", CYAN))
            for nt, prod in sequence:
                print(color(f"{nt} → {' '.join(prod)}", YELLOW))
            return True
        else:
            print(color("Error: la cadena no fue completamente consumida o la pila no está vacía.", RED))
            return False

    # ---------- TABLAS ----------
    def print_productions(self):
        print(color("\n[Producciones]", CYAN))
        for nt in sorted(self.non_terminals):
            prods = []
            for prod in self.productions[nt]:
                prods.append(' '.join(prod) if prod != ['ε'] else "ε")
            print(color(f"{nt} → ", YELLOW) + ' | '.join(prods))

    def print_first_follow(self):
        print(color("\n[FIRST]", CYAN))
        for nt in sorted(self.non_terminals):
            print(color(f"FIRST({nt}): ", YELLOW) + '{' + ', '.join(sorted(self.first[nt])) + '}')
        print(color("\n[FOLLOW]", CYAN))
        for nt in sorted(self.non_terminals):
            print(color(f"FOLLOW({nt}): ", YELLOW) + '{' + ', '.join(sorted(self.follow[nt])) + '}')

    def print_ll1_table(self):
        print(color("\n[TABLA LL(1)]", CYAN))
        col_terms = self.terminals + ['$']
        rows = []
        for nt in sorted(self.non_terminals):
            row = [nt]
            for t in col_terms:
                entry = self.table.get((nt, t))
                if entry:
                    row.append(color(' '.join(entry), GREEN))
                else:
                    row.append('-')
            rows.append(row)
        print(tabulate(rows, headers=['NT'] + col_terms, tablefmt='fancy_grid'))

# --- SLR(1) ---
def closure(items, productions):
    result = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for (nt, rhs, dot) in result:
            if dot < len(rhs):
                B = rhs[dot]
                if B in productions:
                    for prod in productions[B]:
                        item = (B, tuple(prod), 0)
                        if item not in result:
                            new_items.add(item)
        if new_items:
            result |= new_items
            changed = True
    return result

def goto(items, X, productions):
    moved = set()
    for (nt, rhs, dot) in items:
        if dot < len(rhs) and rhs[dot] == X:
            moved.add((nt, rhs, dot+1))
    return closure(moved, productions)

def build_states(productions, start_symbol):
    augmented = f"{start_symbol}'"
    while augmented in productions: augmented += "'"
    all_prods = {augmented: [[start_symbol]]}
    all_prods.update(productions)
    initial = closure({(augmented, tuple(all_prods[augmented][0]), 0)}, all_prods)
    states = [initial]
    transitions = {}
    symbols = set(x for prods in all_prods.values() for prod in prods for x in prod) | set(all_prods.keys())
    while True:
        new_states = []
        for i, state in enumerate(states):
            for X in symbols:
                nxt = goto(state, X, all_prods)
                if nxt and nxt not in states and nxt not in new_states:
                    new_states.append(nxt)
                if nxt:
                    idx = states.index(nxt) if nxt in states else len(states) + new_states.index(nxt)
                    transitions[(i, X)] = idx
        if not new_states:
            break
        states += new_states
    return states, transitions, all_prods, augmented

def compute_first(productions):
    first = {nt: set() for nt in productions}
    for nt in productions:
        for rhs in productions[nt]:
            for sym in rhs:
                if sym not in productions: first[sym] = {sym}
    changed = True
    while changed:
        changed = False
        for nt in productions:
            for rhs in productions[nt]:
                i, add_epsilon = 0, True
                while i < len(rhs) and add_epsilon:
                    sym = rhs[i]
                    f = first.get(sym, {sym})
                    before = len(first[nt])
                    first[nt].update(f - {'ε'})
                    if len(first[nt]) != before: changed = True
                    if 'ε' not in f: add_epsilon = False
                    i += 1
                if add_epsilon:
                    if 'ε' not in first[nt]: first[nt].add('ε'); changed = True
    return first

def compute_follow(productions, first, start_symbol):
    follow = {nt: set() for nt in productions}
    follow[start_symbol].add('$')
    changed = True
    while changed:
        changed = False
        for nt in productions:
            for rhs in productions[nt]:
                trailer = follow[nt].copy()
                for sym in reversed(rhs):
                    if sym in productions:
                        before = len(follow[sym])
                        follow[sym].update(trailer)
                        if len(follow[sym]) != before: changed = True
                        if 'ε' in first[sym]:
                            trailer = trailer.union(first[sym] - {'ε'})
                        else:
                            trailer = first[sym] - {'ε'}
                    else:
                        trailer = {sym}
    return follow

def build_slr_table(productions, start_symbol):
    states, transitions, all_prods, augmented = build_states(productions, start_symbol)
    first = compute_first(all_prods)
    follow = compute_follow(all_prods, first, augmented)
    ACTION = [{} for _ in range(len(states))]
    GOTO = [{} for _ in range(len(states))]
    prod_map = {}
    idx = 0
    prod_list = []
    for nt in all_prods:
        for rhs in all_prods[nt]:
            prod_map[(nt, tuple(rhs))] = idx
            prod_list.append((nt, rhs))
            idx += 1
    conflicts = []
    for i, I in enumerate(states):
        for item in I:
            lhs, rhs, dot = item
            if dot < len(rhs):
                a = rhs[dot]
                if a not in all_prods:
                    j = transitions.get((i, a))
                    if j is not None:
                        if a in ACTION[i]:
                            conflicts.append((i, a, 'shift/shift'))
                        ACTION[i][a] = ('s', j)
            else:
                if lhs == augmented:
                    ACTION[i]['$'] = ('acc',)
                else:
                    prod_idx = prod_map[(lhs, rhs)]
                    for a in follow[lhs]:
                        if a in ACTION[i]:
                            conflicts.append((i, a, 'shift/reduce or reduce/reduce'))
                        ACTION[i][a] = ('r', prod_idx)
        for A in all_prods:
            if A in all_prods:
                j = transitions.get((i, A))
                if j is not None:
                    GOTO[i][A] = j
    is_slr = not conflicts
    return ACTION, GOTO, prod_list, is_slr, states, all_prods

def slr_parse(inp, ACTION, GOTO, prod_list, start_symbol):
    tokens = list(inp.strip()) + ['$']
    stack = [0]
    i = 0
    while True:
        state = stack[-1]
        cur = tokens[i]
        action = ACTION[state].get(cur)
        if not action: return False
        if action[0] == 's':
            stack.append(cur)
            stack.append(action[1])
            i += 1
        elif action[0] == 'r':
            prod = prod_list[action[1]]
            lhs, rhs = prod
            if rhs != ['ε']:
                for _ in range(2*len(rhs)):
                    stack.pop()
            state = stack[-1]
            stack.append(lhs)
            stack.append(GOTO[state][lhs])
        elif action[0] == 'acc':
            return True
        else:
            return False

# --- Pretty print SLR(1) tables ---
def print_slr_tables(ACTION, GOTO, prod_list, all_prods):
    print(color("\n[TABLA ACTION]", CYAN))
    # Filtrar ε y eliminar duplicados en las columnas
    all_syms = sorted(set(sym for a in ACTION for sym in a.keys() if sym != 'ε'))
    rows = []
    for i, a in enumerate(ACTION):
        row = [i]
        for t in all_syms:
            act = a.get(t, '')
            if not act:
                row.append('-')
            elif act[0] == 's':
                row.append(color(f"s{act[1]}", GREEN))
            elif act[0] == 'r':
                lhs, rhs = prod_list[act[1]]
                rhs_str = ' '.join(rhs) if rhs != ['ε'] else 'ε'
                row.append(color(f"r{act[1]}({lhs}→{rhs_str})", YELLOW))
            elif act[0] == 'acc':
                row.append(color("acc", BOLD))
            else:
                row.append(str(act))
        rows.append(row)
    print(tabulate(rows, headers=['st'] + all_syms, tablefmt='fancy_grid'))

    print(color("\n[TABLA GOTO]", CYAN))
    nts = sorted(nt for nt in all_prods if nt.isupper())
    rows = []
    for i, g in enumerate(GOTO):
        row = [i]
        for nt in nts:
            row.append(str(g.get(nt,'-')))
        rows.append(row)
    print(tabulate(rows, headers=['st']+nts, tablefmt='fancy_grid'))

    print(color("\n[PRODUCCIONES] (índices para reduce)", CYAN))
    for i, (lhs, rhs) in enumerate(prod_list):
        rhs_str = ' '.join(rhs) if rhs != ['ε'] else 'ε'
        print(color(f"r{i}: {lhs} → {rhs_str}", YELLOW))

# --- MENÚ DE INTERFAZ ---
def menu(ll1, ACTION, GOTO, prod_list, is_slr, all_prods):
    while True:
        print(color("\n=== Menú de Opciones ===", CYAN))
        print(color("1. Mostrar producciones", YELLOW))
        print(color("2. Mostrar conjuntos FIRST y FOLLOW", YELLOW))
        print(color("3. Mostrar tabla LL(1)", YELLOW))
        print(color("4. Mostrar tablas SLR(1)", YELLOW))
        print(color("5. Probar cadena con LL(1)", YELLOW))
        print(color("6. Probar cadena con SLR(1)", YELLOW))
        print(color("7. Salir", YELLOW))
        opt = input(color("Seleccione una opción [1-7]: ", CYAN)).strip()
        if opt == "1":
            ll1.print_productions()
        elif opt == "2":
            ll1.print_first_follow()
        elif opt == "3":
            ll1.print_ll1_table()
        elif opt == "4":
            print_slr_tables(ACTION, GOTO, prod_list, all_prods)
        elif opt == "5":
            cadena = input(color("Ingrese la cadena a analizar con LL(1): ", CYAN))
            ll1.parse(cadena)
        elif opt == "6":
            cadena = input(color("Ingrese la cadena a analizar con SLR(1): ", CYAN))
            print(color('yes', GREEN) if slr_parse(cadena, ACTION, GOTO, prod_list, ll1.start) else color('no', RED))
        elif opt == "7":
            print(color("Saliendo...", CYAN))
            break
        else:
            print(color("Opción inválida. Intente de nuevo.", RED))

def main():
    productions, start = input_grammar()
    ll1 = GrammarAnalyzerLL1(productions, start)
    ACTION, GOTO, prod_list, is_slr, states, all_prods = build_slr_table(productions, start)
    # --- MENÚ ---
    menu(ll1, ACTION, GOTO, prod_list, is_slr, all_prods)

if __name__ == "__main__":
    main()