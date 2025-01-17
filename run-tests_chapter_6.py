import os
import compiler_chapter_6 as compiler
import interp_Lwhile
import interp_Cif
import type_check_Lwhile
import type_check_Cwhile
from utils import run_tests, run_one_test
from interp_x86.eval_x86 import interp_x86

compiler = compiler.Compiler()

typecheck_Lwhile = type_check_Lwhile.TypeCheckLwhile().type_check
typecheck_Cwhile = type_check_Cwhile.TypeCheckCwhile().type_check

typecheck_dict = {
    'source': typecheck_Lwhile,
    'remove_complex_operands': typecheck_Lwhile,
    'explicate_control': typecheck_Cwhile,
}
interpLwhile = interp_Lwhile.InterpLwhile().interp
interpCif = interp_Cif.InterpCif().interp
interp_dict = {
    'remove_complex_operands': interpLwhile,
    'explicate_control': interpCif,
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

# run_one_test(os.getcwd() + '/tests/while/while_test_1.py',
#                 'while',
#                 compiler,
#                 'while',
#                 typecheck_dict,
#                 interp_dict)

run_one_test(os.getcwd() + '/tests/while/while_test_2.py',
                'while',
                compiler,
                'while',
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

