# Copyright (c) 2025 Benjamin O'Brien
# Version 3.3

# Modules
import re
import operator
from enum import Enum
from dataclasses import dataclass

# Initialization
OPERATORS = {}
for symbols, data in {
    ("⦁", "•", "∧", "^", "&"): {
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

# Enums
class ComparisonMode(Enum):
    RELATIONSHIP = 1
    VALIDITY     = 2

class ValidityResult(Enum):
    VALID   = 1
    INVALID = 2

@dataclass
class RelationshipResult:
    equivalent:    bool
    consistent:    bool
    contradictory: bool
    inconsistent:  bool

# Exceptions
class UnknownOperator(Exception):
    pass

# Methods
class Logic:
    def __init__(self, enable_logging: bool = True) -> None:
        self.enable_logging = enable_logging

    @staticmethod
    def trim(expression: str) -> str:
        return expression[1:][:-1] if expression[0] in GROUPINGS.keys() else expression

    def evaluate(self, expression: str, variables: dict[str, bool], index: int = 0) -> bool:
        def log(text: str, indent: int = 0) -> None:
            if self.enable_logging:
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
            left_value, right_value = self.evaluate(self.trim(left), variables, index + 1), self.evaluate(self.trim(right), variables, index + 1)
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
                value = self.evaluate(self.trim(sanitized), variables, index + 1)

            # Negate the value as many times as needed
            for _ in range(len(segments[0]) - len(segments[0].lstrip("~"))):
                value = not value

            log(f"Evaluate --> {segments[0]} (\033[3{2 if value else 1}m{value}\033[90m)", 1)
            return value

    def find_possible_values(self, *expressions) -> list[list[bool]]:
        variables = []
        for expression in expressions:
            variables += [c for c in expression if c in string.ascii_letters]

        results = []
        def loopback(variables: list[str], values: dict[str, bool] = {}) -> None:
            current_variable = variables[0]
            for value in [True, False]:
                if variables[1:]:
                    loopback(variables[1:], values | {current_variable: value})

                else:
                    results.append([
                        self.evaluate(
                            expression,
                            variables = values | {current_variable: value}
                        )
                        for expression in expressions
                    ])

        loopback(sorted(set(variables)))
        return results

    def compare(self, mode: ComparisonMode, *expressions) -> RelationshipResult | ValidityResult:
        values = self.find_possible_values(*expressions)
        match mode:
            case ComparisonMode.RELATIONSHIP:
                print(values)
                consistent = any([x and y for x, y in values])
                return RelationshipResult(
                    all([x == y for x, y in values]),
                    consistent,
                    all([x != y for x, y in values]),
                    not consistent
                )

            case ComparisonMode.VALIDITY:
                for item in values:
                    if all(item[:-1]) and not item[-1]:
                        return ValidityResult.INVALID

                return ValidityResult.VALID

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
        result = Logic().evaluate(
            expression,
            variables = variables
        )

        print(f"\n\033[36mThe end value is \033[3{2 if result else 1}m{result}.\033[36m")
        print(f"\033[90m  -> Took {round((time.time() - start_time) * 1000)}ms total to calculate.")

    options = [arg for arg in sys.argv[1:] if arg[:2] == "--"]
    expressions = [arg for arg in sys.argv[1:] if arg[:2] != "--"]

    if expressions:
        if "--compare" in options:
            result = Logic(enable_logging = False).compare(ComparisonMode.RELATIONSHIP, *expressions)
            if not isinstance(result, RelationshipResult):
                raise RuntimeError

            print("\033[36mGiven the following equations:")
            for expression in expressions:
                print(f"\033[90m  -> {expression}")

            data = [f"\033[3{1 if 'in' in v or 'ory' in v else 2}m{v}\033[36m" for v in dir(result) if v[0] != "_" and getattr(result, v)]
            print(f"\n\033[36mTheir relationship is {' and '.join(data)}.")
            exit()

        if "--validity" in options:
            result = Logic(enable_logging = False).compare(
                ComparisonMode.VALIDITY,
                *expressions[0].split("//")[0].split("/"),
                expressions[0].split("//")[-1]
            ) == ValidityResult.VALID
            print(f"\033[36mThe provided expression is \033[3{2 if result else 1}m{'valid' if result else 'invalid'}.\033[36m")
            exit()

        [run(expression) for expression in expressions]
        exit()

    while True:
        expression = input("\033[2J\033[H\033[36mExpression: \033[90m")
        run(expression)
        input("\n\033[90m[ Press ENTER to enter another expression. ]")
