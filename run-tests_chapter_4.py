import os
import compiler_register_allocator as compiler
import interp_Lvar
import type_check_Lvar
from utils import run_tests, run_one_test
from interp_x86.eval_x86 import interp_x86

compiler = compiler.Compiler()

typecheck_Lvar = type_check_Lvar.TypeCheckLvar().type_check

typecheck_dict = {
    'source': typecheck_Lvar,
    'remove_complex_operands': typecheck_Lvar,
}
interpLvar = interp_Lvar.InterpLvar().interp
interp_dict = {
    'remove_complex_operands': interpLvar,
    'select_instructions': interp_x86,
    'assign_homes': interp_x86,
    'patch_instructions': interp_x86,
}

from utils import enable_tracing
enable_tracing()

run_one_test(os.getcwd() + '/tests/var/var_test_6.py',
                'var',
                compiler,
                'var',
                typecheck_dict,
                interp_dict)

# if False:
#     run_one_test(os.getcwd() + '/tests/var/zero.py',
#                  'var',
#                  compiler,
#                  'var',
#                  typecheck_dict,
#                  interp_dict)
# else:
#     run_tests('var', compiler, 'var',
#               typecheck_dict,
#               interp_dict)

