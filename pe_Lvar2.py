from ast import *

def pe_neg(r):
	match r:
		case Constant(n):
			return Constant(-n)
		case _:
			return UnaryOp(USub(), r)
		
def pe_add(r1, r2):
	match (r1, r2):
		case (Constant(n1), Constant(n2)):
			return Constant(n1 + n2)
		case _:
			return BinOp(r1, Add(), r2)
	
def pe_sub(r1, r2):
	match (r1, r2):
		case (Constant(n1), Constant(n2)):
			return Constant(n1 - n2)
		case _:
			return BinOp(r1, Sub(), r2)
	


# inert ::= var | input_int() | -var | -input_int() | inert + inert
# residual ::= int | int + inert | inert

def pe_exp(e):
	match e:
		case BinOp(left, Add(), right):
			return pe_add(pe_exp(left), pe_exp(right))
		case BinOp(left, Sub(), right):
			return pe_sub(pe_exp(left), pe_exp(right))
		case UnaryOp(USub(), v):
			return pe_neg(pe_exp(v))
		case Constant(value):
			return e
		case Call(Name('input_int'), []):
			return e
		case Name(id):
			return e
		
def pe_stmt(s):
	match s:
		case Expr(Call(Name('print'), [arg])):
			return Expr(Call(Name('print'), [pe_exp(arg)]))
		case Expr(value):
			return Expr(pe_exp(value))
		case Assign([Name(id)], value):
			return Assign([Name(id)], pe_exp(value))
		case _:
			raise Exception('error in pe_stmt, unexpected ' + repr(s))

def pe_P_var(p):
	match p:
		case Module(body):
			new_body = [pe_stmt(s) for s in body]
			return Module(new_body)

p_str = r'''
i = 1 + 3 - 1
j = 2 - 3 + 4
print(1 + ((input_int() + 1) + j + i))
'''

if __name__ == "__main__":
    p = parse(p_str)
    print(unparse(p))
    print(dump(p))
    # print(unparse(pe_P_var(p)))
    # AttributeError: 'Module' object has no attribute 'type_ignores'
    print(dump(pe_P_var(p)))
