import ast
from ast import *
from utils import *
from x86_ast import *
import os
from typing import List, Tuple, Set, Dict

Binding = Tuple[Name, expr]
Temporaries = List[Binding]


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
            case _:
                raise Exception('error in shrink_stmt, unexpected ' + repr(s))

    def shrink(self, p: Module) -> Module:
        match p:
            case Module(body):
                new_body = []
                for stmt in body:
                    new_body.append(self.shrink_stmt(stmt))
                return Module(new_body)
            case _:
                raise Exception('error in shrink, unexpected ' + repr(p))

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
                return Call(Name('input_int'), []), []
            case BinOp(left, Add(), right):
                tmpVars = []
                if not isinstance(left, (Name, Constant,)):
                    left2, tmp = self.rco_exp(left, need_atomic=False)
                    tmpVars.extend(tmp)
                    left = Name(generate_name('tmpVar'))
                    tmpVars.append((left, left2))
                if not isinstance(right, (Name, Constant,)):
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
                if not isinstance(left, (Name, Constant,)):
                    left2, tmp = self.rco_exp(left, need_atomic=False)
                    tmpVars.extend(tmp)
                    left = Name(generate_name('tmpVar'))
                    tmpVars.append((left, left2))
                if not isinstance(right, (Name, Constant,)):
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
                if not isinstance(v, (Name, Constant,)):
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
            case Compare(left, [cmp], [right]):
                tmpVars = []
                if not isinstance(left, (Name, Constant,)):
                    left2, tmp = self.rco_exp(left, need_atomic=True)
                    tmpVars.extend(tmp)
                    left = Name(generate_name('tmpVar'))
                    tmpVars.append((left, left2))
                if not isinstance(right, (Name, Constant,)):
                    right2, tmp = self.rco_exp(right, need_atomic=True)
                    tmpVars.extend(tmp)
                    right = Name(generate_name('tmpVar'))
                    tmpVars.append((right, right2))
                if need_atomic:
                    tmp = Name(generate_name('tmpVar'))
                    tmpVars.append((tmp, Compare(left, [cmp], right)))
                    return tmp, tmpVars
                else:
                    return Compare(left, [cmp], right), tmpVars
            case IfExp(test, body, orelse):
                return IfExp(test, body, orelse), []
                # tmpVars = []
                # if not isinstance(test, (Name, Constant,)):
                #     test2, tmp = self.rco_exp(test, need_atomic=False)
                #     tmpVars.extend(tmp)
                #     test = Name(generate_name('tmpVar'))
                #     tmpVars.append((test, test2))
                # if not isinstance(body, (Name, Constant,)):
                #     body2, tmp = self.rco_exp(body, need_atomic=need_atomic)
                #     tmpVars.extend(tmp)
                #     body = Name(generate_name('tmpVar'))
                #     tmpVars.append((body, body2))
                # if not isinstance(orelse, (Name, Constant,)):
                #     orelse2, tmp = self.rco_exp(orelse, need_atomic=need_atomic)
                #     tmpVars.extend(tmp)
                #     orelse = Name(generate_name('tmpVar'))
                #     tmpVars.append((orelse, orelse2))
                # if need_atomic:
                #     tmp = Name(generate_name('tmpVar'))
                #     tmpVars.append((tmp, IfExp(test, body, orelse)))
                #     return tmp, tmpVars
                # else:
                #     return IfExp(test, body, orelse), tmpVars
            case _:
                raise Exception('error in rco_exp, unexpected ' + repr(s))

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
            case _:
                raise Exception('error in rco_stmt, unexpected ' + repr(s))

    def remove_complex_operands(self, p: Module) -> Module:
        # YOUR CODE HERE
        match p:
            case Module(body):
                new_body = []
                for stmt in body:
                    new_body.extend(self.rco_stmt(stmt))
                print(new_body)
                return Module(new_body)
            case _:
                raise Exception('error in remove_complex_operands, unexpected ' + repr(p))
        

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
            case _:
                raise Exception('error in select_arg, unexpected ' + repr(s))

    def select_stmt(self, s: stmt) -> List[instr]:
        # YOUR CODE HERE
        match s:
            case Assign([arg], value):
                match value:
                    case Name(n):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(value), self.select_arg(arg)]))
                        return instrs
                    case Constant(v):
                        instrs = []
                        instrs.append(Instr('movq', [self.select_arg(value), self.select_arg(arg)]))
                        return instrs
                    case Call(Name('input_int'), []):
                        instrs = []
                        instrs.append(Callq(label_name("read_int"), 0))
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
            case _:
                raise Exception('error in select_stmt, unexpected ' + repr(s))

    def select_instructions(self, p: Module) -> X86Program:
        # YOUR CODE HERE
        match p:
            case Module(body):
                instrs = []
                for stmt in body:
                    instrs.extend(self.select_stmt(stmt))
                return X86Program(instrs)
            case _:
                raise Exception('error in select_instructions, unexpected ' + repr(p))

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes_arg(self, a: arg, home: Dict[Variable, arg]) -> arg:
        # YOUR CODE HERE
        match a:
            case Variable(id):
                if a in home:
                    return home[a]
                else:
                    home[a] = Deref('rbp',-(len(home)+1)*8)
                    return home[a]
            case _:
                return a

    def assign_homes_instr(self, i: instr,
                           home: Dict[Variable, arg]) -> instr:
        # YOUR CODE HERE
        match i:
            case Instr(name, args):
                args = [self.assign_homes_arg(arg, home) for arg in args]
                return Instr(name, args)
            case _:
                return i

    def assign_homes_instrs(self, ss: List[instr],
                            home: Dict[Variable, arg]) -> List[instr]:
        # YOUR CODE HERE
        instrs = []
        for i in ss:
            instrs.append(self.assign_homes_instr(i, home))
        return instrs

    def assign_homes(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        match p:
            case X86Program(body):
                home = dict()
                instrs = self.assign_homes_instrs(body, home)
                return X86Program(instrs)
            case _:
                raise Exception('error in assign_homes, unexpected ' + repr(p))

    ############################################################################
    # Patch Instructions
    ############################################################################

    def patch_instr(self, i: instr) -> List[instr]:
        # YOUR CODE HERE
        match i:
            case Instr(name, [deref1,deref2]):
                if isinstance(deref1, (Deref,)) and isinstance(deref2, (Deref,)) :
                    instrs = []
                    instrs.append(Instr('movq', [deref1,Reg('rax')]))
                    instrs.append(Instr(name, [Reg('rax'),deref2]))
                    return instrs
                else:
                    return [i]
            case _:
                return [i]

    def patch_instrs(self, ss: List[instr]) -> List[instr]:
        # YOUR CODE HERE
        instrs = []
        for i in ss:
            instrs.extend(self.patch_instr(i))
        return instrs

    def patch_instructions(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        match p:
            case X86Program(body):
                instrs = self.patch_instrs(body)
                return X86Program(instrs)
            case _:
                raise Exception('error in patch_instructions, unexpected ' + repr(p))

    ############################################################################
    # Prelude & Conclusion
    ############################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        match p:
            case X86Program(body):
                offset = 0
                for j in body:
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
                instrs.append(Instr('subq', [Immediate((int(offset/16)-1)*-16),Reg('rsp')]))
                instrs.extend(body)
                instrs.append(Instr('addq', [Immediate((int(offset/16)-1)*-16),Reg('rsp')]))
                instrs.append(Instr('popq', [Reg('rbp')]))
                instrs.append(Instr('retq', []))
                return X86Program(instrs)
            case _:
                raise Exception('error in prelude_and_conclusion, unexpected ' + repr(p))
