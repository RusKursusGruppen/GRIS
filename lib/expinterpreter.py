class ExpinterpreterException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Not a valid expression: " + repr(self.value)

def lexer(string):
    result = ['']
    for char in string:
        if char.isdigit():
            if result[-1].isdigit():
                result[-1] += char
            else:
                result.append(char)
        elif char in "+-*/()l|":
            result += char
        else:
            result.append("")
    return [r for r in result[1:] if r != ""]

def rpn(tokens):
    stack = []
    for t in tokens:
        if t.isdigit():
            stack.append(int(t))
        elif t in "+-*/":
            if len(stack) < 2:
                raise ExpinterpreterException()
            y = stack.pop()
            x = stack.pop()
            if t == '+':
                r = x + y
            elif t == '-':
                r = x - y
            elif t == '*':
                r = x * y
            elif t == '/':
                r = x / y
            stack.append(r)
        elif t in "l|":
            if len(stack) == 0:
                stack.append(1)
            else:
                stack.append(stack.pop()+1)
    if len(stack) == 0:
        return 0
    if len(stack) != 1:
        raise ExpinterpreterException(stack)
    return stack[0]


def interpret(string):
    return rpn(lexer(string))
