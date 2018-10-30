import attributes

from pycparser import parse_file
import os

# izvlacenje atributa iz programa sa takmicenja
# --------------------------------------------------------------------------------------------


# objekti sa vrednostima atributa
instances = []

# 1/0 u zavisnosti od toga da li program zadovoljava specifikacije ili ne
classes = []

#print("----------------------------")
for directory in os.walk("./C_tests"):
    #print(directory)
    folder = directory[0]
    files = directory[2]
    print(folder)
    print(files)
    for file in files:
        if file.endswith(".c"):
            file = os.path.join(folder, file)
            # print(os.path.abspath(filename))
            # print(os.path.join(directory, filename))
            print("Fajl: "+file)

            if "false-unreach-call" in file:
                classes.append(1)
            elif "false-valid-memsafety" in file:
                classes.append(1)
            elif "false-valid-deref" in file:
                classes.append(1)
            elif "false-valid-free" in file:
                classes.append(1)
            elif "false-valid-memtrack" in file:
                classes.append(1)
            elif "false-valid-memcleanup" in file:
                classes.append(1)
            elif "false-no-overflow" in file:
                classes.append(1)
            elif "false-termination" in file:
                classes.append(1)
            else:
                classes.append(0)

            attributes.operators = {}
            attributes.operands = {}
            attributes.type_pointer = 0
            attributes.tpoint = False
            attributes.func_pointer = 0
            attributes.fpoint = False
            attributes.func_call = False
            attributes.func_decl = False
            attributes.assignment = False
            attributes.is_return = False
            attributes.array_ref = False
            attributes.num_params = 0
            attributes.binary_op = False
            attributes.unary_op = False
            attributes.expr_list = False
            attributes.loc_exec = 0

            ast = parse_file(file, use_cpp=True,
                             cpp_path='gcc',
                             cpp_args=['-nostdinc', '-D__attribute__(x)=', '-D__extension__=',  '-D__const=', '-E',
                                       r'-I./pycparser-master/utils/fake_libc_include']
                             )

            # FileAst[ext**]
            for node in ast.ext:
                # print(node)
                attributes.traverse(node)

            attributes.loc_metrics(file)

            attributes.Halstead_metrics(file)

            new_instance = [attributes.loc_blanc, attributes.loc_code_and_comment, attributes.loc_comments,
                            attributes.loc_exec, attributes.I, attributes.D, attributes.E, attributes.B, attributes.N,
                            attributes.L, attributes.T, attributes.V, attributes.N2, attributes.N1, attributes.n2,
                            attributes.n1, attributes.loc_total]
            instances.append(new_instance)

            # print(new_instance)

    print("----")

result_file = open("c_attributes.txt", mode="w")
# print("-------------------------\n")
for instance in instances:
    # print(instance)
    result_file.write(str(instance) + '\n')

result_file.close()


result_file = open("c_attributes_classes.txt", mode="w")
# print("-------------------------\n")
for c in classes:
    # print(c)
    result_file.write(str(c) + '\n')

result_file.close()


# --------------------------------------------------------------------------------------------

'''

file = '../github_c_codes_for_testing_classification/fix_parser-master/src/fix_parser.c'
print(file)

attributes.operators = {}
attributes.operands = {}
attributes.type_pointer = 0
attributes.tpoint = False
attributes.func_pointer = 0
attributes.fpoint = False
attributes.func_call = False
attributes.func_decl = False
attributes.assignment = False
attributes.is_return = False
attributes.array_ref = False
attributes.num_params = 0
attributes.binary_op = False
attributes.unary_op = False
attributes.expr_list = False
attributes.loc_exec = 0


ast = parse_file(file, use_cpp=True,
                 cpp_path='gcc',
                 cpp_args=['-nostdinc', '-D__attribute__(x)=', '-D__extension__=',  '-D__const=', '-E',
                           r'-I./pycparser-master/utils/fake_libc_include',
                           r'-I../github_c_codes_for_testing_classification/fix_parser-master/include']
                 )



# FileAst[ext**]
for node in ast.ext:
    # print(node)
    attributes.traverse(node)

attributes.loc_metrics(file)

attributes.Halstead_metrics(file)

new_instance = [attributes.loc_blanc, attributes.loc_code_and_comment, attributes.loc_comments,
                attributes.loc_exec, attributes.I, attributes.D, attributes.E, attributes.B, attributes.N,
                attributes.L, attributes.T, attributes.V, attributes.N2, attributes.N1, attributes.n2,
                attributes.n1, attributes.loc_total]

print(new_instance)
'''
# ------------------------------------------------------------------------------------------
# file = '../github_c_codes_for_testing_classification/fix_parser-master/src/fix_error.c'
'''
file = '../github_c_codes_for_testing_classification/MylibC-master/lib/my/my_putchar.c'
print(file)

attributes.operators = {}
attributes.operands = {}
attributes.type_pointer = 0
attributes.tpoint = False
attributes.func_pointer = 0
attributes.fpoint = False
attributes.func_call = False
attributes.func_decl = False
attributes.assignment = False
attributes.is_return = False
attributes.array_ref = False
attributes.num_params = 0
attributes.binary_op = False
attributes.unary_op = False
attributes.expr_list = False
attributes.loc_exec = 0


ast = parse_file(file, use_cpp=True,
                 cpp_path='gcc',
                 cpp_args=['-nostdinc', '-D__attribute__(x)=', '-D__extension__=',  '-D__const=', '-E',
                           r'-I./pycparser-master/utils/fake_libc_include',
                           r'-I../github_c_codes_for_testing_classification/MylibC-master/include']
                 )



# FileAst[ext**]
for node in ast.ext:
    # print(node)
    attributes.traverse(node)

attributes.loc_metrics(file)

attributes.Halstead_metrics(file)

new_instance = [attributes.loc_blanc, attributes.loc_code_and_comment, attributes.loc_comments,
                attributes.loc_exec, attributes.I, attributes.D, attributes.E, attributes.B, attributes.N,
                attributes.L, attributes.T, attributes.V, attributes.N2, attributes.N1, attributes.n2,
                attributes.n1, attributes.loc_total]

print(new_instance)


'''