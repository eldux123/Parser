from tabulate import tabulate
import colorama
colorama.init()

class TableColors:
    # Colores básicos
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    
    # Efectos
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Reset
    RESET = '\033[0m'

def color_text(text, color, bold=False, underline=False):
    effects = ""
    if bold: effects += TableColors.BOLD
    if underline: effects += TableColors.UNDERLINE
    return f"{effects}{color}{text}{TableColors.RESET}"

def create_fancy_table(data, headers, title=None):
    colored_headers = [color_text(h, TableColors.CYAN, bold=True) for h in headers]
    
    table = tabulate(data, 
                    headers=colored_headers, 
                    tablefmt="double_grid",
                    stralign="center",
                    colalign=("left",) * len(headers))
    
    if title:
        width = len(title) + 20
        title_border = color_text('═' * width, TableColors.BLUE)
        title_text = color_text(f" {title} ", TableColors.YELLOW, bold=True)
        table = f"\n{title_border}\n{title_text}\n{title_border}\n\n{table}"
    
    return table

class TableStyles:
    SUCCESS = '\033[92m✓\033[0m'
    ERROR = '\033[91m❌\033[0m'
    ARROW = '\033[94m→\033[0m'
    BOX = {
        'top': '╔═╗',
        'middle': '╠═╣',
        'bottom': '╚═╝',
        'vertical': '║'
    }

def create_result_box(result, message):
    symbol = TableStyles.SUCCESS if result else TableStyles.ERROR
    status = "YES" if result else "NO"
    box_width = max(len(message) + 4, 20)
    
    print(f"""
╔{'═' * box_width}╗
║{symbol} Result: {status:<{box_width-10}}║
║  {message:<{box_width-2}}║
╚{'═' * box_width}╝
    """)