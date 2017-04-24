from enum import IntEnum
import sys


class TermRule(IntEnum):
	TERM = 0
	RULE = 1
	SEM_ROUTINE = 2


class TSymbol(IntEnum):
	L_RND_BRACKET = 0   # '('
	R_RND_BRACKET = 1   # ')'
	L_SQR_BRACKET = 2   # '['
	R_SQR_BRACKET = 3   # ']'
	L_CRL_BRACKET = 4   # '{'
	R_CRL_BRACKET = 5   # '}'
	ANY_CHAR = 6        # .^[()[]{}]
	NEW_LINE = 7        # '\n'
	EPSILON = 8         # empty string
	EOS = 9             # $, end of stack


class NTSymbol(IntEnum):
	N_F = 0
	N_S = 1
	
	
class SemRoutine(IntEnum):
	ENTER_SCOPE = 0
	EXIT_SCOPE = 1
	COUNT_LINE = 2


scope_stack = []
line_to_brackets = {}

	
def enter_scope(token, scope, line, brackets_n):
	brackets_n += 1
	line_to_brackets[line].append(token)
	scope += 1
	scope_stack.append((token, scope, line))
	return line, scope, brackets_n


def exit_scope(token, scope, line, brackets_n):
	brackets_n += 1
	line_to_brackets[line].append(token)
	scope -= 1
	scope_stack.pop()
	return line, scope, brackets_n


def line_count(token, scope, line, brackets_n):
	line += 1
	line_to_brackets[line] = []
	return line, scope, brackets_n

	
execute_semantic_routine = {
	SemRoutine.ENTER_SCOPE: enter_scope,
	SemRoutine.EXIT_SCOPE: exit_scope,
	SemRoutine.COUNT_LINE: line_count
}

# parse table
table = [
	[0, 3, 0, 3, 0, 3, 1, 2, -1, 3],
	[4, -1, 5, -1, 6, -1, -1, -1, -1, -1]
]

rules = [
	[(TermRule.RULE, NTSymbol.N_S), (TermRule.RULE, NTSymbol.N_F)],         # R0: F -> S F
	[(TermRule.TERM, TSymbol.ANY_CHAR), (TermRule.RULE, NTSymbol.N_F)],     # R1: F -> <ignored_char> F
	[(TermRule.TERM, TSymbol.NEW_LINE),                                     # R2: F -> <newline> count_line() F
	 (TermRule.SEM_ROUTINE, SemRoutine.COUNT_LINE), (TermRule.RULE, NTSymbol.N_F)],
	[(TermRule.TERM, TSymbol.EPSILON)],                                     # R3: F -> epsilon
	[(TermRule.TERM, TSymbol.L_RND_BRACKET),                                # R4: S -> ( enter_new_scope() F ) exit_scope()
	 (TermRule.SEM_ROUTINE, SemRoutine.ENTER_SCOPE),
	 (TermRule.RULE, NTSymbol.N_F), (TermRule.TERM, TSymbol.R_RND_BRACKET),
	 (TermRule.SEM_ROUTINE, SemRoutine.EXIT_SCOPE)],
	[(TermRule.TERM, TSymbol.L_SQR_BRACKET),                                # R5: S -> [ enter_new_scope() F ] exit_scope()
	 (TermRule.SEM_ROUTINE, SemRoutine.ENTER_SCOPE),
	 (TermRule.RULE, NTSymbol.N_F), (TermRule.TERM, TSymbol.R_SQR_BRACKET),
	 (TermRule.SEM_ROUTINE, SemRoutine.EXIT_SCOPE)],
	[(TermRule.TERM, TSymbol.L_CRL_BRACKET),                                # R6: S -> { enter_new_scope() F } exit_scope()
	 (TermRule.SEM_ROUTINE, SemRoutine.ENTER_SCOPE),
	 (TermRule.RULE, NTSymbol.N_F), (TermRule.TERM, TSymbol.R_CRL_BRACKET),
	 (TermRule.SEM_ROUTINE, SemRoutine.EXIT_SCOPE)],
]


def lexical_analysis(string):
	tokens = []
	cdict = {
		'(': TSymbol.L_RND_BRACKET, ')': TSymbol.R_RND_BRACKET,
		'[': TSymbol.L_SQR_BRACKET, ']': TSymbol.R_SQR_BRACKET,
		'{': TSymbol.L_CRL_BRACKET, '}': TSymbol.R_CRL_BRACKET,
		'\n': TSymbol.NEW_LINE
	}
	
	for c in string:
		tokens.append(cdict.get(c, TSymbol.ANY_CHAR))
	tokens.append(TSymbol.EOS)
	
	return tokens


def syntactic_analysis(tokens):
	# print('Syntactic analysis')
	stack = [(TermRule.TERM, TSymbol.EOS), (TermRule.RULE, NTSymbol.N_F)]   # Stack initialization
	position = 0                                                            # with R0 rule: E -> F $
	current_line = 1
	line_to_brackets[current_line] = []
	current_scope = 0
	number_of_brackets = 0
	while len(stack) > 0:
		(stype, svalue) = stack.pop()
		if svalue == TSymbol.EPSILON:   # If current stack element is EPSILON, ignore it and continue
			continue
		token = tokens[position]
		if stype == TermRule.TERM:
			if svalue == token:
				position += 1
				if token == TSymbol.EOS:
					print('Input accepted with no errors')
					print("Total number of brackets:", number_of_brackets)
					print("Brackets are present in lines: ",
					        list(filter(lambda line: len(line_to_brackets[line]) > 0, list(line_to_brackets.keys()))))
			else:
				(scope_type, scope_level, scope_line) = scope_stack[-1]
				print("Syntax error: can't find matching bracket for {0} on line {1} (scope level: {2})"
				      .format(str(scope_type), scope_line, scope_level))
				scope_stack.clear()
				line_to_brackets.clear()
				break
		elif stype == TermRule.RULE:
			rule = table[svalue][token]
			for r in reversed(rules[rule]):
				stack.append(r)
		elif stype == TermRule.SEM_ROUTINE:
			current_line, current_scope, number_of_brackets \
				= execute_semantic_routine[svalue](tokens[position - 1], current_scope, current_line, number_of_brackets)

input_file_list = sys.argv[1:]
print(input_file_list)
for input_filename in input_file_list:
	with open(input_filename) as input_file:
		print("Current file: " + input_filename)
		input_string = input_file.read()
		syntactic_analysis(lexical_analysis(input_string))
		print('\n')
