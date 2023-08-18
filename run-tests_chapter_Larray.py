import os
import compiler_chapter_Larray as compiler
import interp_Larray
import interp_Carray
import type_check_Larray
import type_check_Carray
from utils import run_tests, run_one_test
from interp_x86.eval_x86 import interp_x86

compiler = compiler.Compiler()

typecheck_Larray = type_check_Larray.TypeCheckLarray().type_check
typecheck_Carray = type_check_Carray.TypeCheckCarray().type_check

typecheck_dict = {
    'source': typecheck_Larray,
    'shrink': typecheck_Larray,   
    'expose_allocation': typecheck_Larray,
    'remove_complex_operands': typecheck_Larray,
    'explicate_control': typecheck_Carray,
}
interpLarray = interp_Larray.InterpLarray().interp
interpCarray = interp_Carray.InterpCarray().interp
interp_dict = {
    'shrink': interpLarray,
    'expose_allocation': interpLarray,
    'remove_complex_operands': interpLarray,
    'explicate_control': interpCarray,
    # 'select_instructions': interp_x86,
    # 'assign_homes': interp_x86,
    # 'patch_instructions': interp_x86,
}

from utils import enable_tracing
enable_tracing()



run_one_test(os.getcwd() + '/tests/array/array_test_1.py',
                'array',
                compiler,
                'array',
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

