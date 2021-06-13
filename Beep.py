#######################################
# IMPORTS
#######################################

from beepmaker import *
from sequence import *
import time
#######################################
# CONSTANTS
#######################################

KEYNOTES = 'ABCDEFGHIJKLMNOPQRSTUVWYZ'

#######################################
# ERRORS
#######################################

class Error:
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details

	def as_string(self):
		result = f'{self.error_name}: {self.details}\n'
		result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
		return result

class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Runtime Error', details)
		self.context = context

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context

		while ctx:
			result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result

#######################################
# POSITION
#######################################

class Position:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def increment(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# LEXEMES
#######################################

LEX_KEYNOTE  = 'KEYNOTE'
LEX_NEXT     = 'NEXT'
LEX_PAUSE    = 'PAUSE'
LEX_SIM      = 'SIMULTANEOUS'
LEX_SEQ      = 'SEQUENCE'
LEX_LPAREN   = 'LEFT PARENTHESE'
LEX_RPAREN   = 'RIGHT PARENTHESE'
LEX_END		 = 'EOF'

class Token:
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.increment()

		if pos_end:
			self.pos_end = pos_end

	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
	def __init__(self, fn, text):
		self.fn = fn
		self.text = text
		self.pos = Position(-1, 0, -1, fn, text)
		self.current_char = None
		self.increment()

	def increment(self):
		self.pos.increment(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def make_tokens(self):
		tokens = []

		Sinefreq = {'A':181.63, 'B':192.43, 'C':203.88, 'D':216.00, 'E':228.45,
				'F':242.45, 'G':261.63, 'H':277.18, 'I':293.66, 'J':311.15,
				'K':329.63, 'L':349.23, 'M':369.99, 'N':372.68, 'O':375.02,
				'P':392.00, 'Q':440.00, 'R':415.30, 'S':466.16, 'R':493.88,
				'S':499.23, 'T':500.25, 'U':510.34, 'V':520.45, 'W':550.93,
				'X':580.88, 'Y':600.32, 'Z':660.00}

		while self.current_char != None:
			if self.current_char in ' \t':
				self.increment()

			elif self.current_char in KEYNOTES:
				tokens.append(Token(LEX_KEYNOTE, float(Sinefreq[self.current_char]), pos_start=self.pos))
				self.increment()

			elif self.current_char == '+':
				tokens.append(Token(LEX_NEXT, pos_start=self.pos))
				self.increment()

			elif self.current_char == '-':
				tokens.append(Token(LEX_PAUSE, pos_start=self.pos))
				self.increment()

			elif self.current_char == '*':
				tokens.append(Token(LEX_SIM, pos_start=self.pos))
				self.increment()

			elif self.current_char == '/':
				tokens.append(Token(LEX_SEQ, pos_start=self.pos))
				self.increment()

			elif self.current_char == '(':
				tokens.append(Token(LEX_LPAREN, pos_start=self.pos))
				self.increment()

			elif self.current_char == ')':
				tokens.append(Token(LEX_RPAREN, pos_start=self.pos))
				self.increment()
			else:
				pos_start = self.pos.copy()
				char = self.current_char
				self.increment()
				return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

		tokens.append(Token(LEX_END, pos_start=self.pos))
		return tokens, None



#######################################
# NODES
#######################################

class SFrequencyNode:
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

#######################################
# PARSE RESULT
#######################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self

#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.increment()

	def increment(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != LEX_END:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*' or '/'"
			))
		return res

	###################################

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (LEX_NEXT, LEX_PAUSE):
			res.register(self.increment())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))

		elif tok.type is LEX_KEYNOTE:
			res.register(self.increment())
			return res.success(SFrequencyNode(tok))

		elif tok.type == LEX_LPAREN:
			res.register(self.increment())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == LEX_RPAREN:
				res.register(self.increment())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected float"
		))

	def term(self):
		return self.bin_op(self.factor, (LEX_SIM, LEX_SEQ))

	def expr(self):
		return self.bin_op(self.term, (LEX_NEXT, LEX_PAUSE))

	###################################

	def bin_op(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register(self.increment())
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)

#######################################
# RUNTIME RESULT
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

#######################################
# VALUES
#######################################

class SFrequency:
	def __init__(self, value):
		self.value = value
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def next_to(self, other):
		if isinstance(other, SFrequency):
			beepmaker(self.value)
			beepmaker(other.value)
			return SFrequency(abs(self.value + other.value)).set_context(self.context), None

	def paused(self, other):
		if isinstance(other, SFrequency):
			beepmaker(self.value)
			print("...Pause...")
			time.sleep(2)
			beepmaker(other.value)
			return SFrequency(abs(self.value - other.value)).set_context(self.context), None

	def simultaneous(self, other):
		if isinstance(other, SFrequency):
			beepmaker(abs(self.value + other.value))
			return SFrequency(abs(self.value*other.value)).set_context(self.context), None

	def sequenced(self, other):
		if isinstance(other, SFrequency):
			sequence(self.value, other.value)

			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			return SFrequency(abs(self.value / other.value)).set_context(self.context), None

	def __repr__(self):
		return str(self.value)

#######################################
# CONTEXT
#######################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos

#######################################
# INTERPRETER
#######################################

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	###################################

	def visit_SFrequencyNode(self, node, context):
		return RTResult().success(
			SFrequency(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.error: return res
		right = res.register(self.visit(node.right_node, context))
		if res.error: return res

		if node.op_tok.type == LEX_NEXT:
			result, error = left.next_to(right)
		elif node.op_tok.type == LEX_PAUSE:
			result, error = left.paused(right)
		elif node.op_tok.type == LEX_SIM:
			result, error = left.simultaneous(right)
		elif node.op_tok.type == LEX_SEQ:
			result, error = left.sequenced(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		sfrequency = res.register(self.visit(node.node, context))
		if res.error: return res

		error = None

		if node.op_tok.type == LEX_PAUSE:
			sfrequency, error = sfrequency.simultaneous(SFrequency(-1))

		if error:
			return res.failure(error)
		else:
			return res.success(sfrequency.set_pos(node.pos_start, node.pos_end))

#######################################
# RUN
#######################################

def run(fn, text):
	# Generate tokens
	LexicalAnalysis = Lexer(fn, text)
	tokens, error = LexicalAnalysis.make_tokens()
	if error: return None, error
	
	# Generate AST
	SyntaxAnalysis = Parser(tokens)
	ast = SyntaxAnalysis.parse()
	if ast.error: return None, ast.error

	# Run program
	SemanticAnalysis = Interpreter()
	context = Context('<program>')
	result = SemanticAnalysis.visit(ast.node, context)

	return result.value, result.error

