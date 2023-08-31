import os
import compiler_chapter_9 as compiler
import interp_Llambda
import interp_Clambda
import type_check_Llambda
import type_check_Clambda
from utils import run_tests, run_one_test
from interp_x86.eval_x86 import interp_x86

compiler = compiler.Compiler()

typecheck_Llambda = type_check_Llambda.TypeCheckLlambda().type_check
typecheck_Clambda = type_check_Clambda.TypeCheckClambda().type_check

typecheck_dict = {
    'source': typecheck_Llambda,
    'shrink': typecheck_Llambda,
    'reveal_functions': typecheck_Llambda,
    'limit_functions': typecheck_Llambda,
    'expose_allocation': typecheck_Llambda,
    'remove_complex_operands': typecheck_Llambda,
    'explicate_control': typecheck_Clambda,
}
interpLlambda = interp_Llambda.InterpLlambda().interp
interpClambda = interp_Clambda.InterpClambda().interp
interp_dict = {
    'shrink': interpLlambda,
    'reveal_functions': interpLlambda,
    'limit_functions': interpLlambda,
    'expose_allocation': interpLlambda,
    'remove_complex_operands': interpLlambda,
    'explicate_control': interpClambda,
    'select_instructions': interp_x86,
    'assign_homes': interp_x86,
    'patch_instructions': interp_x86,
}

from utils import enable_tracing
enable_tracing()


run_one_test(os.getcwd() + '/tests/lambda/lambda_test_4.py',
                'lambda',
                compiler,
                'lambda',
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

