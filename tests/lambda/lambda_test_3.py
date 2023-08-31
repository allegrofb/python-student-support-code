
def f():
	x = 0
	g = lambda: x
	x = 42
	return g
print( f()() )