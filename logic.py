# Copyright (c) 2025 Benjamin O'Brien
# Version 3.1

# Modules
import re
import operator

# Initialization
OPERATORS = {}
for symbols, data in {
    ("⦁", "∧", "^", "&"): {
        "name": "AND",
        "comparison": operator.and_
    },
    ("⊃", "→", "⇒"): {
        "name": "CONDITIONAL",
        "comparison": lambda left, right: right if left else True
    },
    ("≡", "↔", "⇔"): {
        "name": "EQUALIFICATION",
        "comparison": operator.eq
    },
    ("∨", "v", "+", "∥"): {
        "name": "INCLUSIVE OR",
        "comparison": operator.or_
    }
}.items():
    for symbol in symbols:
        OPERATORS[symbol] = data

GROUPINGS = {"(": ")", "[": "]", "{": "}"}
REGEX = re.compile(rf"((?:~+)?[A-Z]) ?([{''.join(OPERATORS.keys())}])? ?((?:~+)?[A-Z])?")

# Exceptions
class UnknownOperator(Exception):
    pass

# Methods
def trim(expression: str) -> str:
    return expression[1:][:-1] if expression[0] in GROUPINGS.keys() else expression

def evaluate(expression: str, variables: dict[str, bool], index: int = 0) -> bool:
    def log(text: str, indent: int = 0) -> None:
        print(f"\033[90m{'\t' * (indent + index)}{text}\033[0m")

    # Take expression, and find the top level assets
    depth, segments, buffer = 0, [], ""
    for character in expression:
        match character:
            case " ":
                continue

            case _ if character in GROUPINGS.keys():
                depth += 1
                buffer += character

            case _ if character in GROUPINGS.values():
                depth -= 1
                buffer += character
                if not depth:
                    segments.append(buffer)
                    buffer = ""

            case _ if not depth and character in OPERATORS:
                if buffer:
                    segments.append(buffer)

                segments.append(character)
                buffer = ""

            case _:
                buffer += character

    if buffer:
        segments.append(buffer)

    log(f"Input expression --> {expression}")

    # Process chains
    if len(segments) > 1:
        left, operator, right = segments
        left_value, right_value = evaluate(trim(left), variables, index + 1), evaluate(trim(right), variables, index + 1)
        log(f"Segments --> {' '.join(segments)}", 1)
        log(f"Method --> {OPERATORS[operator]['name']}", 2)

        if operator not in OPERATORS:
            raise UnknownOperator(f"the specified operator ({operator}) is not known!")

        value = OPERATORS[operator]["comparison"](left_value, right_value)
        log(f"Result --> {left_value} {operator} {right_value} (\033[3{2 if value else 1}m{value}\033[90m)", 2)
        return value

    # Process non-chained values (or anything with a tilde)
    else:
        sanitized = segments[0].lstrip("~")

        # Attempt to find value as a variable
        value = variables.get(sanitized)
        if value is None:

            # If it isn't one, assume it's another chain
            value = evaluate(trim(sanitized), variables, index + 1)

        # Negate the value as many times as needed
        for _ in range(len(segments[0]) - len(segments[0].lstrip("~"))):
            value = not value

        log(f"Evaluate --> {segments[0]} (\033[3{2 if value else 1}m{value}\033[90m)", 1)
        return value

# CLI
if __name__ == "__main__":
    import sys
    import time
    import string

    def run(expression: str):
        variables = {
            v: {"t": True, "f": False}[input(f"  -> \033[36m{v}: \033[90m").lower()[0]]
            for v in sorted(set([c for c in expression if c in string.ascii_letters]))
        }

        # Calculate result
        start_time = time.time()

        print()
        result = evaluate(
            expression,
            variables = variables
        )

        print(f"\n\033[36mThe end value is \033[3{2 if result else 1}m{result}.\033[36m")
        print(f"\033[90m  -> Took {round((time.time() - start_time) * 1000)}ms total to calculate.")

    if len(sys.argv) > 1:
        run(sys.argv[1])
        exit()

    while True:
        expression = input("\033[2J\033[H\033[36mExpression: \033[90m")
        run(expression)
        input("\n\033[90m[ Press ENTER to enter another expression. ]")
