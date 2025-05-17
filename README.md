# FORMAL LANGUAGES AND COMPILERS - Parser Implementation

Group Members:
- Erick Guerrero
- David Ortiz
- Anyela Jimenez

## Implementation Details

Operating System:
- Windows 11

Programming Language:
- Python 3.12 (or the version you used)

Tools and Libraries:
- tabulate 0.8.9 (for pretty-printing tables)

## Running the Implementation

1.  **Prerequisites:**
    * Ensure you have Python 3.6 or later installed on your system.
    * Install the `tabulate` library:
        ```bash
        pip install tabulate
        ```

2.  **Execution:**
    * Save the provided Python code as a `.py` file (e.g., `parser.py`).
    * Run the script from the command line:
        ```bash
        python parser.py
        ```

3.  **Input:**
    * The program will first prompt you to enter the number of non-terminals in the grammar.
    * Then, enter each production rule on a new line, in the format:
        `<nonterminal> -> <derivation alternatives separated by blank spaces>`
        * Alternatives for a non-terminal should be separated by spaces.
        * Use "|" to separate alternatives within a derivation (e.g., `T -> T * F | F`).
        * Represent the empty string (epsilon) as `e`.
    * After entering the grammar, the program will output whether the grammar is LL(1), SLR(1), both, or neither.
    * If the grammar is LL(1) or SLR(1) (or both), the program will then prompt you to enter strings to parse, one string per line.
    * Enter the strings you want to parse. The program will output "yes" if the string is accepted by the grammar and "no" otherwise.
    * To stop entering strings, enter an empty line.
    * If the grammar is both LL(1) and SLR(1), the program will prompt you to select a parser ('T' for LL(1), 'B' for SLR(1), 'Q' for quit) before parsing strings. [cite: 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 30, 31, 32, 5, 6, 7]

## Areas for Improvement

-   **Error Handling:** The LL(1) parser could benefit from more detailed error reporting. Instead of just indicating "no," it could pinpoint the location of the error in the input string and the expected symbol based on the parsing table.
-   **SLR(1) Conflict Resolution:** The current SLR(1) implementation detects conflicts (shift/reduce or reduce/reduce) but doesn't attempt to resolve them. Ideally, a more robust parser generator would incorporate conflict resolution strategies (e.g., using precedence and associativity rules).
-   **"Select a parser" Logic:** The program determines if the grammar is LL(1) or SLR(1), but the menu logic for explicitly selecting a parser ('T', 'B', 'Q') as outlined in the assignment is not fully implemented.
-   **Output Format:** While generally correct, the output format could be made to strictly adhere to all the examples provided in the assignment description, ensuring consistency in all scenarios. [cite: 10, 11, 12, 13, 14, 15, 27, 29, 33, 34, 35, 36, 8]

## Challenges with SLR(1) Implementation

-   The SLR(1) implementation correctly builds the parsing tables and detects conflicts. However, it does not proceed to parse input strings *if conflicts are detected*. SLR(1) parsers are designed to handle a larger class of grammars than LL(1), but conflicts indicate ambiguity that the basic SLR(1) algorithm cannot resolve without further guidance. [cite: 7, 8]
-   In our implementation, if `build_slr_table` identifies conflicts, the `slr_parse` function might not be reliably used, or its results might be incorrect for some inputs. To fully "make it work," conflict resolution strategies need to be added to the table construction.
-   The primary reason it "doesn't fully work" for all SLR(1) grammars is the *lack of conflict resolution*, not an error in the table building itself.

## Files Included

-   `parser.py` - The Python script containing the parser implementation.
-   `README.md` - This file. [cite: 28, 29]
