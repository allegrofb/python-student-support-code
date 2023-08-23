

def map(f : Callable[[int], int], v : tuple[int,int]) -> tuple[int,int]:
	return f(v[0]), f(v[1])
	
def inc(x : int) -> int:
	return x + 1
	
print( map(inc, (0, 41))[1] )



# failed
# interp_x86/convert_x86.py
# unhandled IndirectCallq(func=Variable(id='f'), num_args=1)

