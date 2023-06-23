import os
import compiler_chapter_7 as compiler
import interp_Ltup
import interp_Ctup
import type_check_Ltup
import type_check_Ctup
from utils import run_tests, run_one_test
from interp_x86.eval_x86 import interp_x86

compiler = compiler.Compiler()

typecheck_Ltup = type_check_Ltup.TypeCheckLtup().type_check
typecheck_Ctup = type_check_Ctup.TypeCheckCtup().type_check

typecheck_dict = {
    'source': typecheck_Ltup,
    'expose_allocation': typecheck_Ltup,
    'remove_complex_operands': typecheck_Ltup,
    'explicate_control': typecheck_Ctup,
}
interpLtup = interp_Ltup.InterpLtup().interp
interpCtup = interp_Ctup.InterpCtup().interp
interp_dict = {
    'expose_allocation': interpLtup,
    'remove_complex_operands': interpLtup,
    'explicate_control': interpCtup,
    'select_instructions': interp_x86,
    'assign_homes': interp_x86,
    'patch_instructions': interp_x86,
}

from utils import enable_tracing
enable_tracing()

# run_one_test(os.getcwd() + '/tests/if/if_shrink_1.py',
#                 'if',
#                 compiler,
#                 'if',
#                 typecheck_dict,
#                 interp_dict)

# run_one_test(os.getcwd() + '/tests/tuple/tuple_test_1.py',
#                 'tuple',
#                 compiler,
#                 'tuple',
#                 typecheck_dict,
#                 interp_dict)

run_one_test(os.getcwd() + '/tests/tuple/tuple_test_4.py',
                'tuple',
                compiler,
                'tuple',
                typecheck_dict,
                interp_dict)


# run_tests('if', compiler, 'if',
#             typecheck_dict,
#             interp_dict)


# if False:
#     run_one_test(os.getcwd() + '/tests/var/zero.py',
#                  'var',
#                  compiler,
#                  'var',
#                  typecheck_dict,
#                  interp_dict)
# else:
#     run_tests('if', compiler, 'if',
#               typecheck_dict,
#               interp_dict)

