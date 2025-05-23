import sys
import io
from F import LL1Analyzer, load_grammar as ll1_load_grammar
from S import SyntaxAnalyzer, load_grammar as slr_load_grammar
from table_utils import create_fancy_table, TableColors, color_text, create_result_box



def main(grammar_file):
    # First try to load with F (LL1)
    try:
        ll1_prods, ll1_start_symbol, ll1_test_strings = ll1_load_grammar(grammar_file)
        analyzer = LL1Analyzer(ll1_prods, ll1_start_symbol)

        # Temporarily suppress standard output
        orig_stdout = sys.stdout
        sys.stdout = io.StringIO()

        # Check if it is LL(1)
        is_ll1, issues = analyzer.is_ll1_grammar()

        # Restore standard output
        sys.stdout = orig_stdout

        # Now we control the message
        if is_ll1:
            print(color_text("✓ Grammar is LL(1) - No conflicts found", TableColors.GREEN, bold=True))
        else:
            print(color_text("❌ Grammar is NOT LL(1)", TableColors.RED, bold=True))
            for issue in issues:
                print(f"  ▶ {issue}")
    except Exception as e:
        print(color_text(f"Error loading grammar for LL(1): {str(e)}", TableColors.RED))
        is_ll1 = False

    # Then try with S (SLR)
    try:
        slr_prods, slr_start_symbol, slr_test_strings = slr_load_grammar(grammar_file)
        orig_stdout = sys.stdout
        sys.stdout = io.StringIO()

        # Create the SLR parser
        slr_parser = SyntaxAnalyzer(slr_prods, slr_start_symbol)
        is_slr1 = slr_parser.is_slr1()

        result = sys.stdout.getvalue()
        sys.stdout = orig_stdout

        if not is_slr1:
            print(color_text("❌ Grammar is NOT SLR(1)", TableColors.RED, bold=True))
            conflict_lines = [line for line in result.split('\n') if line.startswith("  - ")]
            for line in conflict_lines:
                print(f"  ▶ {line[4:]}")
        else:
            print(color_text("✓ Grammar is SLR(1) - No conflicts found", TableColors.GREEN, bold=True))
    except Exception as e:
        print(color_text(f"Error loading grammar for SLR: {str(e)}", TableColors.RED))
        is_slr1 = False

    if is_ll1 and is_slr1:
        print("\n" + color_text("═"*50, TableColors.BLUE))
        print(color_text("Grammar is both LL(1) and SLR(1)", TableColors.YELLOW, bold=True))
        print(color_text("═"*50, TableColors.BLUE) + "\n")

        while True:
            print(create_fancy_table([
                ["T", "Use LL(1) Parser"],
                ["B", "Use SLR(1) Parser"],
                ["Q", "Quit Program"]
            ], ["Option", "Action"], "Parser Selection"))
            
            mode = input("\nSelect parser type (T/B/Q): ").strip().upper()
            if mode in {'Q', 'T', 'B'}:
                break
            print(color_text("Invalid option! Try again.", TableColors.RED))

        if mode == 'Q':
            return

        if mode == 'T':
            print("\n" + color_text("LL(1) PARSER EXECUTION", TableColors.CYAN, bold=True))
            from F import print_info as ll1_print_info
            ll1_print_info(analyzer)

            print("\n" + color_text("STRING ANALYSIS", TableColors.YELLOW, bold=True))
            for string in ll1_test_strings:
                if not string.strip(): continue
                print(f"\nInput: {color_text(string, TableColors.CYAN)}")
                valid, msg, steps = analyzer.validate_string(string.strip())
                create_result_box(valid, msg)

        else:
            print("\n" + color_text("SLR(1) PARSER EXECUTION", TableColors.CYAN, bold=True))
            from grammar_utils import print_grammar, print_first_follow
            print_grammar(slr_parser.productions)
            print_first_follow(slr_parser.productions, slr_parser.non_terminals, slr_parser.start_symbol)
            slr_parser.print_states()
            slr_parser.print_slr_table()
            slr_parser.print_reductions()

            print("\n" + color_text("STRING ANALYSIS", TableColors.YELLOW, bold=True))
            for string in slr_test_strings:
                if not string.strip(): continue
                slr_parser.validate_input(string.strip())

    elif is_ll1:
        print(color_text("\nUsing LL(1) Parser", TableColors.CYAN, bold=True))
        from F import print_info as ll1_print_info
        ll1_print_info(analyzer)
        print("\n" + color_text("STRING ANALYSIS", TableColors.YELLOW, bold=True))
        for string in ll1_test_strings:
            if not string.strip(): continue
            print(f"\nInput: {color_text(string, TableColors.CYAN)}")
            valid, msg, steps = analyzer.validate_string(string.strip())
            create_result_box(valid, msg)

    elif is_slr1:
        print(color_text("\nUsing SLR(1) Parser", TableColors.CYAN, bold=True))
        from grammar_utils import print_grammar, print_first_follow
        print_grammar(slr_parser.productions)
        print_first_follow(slr_parser.productions, slr_parser.non_terminals, slr_parser.start_symbol)
        slr_parser.print_states()
        slr_parser.print_slr_table()
        slr_parser.print_reductions()

        print("\n" + color_text("STRING ANALYSIS", TableColors.YELLOW, bold=True))
        for string in slr_test_strings:
            if not string.strip(): continue
            slr_parser.validate_input(string.strip())
    else:
        print(color_text("\n❌ Grammar is neither LL(1) nor SLR(1)", TableColors.RED, bold=True))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(color_text("Usage: python Main.py <grammar_file>", TableColors.YELLOW))
        sys.exit(1)
    main(sys.argv[1])