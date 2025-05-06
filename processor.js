// Copyright (c) 2025 iiPython
// Rewrite of https://github.com/iiPythonx/logic using JS.

const GROUPINGS = {"(": ")", "[": "]", "{": "}"};
const OPERATORS = [
    {
        "symbols": ["⦁", "•", "∧", "^", "&"],
        "comparison": (x, y) => x && y
    },
    {
        "symbols": ["⊃", "→", "⇒"],
        "comparison": (x, y) => x ? y : true
    },
    {
        "symbols": ["≡", "↔", "⇔"],
        "comparison": (x, y) => x === y
    },
    {
        "symbols": ["∨", "+", "∥"],
        "comparison": (x, y) => x || y
    },
];

export class Logic {
    constructor() {
        this.operators = {};
        for (const operator of OPERATORS) {
            for (const symbol of operator.symbols) {
                this.operators[symbol] = operator.comparison;
            }
        }
    }

    trim(expression) {
        return GROUPINGS[expression[0]] ? expression.slice(1, expression.length - 1) : expression;
    }

    evaluate(expression, variables, index) {
        let depth = 0, segments = [], buffer = "";

        // Take expression, and find the top level assets
        for (const character of expression) {
            if (character === " ") continue;
            if (GROUPINGS[character]) {
                depth++;
                buffer += character;
            } else if (Object.values(GROUPINGS).includes(character)) {
                depth--;
                buffer += character;
                if (!depth) {
                    segments.push(buffer);
                    buffer = ""
                }
            } else if (!depth && this.operators[character]) {
                if (buffer.length) segments.push(buffer);
                segments.push(character)
                buffer = ""
            } else { buffer += character; }
        }
        if (buffer) segments.push(buffer);

        // Process chains
        if (segments.length > 1) {
            const [ left, operator, right ] = segments;
            if (!this.operators[operator]) throw new Error("unknown operator!");
            return this.operators[operator](
                this.evaluate(this.trim(left), variables, this.index + 1),
                this.evaluate(this.trim(right), variables, this.index + 1)
            )
        }

        // Process non-chained values (or anything with a tilde)
        const sanitized = segments[0].replace(/^\~+/, "");

        // Attempt to find value as a variable
        let value = variables[sanitized];
        if (value === undefined) {
            
            // If it isn't one, assume it's another chain
            value = this.evaluate(this.trim(sanitized), variables, index + 1);
        }

        // Negate the value as many times as needed
        for (let x = 0; x < (segments[0].length - sanitized.length); x++) value = !value;
        return value;
    }

    find_possible_values(expressions) {
        let variables = [];
        for (const expression of expressions) variables = variables.concat(expression.match(/[a-zA-Z]/g));

        const results = [], that = this;
        function loopback(variables, values) {
            const current_variable = variables[0];
            for (const value of [true, false]) {
                if (variables.slice(1).length) loopback(variables.slice(1), { ...values, ...{ [current_variable]: value } })
                else {
                    results.push(expressions.map((expression) => that.evaluate(
                        expression,
                        { ...values, ...{ [current_variable]: value } },
                        0
                    )));
                }
            }
        }

        variables = [...new Set(variables)];
        variables.sort();

        loopback(variables, {});
        return results;
    }

    consistent(expressions) {
        return this.find_possible_values(expressions).some(sublist => sublist.every(Boolean));
    }
};
