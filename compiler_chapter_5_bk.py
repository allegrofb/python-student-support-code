import ast
from ast import *
from utils import *
from x86_ast import *
import os
from typing import List, Tuple, Set, Dict
from graph import UndirectedAdjList, DirectedAdjList, topological_sort, transpose

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
                # tmpVars = []
                # if need_atomic:
                #     tmp = Name(generate_name('tmpVar'))
                #     tmpVars.append((tmp, IfExp(test, body, orelse)))
                #     return tmp, tmpVars
                # else:
                #     return IfExp(test, body, orelse), tmpVars

                tmpVars = []
                # if not isinstance(test, (Name, Constant,)):
                #     test, tmp = self.rco_exp(test, need_atomic=False)
                #     tmpVars.extend(tmp)
                if not isinstance(body, (Name, Constant,)):  # branch have side-effect code, insert Begin expr
                    body2, tmp = self.rco_exp(body, need_atomic=False) # it's ok for need_atomic=True ?
                    stmts = []
                    for i in tmp:
                        stmts.append(Assign([i[0]], i[1]))
                    body = Begin(stmts,body2)
                if not isinstance(orelse, (Name, Constant,)):
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
                    if not isinstance(body, Constant):
                        body = self.explicate_effect(body, cont, basic_blocks) # for Begin
                    body = cont + [Assign([lhs], body)] + [goto] 
                    cont = []
                    if not isinstance(orelse, Constant):
                        orelse = self.explicate_effect(orelse, cont, basic_blocks) # for Begin
                    orelse = cont + [Assign([lhs], orelse)] + [goto] 
                    return self.explicate_pred(test, body, orelse, basic_blocks)
                else:
                    body = [Assign([lhs], body)] 
                    orelse = [Assign([lhs], orelse)] 
                    return self.explicate_pred(test, body, orelse, basic_blocks) + cont
            case Begin(body, result):
                raise Exception("Begin")
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

    def explicate_stmt(self, s: stmt, cont: List[stmt], basic_blocks: Dict) -> List[stmt]:
        match s:
            case Assign([lhs], rhs):
                return self.explicate_assign(rhs, lhs, cont, basic_blocks)
            case Expr(value):
                return self.explicate_effect(value, cont, basic_blocks)
            case If(test, body, orelse):
                raise Exception("If")
                
    def explicate_control(self, p: Module) -> CProgram:
        match p:
            case Module(body):
                new_body = [Return(Constant(0))]
                basic_blocks = {}
                for s in reversed(body):
                    new_body = self.explicate_stmt(s, new_body, basic_blocks)
                basic_blocks[label_name('start')] = new_body
                # print(basic_blocks)
                return CProgram(basic_blocks)

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
                raise Exception('error in select_arg, unexpected ' + repr(e))

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
                    case Begin(body, result):
                        instrs = []
                        for i in body:
                            instrs.extend(self.select_stmt(i))
                        instrs.append(Instr('movq', [self.select_arg(result), self.select_arg(arg)]))
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
                        instrs.append(Instr('cmpq', [self.select_arg(left), self.select_arg(right)]))
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
                raise Exception('error in select_stmt, unexpected ' + repr(s))

    def select_instructions(self, p: CProgram) -> X86Program:
        # YOUR CODE HERE
        match p:
            case CProgram(body):
                result = dict()
                for l,stmts in body.items():
                    instrs = []
                    for stmt in stmts:
                        instrs.extend(self.select_stmt(stmt))
                    result[l] = instrs
                return X86Program(result)
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
            case Callq(name, num):
                return {Reg(n) for n in 'rax rcx rdx rsi rdi r8 r9 r10 r11'.split(' ')}
            case Instr(name, args):
                return {args[-1]}
            case _:
                raise Exception('error in write_vars, unexpected ' + repr(i))

    def uncover_live(self, p: X86Program) -> Dict[instr, Set[location]]:
        # YOUR CODE HERE
        match p:
            case X86Program(body):
                graph = DirectedAdjList() # control flow graph (CFG)
                for l,ss in body.items():
                    u = l
                    v = []
                    for s in ss:
                        if isinstance(s, (Jump, JumpIf)):
                            v.append(s.label)
                    for i in v:
                        graph.add_edge(u, i)
                vs = topological_sort(transpose(graph)) # reverse basic blocks sequence
                if len(vs) == 0:
                    vs = ['start']
                # print(vs)

                live_before_block = {}
                instr_dict = {}
                after = set()
                for v in vs:
                    for i in reversed(body[v]):
                        if isinstance(i, (Jump, JumpIf)):
                            # print(v, 'jump to: ',graph.out[v])
                            instr_dict[i] = live_before_block[i.label]
                        else:
                            instr_dict[i] = after
                        r = self.read_vars(i)
                        w = self.write_vars(i)
                        before = (after - w).union(r)
                        after = before
                    live_before_block[v] = before
                return instr_dict
            case _:
                raise Exception('error in uncover_live, unexpected ' + repr(p))

    ############################################################################
    # Build Interference
    ############################################################################

    def build_interference(self, p: X86Program,
                           live_after: Dict[instr, Set[location]]) -> UndirectedAdjList:
        # YOUR CODE HERE
        graph = UndirectedAdjList()
        for l, ss in p.body.items():
            for i in ss:
                match i:
                    case Instr('movq', [s,d]):
                        for v in live_after[i]:
                            if v != s and v != d:
                                graph.add_edge(d,v)
                    case _:
                        w = self.write_vars(i)
                        for d in w:
                            for v in live_after[i]:
                                if d != v:
                                    graph.add_edge(d,v)
        return graph

    ############################################################################
    # Allocate Registers
    ############################################################################

    # Returns the coloring and the set of spilled variables.
    def color_graph(self, graph: UndirectedAdjList,
                    variables: Set[location]) -> Tuple[Dict[location, int], Set[location]]:
        # YOUR CODE HERE
        from priority_queue import PriorityQueue
        L = {}
        for v in variables:
            L[v] = []
        def less(x, y):
            return len(L[x.key]) < len(L[y.key])
        Q = PriorityQueue(less)
        for k, v in L.items():
            Q.push(k)

        color = {}
        while not Q.empty():
            # print(Q)
            k = Q.pop()
            adj_k = graph.adjacent(k)
            color_list = []
            for i in adj_k:
                if i in color:
                    color_list.append(color[i])
            low_color = 0
            for i in color_list:
                if low_color in color_list:
                    low_color += 1
            color[k] = low_color
            for i in adj_k:
                if low_color not in L[i]:
                    L[i].append(low_color)
                    Q.increase_key(i)
        # print(L)
        return color, variables

    def allocate_registers(self, p: X86Program,
                           graph: UndirectedAdjList) -> X86Program:
        # YOUR CODE HERE
        var = graph.vertices()
        # print(var)
        color, var = self.color_graph(graph, var)
        # print(color)
        body = {}
        for l, ss in p.body.items():
            instrs = []
            for i in ss:
                match i:
                    case Instr(name, [arg]):
                        if arg in color:
                            if color[arg] == 0:
                                arg = Reg('rcx')
                            elif color[arg] == 1:
                                arg = Reg('rbx')
                            else:
                                arg = Deref('rbp',-(color[arg]-1)*8)
                        elif isinstance(arg, Variable):
                            arg = Reg('rcx')
                        instrs.append(Instr(name,[arg]))
                    case Instr(name, [arg1,arg2]):
                        if arg1 in color:
                            if color[arg1] == 0:
                                arg1 = Reg('rcx')
                            elif color[arg1] == 1:
                                arg1 = Reg('rbx')
                            else:
                                arg1 = Deref('rbp',-(color[arg1]-1)*8)
                        elif isinstance(arg1, Variable):
                            arg1 = Reg('rcx')
                        if arg2 in color:
                            if color[arg2] == 0:
                                arg2 = Reg('rcx')
                            elif color[arg2] == 1:
                                arg2 = Reg('rbx')
                            else:
                                arg2 = Deref('rbp',-(color[arg2]-1)*8)
                        elif isinstance(arg2, Variable):
                            arg2 = Reg('rcx')
                        instrs.append(Instr(name,[arg1,arg2]))
                    case _:
                        instrs.append(i)                            
            body[l] = instrs
        p = X86Program(body)
        setattr(p, 'calleesaved', ['rbx'])
        return p

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes(self, pseudo_x86: X86Program) -> X86Program:
        # YOUR CODE HERE
        live_after = self.uncover_live(pseudo_x86)
        # for k,v in live_after.items():
        #     print(k,v)
        graph = self.build_interference(pseudo_x86, live_after)
        # print(graph.show())
        return self.allocate_registers(pseudo_x86, graph)

    ###########################################################################
    # Patch Instructions
    ###########################################################################

    def patch_instructions(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        body = {}
        for l,ss in p.body.items():
            instrs = []
            for i in ss:
                match i:
                    case Instr(name, [deref1, deref2]):
                        if name =='movq' and deref1 == deref2:
                            pass
                        elif isinstance(deref1, (Deref,)) and isinstance(deref2, (Deref,)) :
                            instrs.append(Instr('movq', [deref1,Reg('rax')]))
                            instrs.append(Instr(name, [Reg('rax'),deref2]))
                        else:
                            instrs.append(i)
                    case _:
                        instrs.append(i)                            
            body[l] = instrs
        p.body = body
        return p

    ###########################################################################
    # Prelude & Conclusion
    ###########################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        match p:
            case X86Program(body):
                offset = 0
                for l,ss in body.items():
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
                instrs.append(Instr('subq', [Immediate((int(offset/16)-1)*-16),Reg('rsp')]))
                instrs.append(Jump(label_name("start")))
                body['main'] = instrs

                body['start'].append(Jump(label_name("conclusion")))

                instrs = []
                instrs.append(Instr('addq', [Immediate((int(offset/16)-1)*-16),Reg('rsp')]))
                for j in p.calleesaved:
                    instrs.append(Instr('popq', [Reg(j)]))
                instrs.append(Instr('popq', [Reg('rbp')]))
                instrs.append(Instr('retq', []))
                body['conclusion'] = instrs

                return X86Program(body)
            case _:
                raise Exception('error in prelude_and_conclusion, unexpected ' + repr(p))

