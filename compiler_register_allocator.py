import compiler
from graph import UndirectedAdjList
from typing import List, Tuple, Set, Dict
from ast import *
from x86_ast import *
from typing import Set, Dict, Tuple

# Skeleton code for the chapter on Register Allocation

class Compiler(compiler.Compiler):

    ###########################################################################
    # Uncover Live
    ###########################################################################

    def read_vars(self, i: instr) -> Set[location]:
        # YOUR CODE HERE
        match i:
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
                instr_dict = {}
                after = set()
                for i in reversed(body):
                    instr_dict[i] = after
                    r = self.read_vars(i)
                    w = self.write_vars(i)
                    before = (after - w).union(r)
                    after = before
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
        for i in p.body:
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
        instrs = []
        for i in p.body:
            match i:
                case Instr(name, [arg]):
                    if arg in color:
                        if color[arg] == 0:
                            arg = Reg('rcx')
                        elif color[arg] == 1:
                            arg = Reg('rbx')
                        else:
                            arg = Deref('rbp',-(color[arg]-1)*8)
                    instrs.append(Instr(name,[arg]))
                case Instr(name, [arg1,arg2]):
                    if arg1 in color:
                        if color[arg1] == 0:
                            arg1 = Reg('rcx')
                        elif color[arg1] == 1:
                            arg1 = Reg('rbx')
                        else:
                            arg1 = Deref('rbp',-(color[arg1]-1)*8)
                    if arg2 in color:
                        if color[arg2] == 0:
                            arg2 = Reg('rcx')
                        elif color[arg2] == 1:
                            arg2 = Reg('rbx')
                        else:
                            arg2 = Deref('rbp',-(color[arg2]-1)*8)
                    instrs.append(Instr(name,[arg1,arg2]))
                case _:
                    instrs.append(i)                            

        p = X86Program(instrs)
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
        instrs = []
        for i in p.body:
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
        p.body = instrs
        return p

    ###########################################################################
    # Prelude & Conclusion
    ###########################################################################

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
                for j in p.calleesaved:
                    instrs.append(Instr('pushq', [Reg(j)]))
                instrs.append(Instr('subq', [Immediate((int(offset/16)-1)*-16),Reg('rsp')]))
                instrs.extend(body)
                instrs.append(Instr('addq', [Immediate((int(offset/16)-1)*-16),Reg('rsp')]))
                for j in p.calleesaved:
                    instrs.append(Instr('popq', [Reg(j)]))
                instrs.append(Instr('popq', [Reg('rbp')]))
                instrs.append(Instr('retq', []))
                return X86Program(instrs)
            case _:
                raise Exception('error in prelude_and_conclusion, unexpected ' + repr(p))
