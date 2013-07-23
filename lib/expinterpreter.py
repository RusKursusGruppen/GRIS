
def lexer(string):
    result = ['']
    for char in string:
        if char.isdigit():
            if result[-1].isdigit():
                result[-1] += char
            else:
                result.append(char)
        elif char in "+-*/()":
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
                raise Exception()
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
    if len(stack) != 1:
        raise Exception(stack)
    return stack[0]


def interpret(string):
    return rpn(lexer(string))
