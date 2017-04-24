ll-py-parser is a simple LL-parser which processes file giving out brackets balance in it.

## Grammar

It is based on the following LL(1) grammar:

    E -> F $ 
	F -> S F | <ignored_char> F | <newline> count_line() F | ε
    S -> ( enter_new_scope() F ) exit_scope() | 
         [ enter_new_scope() F ] exit_scope() | 
         { enter_new_scope() F } exit_scope()

with the following parsing table:

|       | `(`    | `)`    | `[`    | `]`    | `{`    | `}`    | `<ignored_char>`   | `<newline>`   |    `$`    |
| ----- | ------ | ------ | ------ | ------ | ------ | ------ | ------------------ | ------------- | --------- |
| `E` | `R0` | `-` | `R0` | `-` | `R0` | `-` |		`R0`		|		`R0`		|	`R0`	|
| `F` | `R1` | `R4` | `R1` | `R4` | `R1` | `R4` |		`R2`		|		`R3`		|	`R4`    |
| `S` | `R5` | `-`  | `R6` | `-`  | `R7` | `-`  |		`-`			|		`-`         |	`-`	|


with R0...R7 the rules in the aforementioned grammar

**Legal expressions**

- ```(round1[internalsquare]round2)```
- ```[square](round){curly}```
- ```[\n]``` — multi-lined brackets

**Illegal expressions**

- `(])` — closed bracket without matching open bracket
- `[a(b]c)` — ill-locked brackets
- `[abc\n` — non-closed brackets

**Semantic routines (pseudo-code)**

    enter_scope(last_token, current_scope_level, current_line):
        total_brackets++
        brackets_in_line[current_line]++
        current_scope_level++
        scope_stack.push((last_token, current_scope_level, current_line))
        
    exit_scope(current_scope_level, current_line):
        total_brackets++
        brackets_in_line[current_line]++
        current_scope_level--
        scope_stack.pop()
    
    count_line(current_line):
        current_line++
        brackets_in_line[current_line] = 0

## Examples and corresponding output

**file_senza_errori.txt**

~~~~ {.txt .numberLines startFrom="1"}
adhi9e9u
((
))
[[doublequadra]]
{ab(c
)def}
~~~~

**file_con_errore_1.txt**

~~~~ {.txt .numberLines startFrom="1"}
[questo](è){legale}
[quadra]
{graffa}
(((())))
[][]{}{}{}
(error
aiduhiua
daiodaa[]
~~~~

**file_con_errore_2.txt**

~~~~ {.txt .numberLines startFrom="1"}
[questo](è){legale}
(((error
aiduhiua
daiodaa[]
}
~~~~


**Output**
```
Current file: file_senza_errori.txt
Input accepted with no errors
Total number of brackets: 12
Brackets are present in lines:  [2, 3, 4, 5, 6]


Current file: file_con_errore_1.txt
Syntax error: can't find matching bracket for TSymbol.L_RND_BRACKET 
            on line 6 (scope level: 1)


Current file: file_con_errore_2.txt
Syntax error: can't find matching bracket for TSymbol.L_RND_BRACKET 
            on line 2 (scope level: 3)
```


