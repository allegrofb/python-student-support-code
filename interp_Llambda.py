from ast import *
from interp_Lfun import InterpLfun, Function
from utils import *

class ClosureTuple(Value):
  __match_args__ = ("args", "arity")
  def __init__(self, args, arity):
    self.args = args
    self.arity = arity
  def __repr__(self):
    return 'ClosureTuple(' + repr(self.args) + ', ' + repr(self.arity) + ')'
  # TODO: move the following into interp_getitem and interp_setitem 
  def __getitem__(self, item):
    return self.args[item]
  def __setitem__(self, item, value):
    self.args[item] = value
  def __len__(self):
    return len(self.args)
       
class InterpLlambda(InterpLfun):

  def arity(self, v):
    match v:
      case Function(name, params, body, env):
        return len(params)
      case ClosureTuple(args, arity):
        return arity
      case _:
        raise Exception('Llambda arity unexpected ' + repr(v))
      
  def interp_exp(self, e, env):
    match e:
      case Call(Name('arity'), [fun]):
        f = self.interp_exp(fun, env)
        return self.arity(f)
      case Uninitialized(ty):
        return None
      case FunRef(id, arity):
        return env[id]
      case Lambda(params, body):
        return Function('lambda', params, [Return(body)], env)
      case UncheckedCast(exp, ty):
        return self.interp_exp(exp, env)
      case Closure(arity, args):
        return ClosureTuple([self.interp_exp(arg, env) for arg in args], arity)
      case AllocateClosure(length, typ, arity):
        array = [None] * length
        return ClosureTuple(array, arity)
      case _:
        return super().interp_exp(e, env)
    
  def interp_stmt(self, s, env, cont):
    match s:
      # case AnnAssign(lhs, typ, value, simple):  # don't have simple in the python 3.10.6 ??
      case AnnAssign(lhs, typ, value):
        env[lhs.id] = self.interp_exp(value, env)
        return self.interp_stmts(cont, env)
      case Pass():
        return self.interp_stmts(cont, env)
      case _:
        return super().interp_stmt(s, env, cont)
        
