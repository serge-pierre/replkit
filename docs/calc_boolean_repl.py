    
from replkit import repl

"""
A boolean expression interpreter with variable management.
    
Supports boolean operations (and, or, not, xor), variable assignment,
and context inspection. Designed to be used within a REPL environment.
    
Attributes:
    variables (dict): Dictionary storing variable names and their boolean values
    operators (dict): Supported operators and their precedence/preprocessing
"""

class CalcBoolInterpreter:
    def __init__(self):
        self.variables = {}
        self.operators = {
            'not': {'precedence': 4, 'assoc': 'right', 'fn': lambda x: not x},
            'and': {'precedence': 3, 'assoc': 'left', 'fn': lambda x, y: x and y},
            'or':  {'precedence': 2, 'assoc': 'left', 'fn': lambda x, y: x or y},
            'xor': {'precedence': 2, 'assoc': 'left', 'fn': lambda x, y: x != y},
        }

    def eval(self, line: str) -> None:
        """
        Evaluate a line of input and execute the appropriate action.
        
        Handles variable assignment, expression evaluation, and special commands.
        
        Args:
            line: Input string to evaluate
        """
        line = line.strip()
        if not line:
            return
            
        # Handle special commands
        if line == "vars":
            self._show_variables()
            return
        if line == "clear":
            self.variables.clear()
            print("All variables cleared.")
            return
            
        # Handle variable assignment
        if line.startswith("let "):
            self._handle_assignment(line[4:])
            return
            
        # Evaluate as boolean expression
        try:
            result = self._evaluate_expression(line)
            print(f"⇒ {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def get_keywords(self) -> set[str]:
        """Get all keywords for autocompletion support."""
        operators = set(self.operators.keys())
        commands = {"let", "vars", "clear", "True", "False"}
        variables = set(self.variables.keys())
        return operators | commands | variables
    
    def _handle_assignment(self, assignment_str: str) -> None:
        """Process variable assignment in format 'var = expression'."""
        try:
            parts = [p.strip() for p in assignment_str.split("=", 1)]
            if len(parts) != 2:
                raise ValueError("Invalid assignment format. Use 'let var = expr'")
                
            var_name = parts[0]
            if not var_name.isidentifier():
                raise ValueError(f"'{var_name}' is not a valid variable name")
                
            value = self._evaluate_expression(parts[1])
            self.variables[var_name] = value
            print(f"{var_name} = {value}")
        except Exception as e:
            print(f"Assignment error: {str(e)}")
    
    def _show_variables(self) -> None:
        """Display all defined variables and their values."""
        if not self.variables:
            print("No variables defined.")
            return
            
        max_len = max(len(k) for k in self.variables)
        for name, value in sorted(self.variables.items()):
            print(f"{name.ljust(max_len)} = {value}")
    
    def _evaluate_expression(self, expr: str) -> bool:
        """
        Evaluate a boolean expression using the Shunting-Yard algorithm.
        
        Args:
            expr: Boolean expression string to evaluate
            
        Returns:
            Result of the boolean expression
            
        Raises:
            ValueError: If there's a syntax error or undefined variable
        """
        # Tokenize the input
        tokens = self._tokenize(expr)
        # Convert to RPN (Reverse Polish Notation)
        rpn = self._shunting_yard(tokens)
        # Evaluate the RPN expression
        return self._evaluate_rpn(rpn)
    
    def _tokenize(self, expr: str) -> list:
        """
        Convert an expression string into tokens.
        
        Handles operators, parentheses, variables, and boolean literals.
        """
        tokens = []
        i = 0
        n = len(expr)
        
        while i < n:
            c = expr[i]
            
            # Skip whitespace
            if c.isspace():
                i += 1
                continue
                
            # Handle parentheses
            if c in '()':
                tokens.append(c)
                i += 1
                continue
                
            # Handle operators (multi-character)
            for op in sorted(self.operators.keys(), key=len, reverse=True):
                if expr.startswith(op, i):
                    tokens.append(op)
                    i += len(op)
                    break
            else:
                # Handle variables/booleans
                if c.isalpha():
                    j = i
                    while j < n and (expr[j].isalpha() or expr[j].isdigit() or expr[j] == '_'):
                        j += 1
                    token = expr[i:j]
                    tokens.append(token)
                    i = j
                else:
                    raise ValueError(f"Unexpected character: '{c}'")
                    
        return tokens
    
    def _shunting_yard(self, tokens: list) -> list:
        """
        Convert infix notation to RPN using Dijkstra's Shunting-Yard algorithm.
        
        Args:
            tokens: List of tokens in infix notation
            
        Returns:
            List of tokens in RPN notation
        """
        output = []
        operator_stack = []
        
        for token in tokens:
            if token in self.operators:
                # Handle operator precedence and associativity
                while (operator_stack and operator_stack[-1] != '(' and
                       ((self.operators[operator_stack[-1]]['precedence'] > self.operators[token]['precedence']) or
                        (self.operators[operator_stack[-1]]['precedence'] == self.operators[token]['precedence'] and
                         self.operators[token]['assoc'] == 'left'))):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                # Pop until matching '(' is found
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("Mismatched parentheses")
                operator_stack.pop()  # Remove the '('
            else:
                # Variable or boolean literal
                output.append(token)
                
        # Pop remaining operators
        while operator_stack:
            if operator_stack[-1] == '(':
                raise ValueError("Mismatched parentheses")
            output.append(operator_stack.pop())
            
        return output
    
    def _evaluate_rpn(self, rpn: list) -> bool:
        """
        Evaluate an expression in Reverse Polish Notation.
        
        Args:
            rpn: List of tokens in RPN order
            
        Returns:
            Result of the evaluated expression
            
        Raises:
            ValueError: For undefined variables or incorrect arity
        """
        stack = []
        
        for token in rpn:
            if token in self.operators:
                operator = self.operators[token]
                # Handle unary operator
                if token == 'not':
                    if not stack:
                        raise ValueError(f"Operator '{token}' missing operand")
                    operand = stack.pop()
                    stack.append(operator['fn'](operand))
                else:
                    # Handle binary operators
                    if len(stack) < 2:
                        raise ValueError(f"Operator '{token}' requires two operands")
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(operator['fn'](left, right))
            else:
                # Handle variables and literals
                if token == 'True':
                    stack.append(True)
                elif token == 'False':
                    stack.append(False)
                elif token in self.variables:
                    stack.append(self.variables[token])
                else:
                    raise ValueError(f"Undefined variable: '{token}'")
                    
        if len(stack) != 1:
            raise ValueError("Invalid expression")
            
        return stack[0]

def main():
    repl(
        interpreter=CalcBoolInterpreter(),
        argv=[
            "--prompt", "Bool> ",
            "--loglevel", "debug",
            "--hello", "Welcome in CalcBooleanInterpreter",
            "--file", "init.txt",
            "--run", "let D = A or B or C"
        ]
    )

if __name__ == "__main__":
    main()