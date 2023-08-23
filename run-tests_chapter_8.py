import os
import compiler_chapter_8 as compiler
import interp_Lfun
import interp_Cfun
import type_check_Lfun
import type_check_Cfun
from utils import run_tests, run_one_test
from interp_x86.eval_x86 import interp_x86

compiler = compiler.Compiler()

typecheck_Lfun = type_check_Lfun.TypeCheckLfun().type_check
typecheck_Cfun = type_check_Cfun.TypeCheckCfun().type_check

typecheck_dict = {
    'source': typecheck_Lfun,
    'shrink': typecheck_Lfun,
    'reveal_functions': typecheck_Lfun,
    'limit_functions': typecheck_Lfun,
    'expose_allocation': typecheck_Lfun,
    'remove_complex_operands': typecheck_Lfun,
    'explicate_control': typecheck_Cfun,
}
interpLfun = interp_Lfun.InterpLfun().interp
interpCfun = interp_Cfun.InterpCfun().interp
interp_dict = {
    'shrink': interpLfun,
    'reveal_functions': interpLfun,
    'limit_functions': interpLfun,
    'expose_allocation': interpLfun,
    'remove_complex_operands': interpLfun,
    'explicate_control': interpCfun,
    'select_instructions': interp_x86,
    'assign_homes': interp_x86,
    'patch_instructions': interp_x86,
}

from utils import enable_tracing
enable_tracing()


# run_one_test(os.getcwd() + '/tests/fun/fun_test_1.py',
#                 'fun',
#                 compiler,
#                 'fun',
#                 typecheck_dict,
#                 interp_dict)


# run_one_test(os.getcwd() + '/tests/fun/fun_test_3.py',
#                 'fun',
#                 compiler,
#                 'fun',
#                 typecheck_dict,
#                 interp_dict)

run_one_test(os.getcwd() + '/tests/fun/fun_test_2.py',
                'fun',
                compiler,
                'fun',
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

