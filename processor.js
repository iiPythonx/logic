// Copyright (c) 2025 iiPython
// Rewrite of https://github.com/iiPythonx/logic using JS.

const CONJUNCTION = ["⦁", "•", "∧", "^", "&"];
const CONDITIONAL = ["⊃", "→", "⇒"];
const EQUIVALANCE = ["≡", "↔", "⇔"];
const DISJUNCTION = ["∨", "+", "∥"];

const GROUPINGS = {"(": ")", "[": "]", "{": "}"};
const OPERATORS = [
    {
        "symbols": CONJUNCTION,
        "comparison": (x, y) => x && y
    },
    {
        "symbols": CONDITIONAL,
        "comparison": (x, y) => x ? y : true
    },
    {
        "symbols": EQUIVALANCE,
        "comparison": (x, y) => x === y
    },
    {
        "symbols": DISJUNCTION,
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

    parse(expression) {
        let depth = 0, segments = [], buffer = "";
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
        return segments;
    }

    evaluate(expression, variables, index) {

        // Take expression, and find the top level assets
        const segments = this.parse(expression);

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

    check_rule(lines, attempted_rule, conclusion) {
        lines = lines.map(line => this.parse(line));
        conclusion = this.parse(conclusion);
        switch (attempted_rule.toUpperCase()) {
            case "MP":    // Modus Ponens
                return lines.length === 2 &&
                        CONDITIONAL.includes(lines[0][1])                          &&
                        this.trim(lines[0][0]) === this.trim(lines[1].join(""))    &&
                        this.trim(lines[0][2]) === this.trim(conclusion.join(""));

            case "MT":    // Modus Tollens
                return lines.length === 2 &&
                        CONDITIONAL.includes(lines[0][1])        &&
                        lines[1].join("") === `~${lines[0][2]}`  &&
                        `~${lines[0][0]}` === conclusion.join("");

            case "HS":    // Hypothetical Syllogism
                return lines.length === 2 &&
                        CONDITIONAL.includes(lines[0][1]) &&
                        CONDITIONAL.includes(lines[1][1]) &&
                        lines[0][2] === lines[1][0];

            case "DS":    // Disjunctive Syllogism
                return lines.length === 2 &&
                        DISJUNCTION.includes(lines[0][1])     &&
                        `~${lines[0][0]}` === lines[1].join("") &&
                        lines[0][2] === conclusion.join("");

            case "CD":    // Constructive Dillemma
                const first = this.parse(this.trim(lines[0][0]));
                const second = this.parse(this.trim(lines[0][2]));
                return lines.length === 2 &&
                        DISJUNCTION.includes(conclusion[1]) &&  // Ensure conclusion is a disjunct
                        CONJUNCTION.includes(lines[0][1])   &&  // Ensure first line is a conjunct
                        DISJUNCTION.includes(lines[1][1])   &&  // Ensure second line is a disjunct
                        CONDITIONAL.includes(first[1])      &&  // Ensure first piece is a conditional
                        CONDITIONAL.includes(second[1])     &&  // Ensure second piece is a conditional
                        first[0]  === lines[1][0]           &&  // Ensure first piece matches disjunct
                        second[0] === lines[1][2]           &&  // Ensure second piece matches disjunct
                        first[2]  === conclusion[0]         &&  // Ensure first piece matches conclusion
                        second[2] === conclusion[2]             // Ensure second piece matches conclusion

            case "CONJ":  // Conjunction
                return lines.length === 2 &&
                        CONJUNCTION.includes(conclusion[1])             &&
                        this.trim(conclusion[0]) === lines[0].join("")  &&
                        this.trim(conclusion[2]) === lines[1].join("");

            case "ADD":   // Addition
                return lines.length === 1 &&
                    DISJUNCTION.includes(conclusion[1]) &&
                    conclusion[0] === lines[0].join("");

            case "SIMP":  // Simplification
                return lines.length === 1 &&
                    CONJUNCTION.includes(lines[0][1]) &&
                    this.trim(conclusion.join()) === this.trim(lines[0][0]);

            default:
                if (!this.alerted) {
                    alert("This tool allows you to use rules of replacement with no rule validation. It's up to you to make sure your rule is OK. This notice will not be shown again.");
                    this.alerted = true;
                }
                return true;
        }
    }
};
