
# Grammar Parser - LL(1) and SLR(1) Analyzer

## 📘 Description  
A Python-based tool developed for the *Formal Languages and Compilers* course (*ST0270 / SI2002*). This tool implements both **LL(1)** and **SLR(1)** parsers for context-free grammars. It features colorful terminal output, detailed parsing steps, and comprehensive grammar analysis.

### 👥 Group Members  
- Erick Guerrero  
- David Ortiz  
- Anyela Jimenez  

### 🖥️ Environment  
- **Operating System:** Windows 11  
- **Programming Language:** Python 3.12  
- **Libraries Used:**  
  - `tabulate` 0.8.9  
  - `colorama` *(optional, for color output)*

---

## ✨ Features

### 🔍 Grammar Analysis  
- Automatic detection of grammar type: **LL(1)**, **SLR(1)**, both, or neither  
- Proper computation of **FIRST** and **FOLLOW** sets  
- Detection of **left recursion**  
- Detection of **conflicts** (e.g., shift/reduce in SLR(1))  
- Grammar validation and **user-friendly feedback**

### 📊 Parsing Capabilities  
- **LL(1) Parser:**
  - Generates parsing table
  - Step-by-step derivation output
  - Halts and warns on left recursion
- **SLR(1) Parser:**
  - Constructs LR(0) automaton
  - Generates **ACTION** and **GOTO** tables
  - Detects and flags shift/reduce conflicts

### 🧑‍💻 User Interface  
- Colored and bordered output using `colorama` and `tabulate`  
- Interactive parser selection  
- Clear diagnostics and table previews  
---

---

## 🚀 Usage

1. **Prepare the grammar file (`grammar.txt`)** in the following format:
```
<number of productions>
Production 1
Production 2
...
Production N
<string to analyze 1>
<string to analyze 2>
...
<string to analyze M>
```

📝 **Example:**
```
3
S -> AB
A -> aA | d
B -> bBc | e
adbc
d
a
```

2. **Run the analyzer:**
```bash
python Main.py grammar.txt
```

3. **Select the parsing strategy:**
- `T`: Use **LL(1)** parser
- `B`: Use **SLR(1)** parser
- `Q`: Quit the program

---

## 📁 File Structure
```
project/
├── Main.py             # Program entry point and CLI
├── F.py                # LL(1) parser module
├── S.py                # SLR(1) parser module
├── grammar_utils.py    # Grammar processing and set computations
├── table_utils.py      # Table rendering helpers
├── grammar.txt         # Input grammar and strings file
└── README.md           # Project documentation
```

---

## 🧪 Sample Output

### Grammar Analysis
```
✓ Grammar is LL(1) - No conflicts found
✓ Grammar is SLR(1) - No conflicts found

═══════════════════════════════════════
 Grammar is both LL(1) and SLR(1) 
═══════════════════════════════════════
```

### Parsing Result
```
╔════════════════════╗
║✓ Result: YES      ║
║  Input Accepted   ║
╚════════════════════╝
```

---

## 🧩 Problems Encountered and Solutions

### 1. Left Recursion
- **Problem:** Causes infinite loops in LL(1) parsing.
- **Solution:** Implemented detection. Program halts LL(1) parsing and warns user.

### 2. Incorrect FIRST and FOLLOW
- **Problem:** `ε` (`e`) was not propagated properly.
- **Solution:** Fixed computation to handle `e` correctly.

### 3. Shift/Reduce Conflicts
- **Problem:** Conflicts in SLR(1) `action` table.
- **Solution:** Conflicts are detected and flagged. Parsing is not allowed until fixed.

### 4. Table Construction Errors
- **Problem:** Uninitialized structures caused runtime errors.
- **Solution:** Improved initialization and added debug tools.

### 5. Invalid Grammars
- **Problem:** Some grammars were ambiguous or not suitable for LL(1)/SLR(1).
- **Solution:** Program classifies the grammar and prevents invalid analysis.

---

## ✅ Requirements
- Python 3.8+
- `tabulate`
- `colorama` (optional but recommended)

---

## ⚠️ Limitations
- Only supports LL(1) and SLR(1) parsing
- Grammar must be formatted correctly in `grammar.txt`
- Conflict resolution strategies (e.g., operator precedence) are not implemented
- Ambiguous grammars are not supported

---
