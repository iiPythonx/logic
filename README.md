# iiPythonx / Logic

A logic symbol processor for PHI-1113.

## Usage

Example usage:
```sh
python3 logic.py "(X ⊃ Z) ⊃ [(B ≡ ~X) ⦁ ~(C ∨ ~A)]"
python3 logic.py "~(~B v B)" "(A ⊃ B) ⦁ (A ⦁ ~B)" --compare
python3 logic.py "~(A v ~B) / ~A v B // A ≡ B" --validity
```

Alternatively, run `python3 logic.py` with no arguments for an interactive session.

## Support

- Basic logic symbols (as defined by [Wikipedia](https://en.wikipedia.org/wiki/List_of_logic_symbols))
    - Material conditional ("⊃", "→", "⇒")
    - Material biconditional ("≡", "↔", "⇔")
    - Negation ("~")
    - Logical conjunction ("⦁", "•", "∧", "^", "&")
    - Logical inclusive disjunction ("∨", "v", "+", "∥")

- Basic structuring/organization
    - Supports nested parenthesis, brackets, and curly braces

- Supports basic equations
    - `(X ⊃ Z) ⊃ [(B ≡ ~X) ⦁ ~(C ∨ ~A)]`
    - `~(~B ∨ ~A)`
    - `(A ⊃ B) ⦁ (A ⦁ ~B)`
    - And nearly any other valid equation, as defined by the above prerequisites

- Supports truth tables
    - Supports calculating if an expression is valid or invalid
    - ~~Supports brute force calculating all possible values for a given equation~~ (soon)
    - Supports calculating [Equivalent](https://en.wikipedia.org/wiki/Logical_equivalence)/[Contradictory](https://en.wikipedia.org/wiki/Contradiction)/[Consistent](https://en.wikipedia.org/wiki/Consistency#First-order_logic)/[Inconsistent](https://en.wikipedia.org/wiki/Consistency#First-order_logic)
