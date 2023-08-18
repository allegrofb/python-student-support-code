import ast
from ast import *
from utils import *
from x86_ast import *
import os
from typing import List, Tuple, Set, Dict
from graph import UndirectedAdjList, DirectedAdjList, topological_sort, transpose
import math
from dataflow_analysis import analyze_dataflow
from collections import defaultdict, deque

Binding = Tuple[Name, expr]
Temporaries = List[Binding]

##############################################################################
# copy from https://github.com/murcake/python-student-support-code
max_tuple_size = 50

def mk_tag(typ: Type) -> int:
    # extra 64 bits: 0 1-6 7-56 57-63
    # bit 0     : 0 - entire tag is a forwarding pointer //The lower 3 bits of a pointer are always zero in any case, because our tuples are 8-byte aligned.
    #             1 - not yet copied to the ToSpace
    # bit 1-6   : length of the tuple
    # bit 7-56  : pointer mask   //maximum tuple elem number = 50, 1 indicate its a pointer
    # bit 57-63 : unused
    if not isinstance(typ, TupleType):
        raise Exception(f"Expected a TupleType, got {typ}")
    l = len(typ.types)
    if l > max_tuple_size:
        raise Exception(f"The maximum size of tuples allowed is {max_tuple_size}")
    pointer_mask = as_bit_string(map(is_pointer, typ.types))[::-1]
    bits = f"{pointer_mask:>0{max_tuple_size}}{l:06b}1"
    print("********************",bits)
    return int(bits, 2)

def is_pointer(typ: Type) -> bool:
    return isinstance(typ, TupleType)

def as_bit_string(bs: Iterable[bool]) -> str:
    return "".join(str(int(x)) for x in bs)
##############################################################################

class Compiler:

    ############################################################################
    # Shrink
    ############################################################################
    
    def shrink_exp(self, e: expr) -> expr:
        # YOUR CODE HERE
        match e:
            case BinOp(left, Add(), right):
                return BinOp(self.shrink_exp(left), Add(), self.shrink_exp(right))
            case BinOp(left, Sub(), right):
                return BinOp(self.shrink_exp(left), Sub(), self.shrink_exp(right))
            case UnaryOp(USub(), v):
                return UnaryOp(USub(), self.shrink_exp(v))
            case IfExp(test, body, orelse):
                return IfExp(self.shrink_exp(test), self.shrink_exp(body), self.shrink_exp(orelse))
            case UnaryOp(Not(), v):
                return UnaryOp(Not(), self.shrink_exp(v))
            case BoolOp(And(), values):
                return IfExp(self.shrink_exp(values[0]), self.shrink_exp(values[1]), Constant(False))
            case BoolOp(Or(), values):
                return BoolOp(Or(), [self.shrink_exp(i) for i in values])
            case Compare(left, [cmp], [right]):
                return Compare(self.shrink_exp(left), [cmp], [self.shrink_exp(right)])
            case _:
                return e

    def shrink_stmt(self, s: stmt) -> stmt:
        # YOUR CODE HERE
        match s:
            case If(test, body, orelse):
                return If(self.shrink_exp(test), 
                            [self.shrink_stmt(i) for i in body], 
                            [self.shrink_stmt(i) for i in orelse])
            case Assign([Name(id)], value):
                return Assign([Name(id)], self.shrink_exp(value))
            case Expr(Call(Name('print'), [arg])):
                return Expr(Call(Name('print'), [self.shrink_exp(arg)]))
            case Expr(value):
                return Expr(self.shrink_exp(value))
            case While(test, body, []):
                return While(self.shrink_exp(test),
                          [self.shrink_stmt(i) for i in body], [])
            case Return(value):
                return Return(self.shrink_exp(value))
            case _:
                raise Exception('error in shrink_stmt, unexpected ' + repr(s))

    def shrink(self, p: Module) -> Module:
        match p:
            case Module(body):
                new_body = []
                main_body = []
                for stmt in body:
                    match stmt:
                        case FunctionDef(name, params, bod, dl, returns, comment):
                            new_bod = []
                            for s in bod:
                                new_bod.append(self.shrink_stmt(s))
                            new_body.append(FunctionDef(name, params, new_bod, dl, returns, comment))
                        case _:
                            main_body.append(self.shrink_stmt(stmt))
                main_body.append(Return(Constant(0)))
                new_body.append(FunctionDef('main', [], main_body, None, IntType(), None))
                print(new_body)
                return Module(new_body)
            case _:
                raise Exception('error in shrink, unexpected ' + repr(p))


    ############################################################################
    # Reveal Functions
    ############################################################################

    def reveal_exp(self, e: expr, func_refs: Dict) -> expr:
        # YOUR CODE HERE
        match e:
            case Name(n):
                if n in func_refs:
                    return FunRef(n, func_refs[n])
                return Name(n)
            case BinOp(left, Add(), right):
                return BinOp(self.reveal_exp(left, func_refs), Add(), self.reveal_exp(right, func_refs))
            case BinOp(left, Sub(), right):
                return BinOp(self.reveal_exp(left, func_refs), Sub(), self.reveal_exp(right, func_refs))
            case UnaryOp(USub(), v):
                return UnaryOp(USub(), self.reveal_exp(v, func_refs))
            case IfExp(test, body, orelse):
                return IfExp(self.reveal_exp(test, func_refs), self.reveal_exp(body, func_refs), self.reveal_exp(orelse, func_refs))
            case UnaryOp(Not(), v):
                return UnaryOp(Not(), self.reveal_exp(v, func_refs))
            case BoolOp(And(), values):
                return UnaryOp(And(), self.reveal_exp(v, func_refs))
            case BoolOp(Or(), values):
                return BoolOp(Or(), [self.reveal_exp(i, func_refs) for i in values])
            case Compare(left, [cmp], [right]):
                return Compare(self.reveal_exp(left, func_refs), [cmp], [self.reveal_exp(right, func_refs)])
            case Call(func, args):
                return Call(self.reveal_exp(func, func_refs), [self.reveal_exp(i, func_refs) for i in args])
            case Constant(v):
                return Constant(v)
            case _:
                raise Exception('error in reveal_exp, unexpected ' + repr(e))

    def reveal_stmt(self, s: stmt, func_refs: Dict) -> stmt:
        # YOUR CODE HERE
        match s:
            case If(test, body, orelse):
                return If(self.reveal_exp(test), 
                            [self.reveal_stmt(i, func_refs) for i in body], 
                            [self.reveal_stmt(i, func_refs) for i in orelse])
            case Assign([Name(id)], value):
                return Assign([Name(id)], self.reveal_exp(value, func_refs))
            case Expr(Call(Name('print'), [arg])):
                return Expr(Call(Name('print'), [self.reveal_exp(arg, func_refs)]))
            case Expr(value):
                return Expr(self.reveal_exp(value, func_refs))
            case While(test, body, []):
                return While(self.reveal_exp(test, func_refs),
                          [self.reveal_stmt(i, func_refs) for i in body], [])
            case Return(value):
                return Return(self.reveal_exp(value, func_refs))
            case _:
                raise Exception('error in reveal_stmt, unexpected ' + repr(s))

    def reveal_functions(self, p: Module) -> Module:
        match p:
            case Module(body):
                new_body = []

                func_refs = {}
                arity = 0
                for stmt in body:
                    match stmt:
                        case FunctionDef(name, params, bod, dl, returns, comment):
                            func_refs[name] = arity
                        case _:
                            raise Exception('error in reveal_functions, unexpected ' + repr(stmt))
                    arity += 1

                for stmt in body:
                    match stmt:
                        case FunctionDef(name, params, bod, dl, returns, comment):
                            new_bod = []
                            for s in bod:
                                new_bod.append(self.reveal_stmt(s, func_refs))
                            new_body.append(FunctionDef(name, params, new_bod, dl, returns, comment))
                        case _:
                            raise Exception('error in reveal_functions, unexpected ' + repr(stmt))
                print(new_body)
                return Module(new_body)
            case _:
                raise Exception('error in reveal_functions, unexpected ' + repr(p))


    ############################################################################
    # Limit Functions
    ############################################################################


    # def limit_functions(self, p: Module) -> Module:
    #     match p:
    #         case Module(body):
    #             new_body = []

    #             for stmt in body:
    #                 match stmt:
    #                     case FunctionDef(name, params, bod, dl, returns, comment):
    #                         new_bod = []
    #                         for s in bod:
    #                             new_bod.append(self.limit_stmt(s))
    #                         new_body.append(FunctionDef(name, params, new_bod, dl, returns, comment))
    #                     case _:
    #                         raise Exception('error in limit_functions, unexpected ' + repr(stmt))
    #             print(new_body)
    #             return Module(new_body)
    #         case _:
    #             raise Exception('error in limit_functions, unexpected ' + repr(p))
    ############################################################################
    # Expose Allocation
    ############################################################################

    def expose_exp(self, e: expr) -> Tuple[expr, List[expr]]:
        # YOUR CODE HERE
        match e:
            case BinOp(left, cmp, right):
                left, ss = self.expose_exp(left)
                right, ss2 = self.expose_exp(right)
                return BinOp(left, cmp, right), ss+ss2
            # case UnaryOp(USub(), v):
            #     return UnaryOp(USub(), v), tmpVars
            # case Compare(left, [cmp], [right]):
            #     return Compare(left, [cmp], [right]), tmpVars
            case IfExp(test, body, orelse):
                test, ss = self.expose_exp(test)
                body, ss2 = self.expose_exp(body)
                orelse, ss3 = self.expose_exp(orelse)
                return IfExp(test, body, orelse), ss+ss2+ss3
            case Name(id):
                return Name(id), []
            case Constant(value):
                return Constant(value), []
            case Subscript(tup, Constant(index), Load()):
                tup,ss = self.expose_exp(tup)
                return Subscript(tup, Constant(index), Load()), ss
            case ast.Tuple(es, Load()):
                # x0 = e0
                # ...
                # xn–1 = en–1
                # if global_value(free_ptr) + bytes < global_value(fromspace_end):
                # 	0
                # else:
                # 	collect(bytes)          //<---------- collect function c code
                # v = allocate(len, type)     //<---------- allocate function c code
                # v[0] = x0                   //<---------- access tuple
                # ...
                # v[n – 1] = xn–1
                # v                           //<---------- v tuple varialbe
                stmts = []
                ts = []
                ss = []
                for e in es:
                    tmp = Name(generate_name('tmpVar'))
                    # breakpoint()
                    match e:
                        case Constant(value) if isinstance(value, bool):
                            ts.append((tmp,BoolType()))
                        case Constant(value):
                            ts.append((tmp,IntType()))
                        case ast.Tuple(value):
                            ts.append((tmp,e.has_type))
                            e, ss = self.expose_exp(e)
                        case _:
                            raise Exception('error in expose_exp, unexpected ' + repr(e))
                    stmts.append(Assign([tmp], e))

                bytes = Constant(len(ts)*8 + 8)
                fromspace_end = GlobalValue('fromspace_end')
                free_ptr = GlobalValue('free_ptr')
                test = Compare(BinOp(free_ptr, Add(), bytes), [Lt()], [fromspace_end])
                orelse = [Collect(bytes)]  # Collect function should be stmt
                stmts.append(If(test,[],orelse))

                v = Name(generate_name('tmpVar'))
                stmts.append(Assign([v], Allocate(len(ts), TupleType([i[1] for i in ts]))))

                for index,i in enumerate(ts):
                    stmts.append(Assign([Subscript(v, Constant(index), Store())], i[0]))

                return v, ss+stmts

            case Call(FunRef(name, arity), args):
                stmts = []
                arguments = []
                for arg in args:
                    aa, ss = self.expose_exp(arg)
                    stmts.extend(ss)
                    arguments.append(aa)
                return Call(FunRef(name, arity), arguments), stmts
            case _:
                # return e, []
                raise Exception('error in expose_exp, unexpected ' + repr(e))

    def expose_stmt(self, s: stmt) -> stmt:
        # YOUR CODE HERE
        match s:
            case Assign([Name(id)], value):
                value, ss = self.expose_exp(value)
                return ss + [Assign([Name(id)], value)]
            case Expr(Call(Name('print'), [arg])):
                arg, ss = self.expose_exp(arg)
                return ss + [Expr(Call(Name('print'), [arg]))]
            case Return(value):
                value, ss = self.expose_exp(value)
                return ss+[Return(value)]
            # case Assign([Subscript(tup, Constant(index), Store())], value):                
            #     return
            # case Expr(value):
            #     stmts = []
            #     value, tmp = self.expose_exp(value)
            #     for i in tmp:
            #         stmts.append(Assign([i[0]], i[1]))
            #     stmts.append(Expr(value))
            #     return stmts
            # case If(test, body, orelse):
            #     stmts = []
            #     test, tmp = self.expose_exp(test)
            #     for i in tmp:
            #         stmts.append(Assign([i[0]], i[1]))
            #     body_stmts = []
            #     for i in body:
            #         body_stmts.extend(self.expose_stmt(i))
            #     orelse_stmts = []
            #     for i in orelse:
            #         orelse_stmts.extend(self.expose_stmt(i))
            #     stmts.append(If(test,body_stmts,orelse_stmts))
            #     return stmts
            # case While(test, body, []):
            #     stmts = []
            #     test, tmp = self.expose_exp(test)
            #     for i in tmp:
            #         stmts.append(Assign([i[0]], i[1]))
            #     body_stmts = []
            #     for i in body:
            #         body_stmts.extend(self.expose_stmt(i))
            #     stmts.append(While(test,body_stmts,[]))
            #     return stmts
            case _:
                raise Exception('error in expose_stmt, unexpected ' + repr(s))

    def expose_allocation(self, p: Module) -> Module:
        # YOUR CODE HERE
        match p:
            case Module(body):
                new_body = []
                for stmt in body:
                    match stmt:
                        case FunctionDef(name, params, bod, dl, returns, comment):
                            new_bod = []
                            for s in bod:
                                new_bod.extend(self.expose_stmt(s))
                            new_body.append(FunctionDef(name, params, new_bod, dl, returns, comment))
                        case _:
                            raise Exception('error in expose_allocation, unexpected ' + repr(stmt))
                print(new_body)
                return Module(new_body)
            case _:
                raise Exception('error in expose_allocation, unexpected ' + repr(p))

    ############################################################################
    # Remove Complex Operands
    ############################################################################

    def rco_exp(self, e: expr, need_atomic: bool) -> Tuple[expr, Temporaries]:
        # YOUR CODE HERE
        match e:
            case Name(id):
                return Name(id), []
            case Constant(value):
                return Constant(value), []
            case Call(Name('input_int'), []):
                tmpVars = []
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, Call(Name('input_int'), [])))
                    return tmp, tmpVars
                else:
                    return Call(Name('input_int'), []), tmpVars
            case Call(func, args):
                tmpVars = []
                tmp_args = []
                for arg in args:
                    if not isinstance(arg, (Name, Constant, GlobalValue, )):
                        arg2, tmp = self.rco_exp(arg, need_atomic=True)
                        tmpVars.extend(tmp)
                        arg = Name(generate_name('tmpVar'))
                        tmpVars.append((arg, arg2))
                        tmp_args.append(arg)
                    else:
                        tmp_args.append(arg)
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, Call(func, tmp_args)))
                    return tmp, tmpVars
                else:
                    return Call(func, tmp_args), tmpVars
            case BinOp(left, Add(), right):
                tmpVars = []
                if not isinstance(left, (Name, Constant, GlobalValue, )):
                    left2, tmp = self.rco_exp(left, need_atomic=False)
                    tmpVars.extend(tmp)
                    left = Name(generate_name('tmpVar'))
                    tmpVars.append((left, left2))
                if not isinstance(right, (Name, Constant, GlobalValue,)):
                    right2, tmp = self.rco_exp(right, need_atomic=False)
                    tmpVars.extend(tmp)
                    right = Name(generate_name('tmpVar'))                        
                    tmpVars.append((right, right2))
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, BinOp(left, Add(), right)))
                    return tmp, tmpVars
                else:
                    return BinOp(left, Add(), right), tmpVars
            case BinOp(left, Sub(), right):
                tmpVars = []
                if not isinstance(left, (Name, Constant, GlobalValue,)):
                    left2, tmp = self.rco_exp(left, need_atomic=False)
                    tmpVars.extend(tmp)
                    left = Name(generate_name('tmpVar'))
                    tmpVars.append((left, left2))
                if not isinstance(right, (Name, Constant, GlobalValue,)):
                    right2, tmp = self.rco_exp(right, need_atomic=False)
                    tmpVars.extend(tmp)
                    right = Name(generate_name('tmpVar'))
                    tmpVars.append((right, right2))
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, BinOp(left, Sub(), right)))
                    return tmp, tmpVars
                else:
                    return BinOp(left, Sub(), right), tmpVars
            case UnaryOp(USub(), v):
                tmpVars = []
                if not isinstance(v, (Name, Constant, GlobalValue,)):
                    v2, tmp = self.rco_exp(v, need_atomic=False)
                    tmpVars.extend(tmp)
                    v = Name(generate_name('tmpVar'))
                    tmpVars.append((v, v2))
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, UnaryOp(USub(), v)))
                    return tmp, tmpVars
                else:
                    return UnaryOp(USub(), v), tmpVars
            case UnaryOp(Not(), v):
                tmpVars = []
                if not isinstance(v, (Name, Constant, GlobalValue,)):
                    v2, tmp = self.rco_exp(v, need_atomic=False)
                    tmpVars.extend(tmp)
                    v = Name(generate_name('tmpVar'))
                    tmpVars.append((v, v2))
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, UnaryOp(Not(), v)))
                    return tmp, tmpVars
                else:
                    return UnaryOp(Not(), v), tmpVars
            case Compare(left, [cmp], [right]):
                tmpVars = []
                if not isinstance(left, (Name, Constant, GlobalValue,)):
                    left2, tmp = self.rco_exp(left, need_atomic=True)
                    tmpVars.extend(tmp)
                    left = Name(generate_name('tmpVar'))
                    tmpVars.append((left, left2))
                if not isinstance(right, (Name, Constant, GlobalValue,)):
                    right2, tmp = self.rco_exp(right, need_atomic=True)
                    tmpVars.extend(tmp)
                    right = Name(generate_name('tmpVar'))
                    tmpVars.append((right, right2))
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, Compare(left, [cmp], [right])))
                    return tmp, tmpVars
                else:
                    return Compare(left, [cmp], [right]), tmpVars
            case IfExp(test, body, orelse):
                tmpVars = []
                if not isinstance(test, (Name, Constant, GlobalValue,)):
                    test2, tmp = self.rco_exp(test, need_atomic=False)
                    tmpVars.extend(tmp)
                    test = Name(generate_name('tmpVar'))
                    tmpVars.append((test, test2))
                if not isinstance(body, (Name, Constant,  GlobalValue, Compare,)):  # branch have side-effect code, insert Begin expr
                    body2, tmp = self.rco_exp(body, need_atomic=False) # it's ok for need_atomic=True ?
                    stmts = []
                    for i in tmp:
                        stmts.append(Assign([i[0]], i[1]))
                    body = Begin(stmts,body2)
                if not isinstance(orelse, (Name, Constant,  GlobalValue, Compare,)):
                    orelse2, tmp = self.rco_exp(orelse, need_atomic=False)
                    stmts = []
                    for i in tmp:
                        stmts.append(Assign([i[0]], i[1]))
                    orelse = Begin(stmts,orelse2)
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, IfExp(test, body, orelse)))
                    return tmp, tmpVars
                else:
                    return IfExp(test, body, orelse), tmpVars
            case GlobalValue(name):
                return GlobalValue(name), []
            case Allocate(length, ty):
                return Allocate(length, ty), []
            case Begin(body, result):
                tmpVars = []
                stmts = []
                for s in body:
                    stmts.extend(self.rco_stmt(s))
                return Begin(stmts, result), tmpVars
            case Subscript(tup, Constant(index), Load()):
                tmpVars = []
                if not isinstance(tup, (Name, Constant, GlobalValue,)):
                    tup2, tmp = self.rco_exp(tup, need_atomic=True)
                    tmpVars.extend(tmp)
                    tup = Name(generate_name('tmpVar'))
                    tmpVars.append((tup, tup2))
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, Subscript(tup, Constant(index), Load())))
                    return tmp, tmpVars
                else:
                    return Subscript(tup, Constant(index), Load()), tmpVars
            case _:
                raise Exception('error in rco_exp, unexpected ' + repr(e))

    def rco_stmt(self, s: stmt) -> List[stmt]:
        # YOUR CODE HERE
        match s:
            case Assign([Name(id)], value):
                stmts = []
                value, tmp = self.rco_exp(value, need_atomic=False)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                stmts.append(Assign([Name(id)], value))
                return stmts
            case Collect(value):
                stmts = []
                value, tmp = self.rco_exp(value, need_atomic=False)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                stmts.append(Collect(value))
                return stmts
            case Assign([Subscript(Name(id), Constant(index), Store())], value):
                stmts = []
                value, tmp = self.rco_exp(value, need_atomic=False)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                stmts.append(Assign([Subscript(Name(id), Constant(index), Store())], value))
                return stmts
            case Expr(Call(Name('print'), [arg])):
                stmts = []
                arg, tmp = self.rco_exp(arg, need_atomic=True)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                stmts.append(Expr(Call(Name('print'), [arg])))
                return stmts
            case Expr(value):
                stmts = []
                value, tmp = self.rco_exp(value, need_atomic=False)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                stmts.append(Expr(value))
                return stmts
            case If(test, body, orelse):
                stmts = []
                test, tmp = self.rco_exp(test, need_atomic=False)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                body_stmts = []
                for i in body:
                    body_stmts.extend(self.rco_stmt(i))
                orelse_stmts = []
                for i in orelse:
                    orelse_stmts.extend(self.rco_stmt(i))
                stmts.append(If(test,body_stmts,orelse_stmts))
                return stmts
            case While(test, body, []):
                stmts = []
                test, tmp = self.rco_exp(test, need_atomic=False)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                body_stmts = []
                for i in body:
                    body_stmts.extend(self.rco_stmt(i))
                stmts.append(While(test,body_stmts,[]))
                return stmts
            case Return(value):
                stmts = []
                value, tmp = self.rco_exp(value, need_atomic=True)
                for i in tmp:
                    stmts.append(Assign([i[0]], i[1]))
                stmts.append(Return(value))
                return stmts
            case _:
                raise Exception('error in rco_stmt, unexpected ' + repr(s))

    def remove_complex_operands(self, p: Module) -> Module:
        # YOUR CODE HERE
        match p:
            case Module(body):
                new_body = []
                for stmt in body:
                    match stmt:
                        case FunctionDef(name, params, bod, dl, returns, comment):
                            new_bod = []
                            for s in bod:
                                new_bod.extend(self.rco_stmt(s))
                            new_body.append(FunctionDef(name, params, new_bod, dl, returns, comment))
                        case _:
                            raise Exception('error in remove_complex_operands, unexpected ' + repr(stmt))
                print(new_body)
                return Module(new_body)
            case _:
                raise Exception('error in remove_complex_operands, unexpected ' + repr(p))

    
    ############################################################################
    # Explicate Control
    ############################################################################

    def create_block(self, stmts: List[stmt], basic_blocks: Dict) -> Goto:
        label = label_name(generate_name('block'))
        basic_blocks[label] = stmts
        return Goto(label)

    def explicate_effect(self, e: expr, cont: List[stmt], basic_blocks: Dict) -> List[stmt]:
        match e:
            case IfExp(test, body, orelse):
                body = self.explicate_effect(body, cont, basic_blocks)
                orelse = self.explicate_effect(orelse, cont, basic_blocks)
                return self.explicate_pred(test, body, orelse, basic_blocks) + cont
            case Call(func, args):
            # case Call(Name('input_int'), args):
                # for arg in args:
                #     self.explicate_effect(arg, cont, basic_blocks)
                return [Expr(Call(func, args))] + cont
            case Begin(body, result):
                for s in body:
                    cont.extend(self.explicate_stmt(s, [], basic_blocks))
                return result
            case _:
                return [e] + cont
                
    def explicate_assign(self, rhs: expr, lhs: expr, cont: List[stmt], basic_blocks: Dict) -> List[stmt]:
        match rhs:
            case IfExp(test, body, orelse):
                if not isinstance(test, Constant):
                    goto = self.create_block(cont, basic_blocks)
                    cont = []
                    if not isinstance(body, (Constant,Name,)):
                        body = self.explicate_effect(body, cont, basic_blocks) # for Begin
                    body = cont + [Assign([lhs], body)] + [goto] 
                    cont = []
                    if not isinstance(orelse, (Constant,Name,)):
                        orelse = self.explicate_effect(orelse, cont, basic_blocks) # for Begin
                    orelse = cont + [Assign([lhs], orelse)] + [goto] 
                    return self.explicate_pred(test, body, orelse, basic_blocks)
                else:
                    body = [Assign([lhs], body)] 
                    orelse = [Assign([lhs], orelse)] 
                    return self.explicate_pred(test, body, orelse, basic_blocks) + cont
            case Begin(body, result):
                # new_body = [Assign([lhs], result)] + cont
                # for s in reversed(body):
                #     new_body = self.explicate_stmt(s, new_body, basic_blocks)
                # return new_body
                goto = self.create_block([Assign([lhs], result)] + cont, basic_blocks)
                new_body = [goto]
                for s in reversed(body):
                    new_body = self.explicate_stmt(s, new_body, basic_blocks)
                return new_body
            # case Call(FunRef(name='inc', arity=0), [Constant(41)]):
            # case Call(func, args):
            #     return
            case _:
                return [Assign([lhs], rhs)] + cont
                
    def explicate_pred(self, cnd: expr, thn: List[stmt], els: List[stmt], basic_blocks: Dict) -> List[stmt]:
        match cnd:
            case Compare(left, [op], [right]):
                goto_thn = self.create_block(thn, basic_blocks)
                goto_els = self.create_block(els, basic_blocks)
                return [If(cnd, [goto_thn], [goto_els])]
            case Constant(True):
                return thn
            case Constant(False):
                return els
            case UnaryOp(Not(), operand):
                return self.explicate_pred(operand, els, thn, basic_blocks)
            case IfExp(test, body, orelse):
                goto_thn = self.create_block(thn, basic_blocks)
                goto_els = self.create_block(els, basic_blocks)
                body = [If(body, [goto_thn], [goto_els])]        # body and orelse won't be IfExp
                orelse = [If(orelse, [goto_thn], [goto_els])]
                return self.explicate_pred(test, body, orelse, basic_blocks)
            case Begin(body, result):
                raise Exception("Begin")
            case _:
                return [If(Compare(cnd, [Eq()], [Constant(False)]),
                        [self.create_block(els, basic_blocks)],
                        [self.create_block(thn, basic_blocks)])]
    
    def explicate_tail(self, e: expr, cont: List[stmt], basic_blocks: Dict) -> List[stmt]:
        match e:
            case IfExp(test, body, orelse):
                body = self.explicate_effect(body, cont, basic_blocks)
                orelse = self.explicate_effect(orelse, cont, basic_blocks)
                return self.explicate_pred(test, body, orelse, basic_blocks) + cont
            case Call(func, args):
                return [Expr(Call(func, args))] + cont
            case Begin(body, result):
                for s in body:
                    cont.extend(self.explicate_stmt(s, [], basic_blocks))
                return Return(result)
            case _:
                return [Return(e)] + cont

    def explicate_stmt(self, s: stmt, cont: List[stmt], basic_blocks: Dict) -> List[stmt]:
        match s:
            case Assign([lhs], rhs):
                return self.explicate_assign(rhs, lhs, cont, basic_blocks)
            case Expr(value):
                return self.explicate_effect(value, cont, basic_blocks)
            case If(test, body, orelse):
                thn = []
                for s in body:
                    thn.extend(self.explicate_stmt(s, [], basic_blocks))
                els = []
                for s in orelse:
                    els.extend(self.explicate_stmt(s, [], basic_blocks))
                goto_thn = self.create_block(thn+cont, basic_blocks)
                goto_els = self.create_block(els+cont, basic_blocks)
                return [If(test, [goto_thn], [goto_els])]
            case While(test, body, []):
                label = label_name(generate_name('block'))
                body_stmts = []
                for s in body:
                    body_stmts.extend(self.explicate_stmt(s, [], basic_blocks))
                goto_els = self.create_block(cont, basic_blocks)
                body = body_stmts + [Goto(label)]
                basic_blocks[label] = self.explicate_pred(test, body, [goto_els], basic_blocks)
                return [Goto(label)]
            case Collect(size):
                return [Collect(size)] + cont
            case Return(expr):
                return self.explicate_tail(expr, cont, basic_blocks)
            case _:
                raise Exception('error in explicate_stmt, unexpected ' + repr(s))

    def explicate_control(self, p: Module) -> CProgramDefs:
        match p:
            case Module(body):
                new_body = []
                for stmt in body:
                    match stmt:
                        case FunctionDef(name, params, bod, dl, returns, comment):
                            basic_blocks = {}
                            new_bod = []
                            for s in reversed(bod):
                                new_bod = self.explicate_stmt(s, new_bod, basic_blocks)
                            basic_blocks[label_name(name+"_start")] = new_bod
                            new_body.append(FunctionDef(name, params, basic_blocks, None, returns, None))
                        case _:
                            raise Exception('error in remove_complex_operands, unexpected ' + repr(stmt))
                print(new_body)
                return CProgramDefs(new_body)

    ############################################################################
    # Select Instructions
    ############################################################################

    def select_arg(self, e: expr) -> arg:
        # YOUR CODE HERE
        match e:
            case Name(n):
                return Variable(n)
            case Constant(v):
                return Immediate(int(v))
            case GlobalValue(name):
                return Global(name)
            case _:
                raise Exception('error in select_arg, unexpected ' + repr(e))

    def select_stmt(self, s: stmt) -> List[instr]:
        # YOUR CODE HERE
        match s:
            case Assign([Subscript(tup, Constant(index), Store())], value):
                instrs = []
                instrs.append(Instr('movq', [self.select_arg(tup), Reg('r11')]))
                instrs.append(Instr('movq', [self.select_arg(value), Deref('r11', 8*(index+1))]))
                return instrs
            case Assign([arg], value):
                match value:
                    case Constant(v):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(value), self.select_arg(arg)]))
                        return instrs
                    case Call(Name('input_int'), []):
                        instrs = []
                        instrs.append(Callq(label_name("read_int"), 0))
                        instrs.append(Instr('movq', [Reg('rax'), self.select_arg(arg)]))
                        return instrs
                    case Call(FunRef(name, arity), args):
                        param_regs = [Reg(i) for i in 'rdi rsi rdx rcx r8 r9'.split(' ')]
                        instrs = []
                        for i,a in enumerate(args):
                            instrs.append(Instr('movq', [self.select_arg(a), param_regs[i]]))
                        # instrs.append(Callq(label_name(name+'_start'), len(args)))
                        instrs.append(Callq(label_name(name), len(args)))
                        instrs.append(Instr('movq', [Reg('rax'), self.select_arg(arg)]))
                        return instrs
                    case BinOp(left, Add(), right):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(left), self.select_arg(arg)]))
                        instrs.append(Instr('addq', [self.select_arg(right), self.select_arg(arg)]))
                        return instrs
                    case BinOp(left, Sub(), right):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(left), self.select_arg(arg)]))
                        instrs.append(Instr('subq', [self.select_arg(right), self.select_arg(arg)]))
                        return instrs
                    case UnaryOp(USub(), v):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(v), self.select_arg(arg)]))
                        instrs.append(Instr('negq', [self.select_arg(arg)]))
                        return instrs
                    case Begin(body, result):
                        instrs = []
                        for i in body:
                            instrs.extend(self.select_stmt(i))
                        instrs.append(Instr('movq', [self.select_arg(result), self.select_arg(arg)]))
                        return instrs
                    case Subscript(tup, Constant(index), Load()):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(tup), Reg('r11')]))
                        instrs.append(Instr('movq', [Deref('r11', 8*(index+1)), self.select_arg(arg)]))
                        return instrs
                    case Allocate(length, ty):
                        instrs = []
                        instrs.append(Instr('movq', [Global('free_ptr'), Reg('r11')]))
                        instrs.append(Instr('addq', [Immediate(8*(length + 1)), Global('free_ptr')]))
                        tag = mk_tag(ty)
                        instrs.append(Instr('movq', [Immediate(tag), Deref('r11', 0)]))
                        instrs.append(Instr('movq', [Reg('r11'), self.select_arg(arg)]))
                        return instrs
                    case Name(n):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(value), self.select_arg(arg)]))
                        return instrs
                    case _:
                        raise Exception('error in select_stmt, unexpected ' + repr(s))
                return
            case Expr(Call(Name('print'), [arg])):
                instrs = []
                instrs.append(Instr('movq', [self.select_arg(arg), Reg('rdi')]))
                instrs.append(Callq(label_name("print_int"), 1))
                return instrs
            case Expr(value):
                instrs = []
                instrs.extend(self.select_stmt(value))
                return instrs
            case Return(arg):
                instrs = []
                instrs.append(Instr('movq', [self.select_arg(arg), Reg('rax')]))
                # instrs.append(Jump(label_name("conclusion")))
                return instrs
            case Goto(label):
                instrs = []
                instrs.append(Jump(label_name(label)))
                return instrs
            # case If(test, body, orelse):
            case If(test, [Goto(label1)], [Goto(label2)]):
                match test:
                    case Compare(left, [cmp], [right]):
                        instrs = []
                        instrs.append(Instr('cmpq', [self.select_arg(right), self.select_arg(left)]))
                        if isinstance(cmp,(Lt,)):
                            instrs.append(JumpIf('l',label_name(label1)))
                        elif isinstance(cmp,(LtE,)):
                            instrs.append(JumpIf('le',label_name(label1)))
                        elif isinstance(cmp,(Gt,)):
                            instrs.append(JumpIf('g',label_name(label1)))
                        elif isinstance(cmp,(GtE,)):
                            instrs.append(JumpIf('ge',label_name(label1)))
                        elif isinstance(cmp,(Eq,)):
                            instrs.append(JumpIf('e',label_name(label1)))
                        elif isinstance(cmp,(NotEq,)):
                            instrs.append(JumpIf('ne',label_name(label1)))
                        else:
                            raise Exception('error in Compare, unexpected ' + repr(cmp))
                        instrs.append(Jump(label_name(label2)))
                        return instrs
                    case UnaryOp(Not(), v):
                        instrs = []
                        instrs.append(Instr('xorq', [Immediate(1), self.select_arg(v)]))
                        return instrs
                    case _:
                        raise Exception('error in select_stmt, unexpected ' + repr(test))
            case Collect(size):
                instrs = []
                instrs.append(Instr('movq', [Reg('r15'), Reg('rdi')]))
                instrs.append(Instr('movq', [Immediate(size), Reg('rsi')]))
                instrs.append(Callq(label_name("collect"), 2))
                return instrs
            case _:
                raise Exception('error in select_stmt, unexpected ' + repr(s))

    def select_instructions(self, p: CProgramDefs) -> X86ProgramDefs:
        # YOUR CODE HERE
        match p:
            case CProgramDefs(body):
                result = []
                for stmt in body:
                    match stmt:
                        case FunctionDef(name, params, bod, dl, returns, comment):
                            basic_blocks = {}
                            for l,ss in bod.items():
                                instrs = []
                                for s in ss:
                                    # print(s)
                                    instrs.extend(self.select_stmt(s))
                                basic_blocks[l] = instrs
                            param_instrs = []
                            param_regs = [Reg(i) for i in 'rdi rsi rdx rcx r8 r9'.split(' ')]
                            for i, p in enumerate(params):
                                param_instrs.append(Instr('movq', [param_regs[i], Variable(p[0])]))
                            basic_blocks[name+"_start"] = param_instrs + basic_blocks[name+"_start"]
                            result.append(FunctionDef(name, [], basic_blocks, None, returns, None))
                        case _:
                            raise Exception('error in select_instructions, unexpected ' + repr(stmt))
                print(result)
                return X86ProgramDefs(result)
            case _:
                raise Exception('error in select_instructions, unexpected ' + repr(p))

    ###########################################################################
    # Uncover Live
    ###########################################################################

    def read_vars(self, i: instr) -> Set[location]:
        # YOUR CODE HERE
        match i:
            case Jump(label):
                return set()
            case JumpIf(e, label):
                return set()
            case Instr('cmpq', args):
                result = set()
                if not isinstance(args[0],(Immediate,)):
                    result.add(args[0])
                if not isinstance(args[-1],(Immediate,)):
                    result.add(args[-1])
                return result                    
            case Instr('addq', args):
                if not isinstance(args[0],(Immediate,)):
                    return {args[0],args[-1]}
                else:
                    return {args[-1]}
            case Instr('subq', args):
                if not isinstance(args[0],(Immediate,)):
                    return {args[0],args[-1]}
                else:
                    return {args[-1]}
            case Instr(name, args):
                if not isinstance(args[0],(Immediate,)):
                    return {args[0]}
                else:
                    return set()
            case Callq(name, num):
                return {Reg(n) for n in 'rdi rsi rdx rcx r8 r9'.split(' ')[:num]}
            case _:
                raise Exception('error in read_vars, unexpected ' + repr(i))
                
    def write_vars(self, i: instr) -> Set[location]:
        # YOUR CODE HERE
        match i:
            case Jump(label):
                return set()
            case JumpIf(e, label):
                return set()
            case Instr('cmpq', args):
                return set()
            case Callq(name, num):
                return {Reg(n) for n in 'rax rcx rdx rsi rdi r8 r9 r10 r11'.split(' ')}
            case Instr(name, args):
                return {args[-1]}
            case _:
                raise Exception('error in write_vars, unexpected ' + repr(i))

    def uncover_live(self, p: X86ProgramDefs) -> Dict[str, Dict[instr, Set[location]]]:
        # YOUR CODE HERE
        match p:
            case X86ProgramDefs(defs):
                result = {}
                for stmt in defs:
                    match stmt:
                        case FunctionDef(name, params, body, dl, returns, comment):
                            graph = DirectedAdjList() # control flow graph (CFG)
                            worklist = deque([name+"_start"])
                            visited = set()
                            while worklist:
                                head = worklist.popleft()
                                if head in visited:
                                    continue
                                visited.add(head)
                                for instr in body[head]:
                                    if isinstance(instr, (Jump, JumpIf)):
                                        graph.add_edge(instr.label, head)
                                        worklist.append(instr.label)

                            def transfer(node: str, live_after: set[location]) -> set[location]:
                                for instr in reversed(body[node]):
                                    if not isinstance(instr, (Jump, JumpIf)):
                                        r_set = self.read_vars(instr)
                                        w_set = self.write_vars(instr)
                                        live_after = (live_after - w_set) | r_set
                                return live_after

                            live_before_block = analyze_dataflow(graph, transfer, set(), lambda a, b: a | b)
                            if len(live_before_block.keys()) == 0:
                                live_before_block[name+"_start"] = set()

                            instr_dict = {}
                            after = set()
                            for v in live_before_block:
                                for i in reversed(body[v]):
                                    if isinstance(i, (Jump, JumpIf)):
                                        # print(v, 'jump to: ',graph.out[v])
                                        instr_dict[i] = live_before_block[i.label]
                                        after = live_before_block[i.label]
                                    else:
                                        instr_dict[i] = after
                                    r = self.read_vars(i)
                                    w = self.write_vars(i)
                                    before = (after - w).union(r)
                                    after = before
                            result[name] = instr_dict
                        case _:
                            raise Exception('error in select_instructions, unexpected ' + repr(stmt))

                return result
            case _:
                raise Exception('error in uncover_live, unexpected ' + repr(p))

    ############################################################################
    # Build Interference
    ############################################################################

    def build_interference(self, p: X86ProgramDefs,
                           live_after: Dict[str, Dict[instr, Set[location]]]) -> Dict[str, UndirectedAdjList]:
        # YOUR CODE HERE
        match p:
            case X86ProgramDefs(defs):
                result = {}
                for stmt in defs:
                    match stmt:
                        case FunctionDef(name, params, body, dl, returns, comment):
                            graph = UndirectedAdjList()
                            for l, ss in body.items():
                                for i in ss:
                                    match i:
                                        case Instr('movq', [s,d]):
                                            for v in live_after[name][i]:
                                                if v != s and v != d:
                                                    graph.add_edge(d,v)
                                        case _:
                                            w = self.write_vars(i)
                                            for d in w:
                                                for v in live_after[name][i]:
                                                    if d != v:
                                                        graph.add_edge(d,v)
                            result[name] = graph
                        case _:
                            raise Exception('error in build_interference, unexpected ' + repr(stmt))
                return result
            case _:
                raise Exception('error in build_interference, unexpected ' + repr(p))
        

    ############################################################################
    # Allocate Registers
    ############################################################################

    # Returns the coloring and the set of spilled variables.
    def color_graph(self, graph: UndirectedAdjList,
                    variables: Set[location]) -> Tuple[Dict[location, int], Set[location]]:
        # YOUR CODE HERE
        from priority_queue import PriorityQueue
        L = {}
        for v in variables: # add variables
            L[v] = []
        def less(x, y):
            return len(L[x.key]) < len(L[y.key])
        Q = PriorityQueue(less)
        for k, v in L.items():
            Q.push(k)       # create priority queue

        color = {}
        while not Q.empty():
            # print(Q)
            k = Q.pop()     # pick one variable
            if k in {Reg(n) for n in 'rax rcx rdx rsi rdi r8 r9 r10 r11 rbx r12 r13 r14 rsp rbp r15'.split(' ')}:
                continue
            if isinstance(k, (Global,Deref,)):
                continue
            adj_k = graph.adjacent(k) # get other interference variable
            color_list = []
            for i in adj_k:
                if i in color:
                    color_list.append(color[i]) # get already assign color
            low_color = 0
            for i in color_list:
                if low_color in color_list:
                    low_color += 1    # get lowest color
            color[k] = low_color      # assign lowest color
            for i in adj_k:
                if low_color not in L[i]:
                    L[i].append(low_color)  # update L
                    Q.increase_key(i)       # update priority queue
        # print(L)
        return color, variables

    def allocate_registers(self, p: X86ProgramDefs,
                           graph: Dict[str, UndirectedAdjList]) -> X86ProgramDefs:
        # YOUR CODE HERE

        result = []
        for stmt in p.defs:
            match stmt:
                case FunctionDef(name, params, bod, dl, returns, comment):

                    var = graph[name].vertices()
                    # print(var)
                    color, var = self.color_graph(graph[name], var) # call coloring algorithm, get coloring variables
                    # print(color)
                    body = {}
                    for l, ss in bod.items():
                        instrs = []
                        for i in ss:
                            match i:
                                case Instr(n, [arg]):
                                    if arg in color:
                                        if color[arg] == 0:
                                            arg = Reg('rcx')
                                        elif color[arg] == 1:
                                            arg = Reg('rbx')
                                        elif color[arg] > 1:
                                            arg = Deref('rbp',-(color[arg]-1)*8)
                                    elif isinstance(arg, Variable):
                                        arg = Reg('rcx')
                                    instrs.append(Instr(n,[arg]))
                                case Instr(n, [arg1,arg2]):
                                    if arg1 in color:
                                        if color[arg1] == 0:
                                            arg1 = Reg('rcx')
                                        elif color[arg1] == 1:
                                            arg1 = Reg('rbx')
                                        elif color[arg1] > 1:
                                            arg1 = Deref('rbp',-(color[arg1]-1)*8)
                                    elif isinstance(arg1, Variable):
                                        arg1 = Reg('rcx')
                                    if arg2 in color:
                                        if color[arg2] == 0:
                                            arg2 = Reg('rcx')
                                        elif color[arg2] == 1:
                                            arg2 = Reg('rbx')
                                        elif color[arg2] > 1:
                                            arg2 = Deref('rbp',-(color[arg2]-1)*8)
                                    elif isinstance(arg2, Variable):
                                        arg2 = Reg('rcx')
                                    instrs.append(Instr(n,[arg1,arg2]))
                                case _:
                                    instrs.append(i)                            
                        body[l] = instrs

                    result.append(FunctionDef(name, params, body, dl, returns, comment))

                case _:
                    raise Exception('error in build_interference, unexpected ' + repr(stmt))
        print(result)
        p = X86ProgramDefs(result)
        setattr(p, 'calleesaved', ['rbx'])
        return p

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes(self, pseudo_x86: X86ProgramDefs) -> X86ProgramDefs:
        # YOUR CODE HERE
        live_after = self.uncover_live(pseudo_x86)
        # for k,v in live_after.items():
        #    print(k,v)
        graph = self.build_interference(pseudo_x86, live_after)
        # print(graph.show())
        return self.allocate_registers(pseudo_x86, graph)

    ###########################################################################
    # Patch Instructions
    ###########################################################################

    def patch_instructions(self, p: X86ProgramDefs) -> X86ProgramDefs:
        # YOUR CODE HERE
        result = []
        for stmt in p.defs:
            match stmt:
                case FunctionDef(fname, params, bod, dl, returns, comment):
                    body = {}
                    for l,ss in bod.items():
                        instrs = []
                        for i in ss:
                            match i:
                                case Instr(name, [deref1, deref2]):
                                    if name =='movq' and deref1 == deref2:
                                        pass
                                    elif isinstance(deref1, (Deref,)) and isinstance(deref2, (Deref,)) :
                                        instrs.append(Instr('movq', [deref1,Reg('rax')]))
                                        instrs.append(Instr(name, [Reg('rax'),deref2]))
                                    elif name == 'cmpq' and isinstance(deref1, (Immediate,)) and isinstance(deref2, (Immediate,)) :
                                        instrs.append(Instr('movq', [deref2,Reg('rax')]))
                                        instrs.append(Instr(name, [deref1,Reg('rax')]))
                                    else:
                                        instrs.append(i)
                                case _:
                                    instrs.append(i)                            
                        body[l] = instrs
                    result.append(FunctionDef(fname, params, body, dl, returns, comment))
                case _:
                    raise Exception('error in patch_instructions, unexpected ' + repr(p))
        print(result)
        p.defs = result
        return p

    ###########################################################################
    # Prelude & Conclusion
    ###########################################################################

    def prelude_and_conclusion(self, p: X86ProgramDefs) -> X86Program:
        # YOUR CODE HERE

        body = {}
        for stmt in p.defs:
            match stmt:
                case FunctionDef(fname, params, bod, dl, returns, comment):
                    body.update(bod)
                    offset = 0
                    for l,ss in bod.items():
                        for j in ss:
                            match j:
                                case Instr(name, [deref1,deref2]):
                                    if isinstance(deref1, (Deref,)):
                                        if deref1.offset < offset:
                                            offset = deref1.offset
                                    elif isinstance(deref2, (Deref,)) :
                                        if deref2.offset < offset:
                                            offset = deref2.offset
                    instrs = []
                    instrs.append(Instr('pushq', [Reg('rbp')]))
                    instrs.append(Instr('movq', [Reg('rsp'),Reg('rbp')]))
                    for j in p.calleesaved:
                        instrs.append(Instr('pushq', [Reg(j)]))
                    size = math.ceil(-offset / 16)*16 + (len(p.calleesaved)%2)*8
                    instrs.append(Instr('subq', [Immediate(size),Reg('rsp')]))
                    if fname == 'main':
                        instrs.append(Instr('movq', [Immediate(65536), Reg('rdi')]))
                        instrs.append(Instr('movq', [Immediate(65536), Reg('rsi')]))
                        instrs.append(Callq(label_name("initialize"), 2))
                    instrs.append(Instr('movq', [Global('rootstack_begin'), Reg('r15')]))
                    instrs.append(Instr('movq', [Immediate(0), Deref('r15',0)]))
                    instrs.append(Instr('addq', [Immediate(8), Reg('r15')]))
                    instrs.append(Jump(label_name(fname+"_start")))
                    body[fname] = instrs
                    body[fname+'_start'].append(Jump(label_name(fname+"_conclusion")))
                    instrs = []
                    instrs.append(Instr('subq', [Immediate(8),Reg('r15')]))
                    instrs.append(Instr('addq', [Immediate(size),Reg('rsp')]))
                    for j in p.calleesaved:
                        instrs.append(Instr('popq', [Reg(j)]))
                    instrs.append(Instr('popq', [Reg('rbp')]))
                    instrs.append(Instr('retq', []))
                    body[fname+'_conclusion'] = instrs
                case _:
                    raise Exception('error in prelude_and_conclusion, unexpected ' + repr(p))

        return X86Program(body)

