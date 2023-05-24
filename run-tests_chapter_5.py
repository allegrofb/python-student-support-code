import os
import compiler_chapter_5 as compiler
import interp_Lif
import type_check_Lif
from utils import run_tests, run_one_test
from interp_x86.eval_x86 import interp_x86

compiler = compiler.Compiler()

typecheck_Lif = type_check_Lif.TypeCheckLif().type_check

typecheck_dict = {
    'source': typecheck_Lif,
    'remove_complex_operands': typecheck_Lif,
}
interpLif = interp_Lif.InterpLif().interp
interp_dict = {
    'remove_complex_operands': interpLif,
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

run_one_test(os.getcwd() + '/tests/if/if_explicate_control_1.py',
                'if',
                compiler,
                'if',
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
#     run_tests('if', compiler, 'if',
#               typecheck_dict,
#               interp_dict)

