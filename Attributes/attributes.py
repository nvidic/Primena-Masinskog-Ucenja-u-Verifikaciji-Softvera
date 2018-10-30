from __future__ import print_function
import sys

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

from pycparser import c_ast #c_parser, c_ast
# from pycparser import parse_file

import math
import re


# loc metrike
global loc_exec                 # racuna se u funkciji traverse
global loc_total
global loc_blanc
global loc_code_and_comment
global loc_comments

# halstead metrike
global n1
global n2
global N1
global N2
global N
global V
global L
global I
global D
global B
global T
global E


# traverse
global operands
global operators

global type_pointer
global tpoint
global func_pointer
global fpoint
global func_call
global func_decl
global assignment
global is_return
global array_ref
global num_params
global binary_op
global unary_op
global expr_list
global loc_exec

'''
operators = {}
operands = {}
# broj pokazivaca za pointerdecl. anulira se u identifiertype
# num_pointers = 0
type_pointer = 0
tpoint = False
func_pointer = 0
fpoint = False
# ne zanima me ID ako je deklaracija, inace me zanima
# is_declaration = 0
# pozivi funkcija
func_call = False
func_decl = False
assignment = False
is_return = False
array_ref = False
num_params = 0
# is_param = False
binary_op = False
unary_op = False
expr_list = False
loc_exec = 0
'''

def traverse(node):

    # global num_pointers
    global type_pointer
    global tpoint
    global func_pointer
    global fpoint
    global func_call
    global func_decl
    global assignment
    global is_return
    global array_ref
    global num_params
    global binary_op
    global unary_op
    global expr_list
    global loc_exec


    if isinstance(node, c_ast.ArrayDecl):
        #print("ArrayDecl")
        # ArrayDecl[type*, dim*, dim_quals*]

        if node.type:
            traverse(node.type)
        if node.dim:
            traverse(node.dim)
        if node.dim_quals:
            traverse(node.dim_quals)

    elif isinstance(node, c_ast.ArrayRef):
        #print("ArrayRef")
        # ArrayRef[name*, subscript*]
        array_ref = True

        if node.name:
            traverse(node.name)
        if node.subscript:
            traverse(node.subscript)

    elif isinstance(node, c_ast.Assignment):
        #print("Assignment")
        # Assignment[op, lvalue*, rvalue*]

        loc_exec += 1

        if node.op in operators:
            operators[node.op] += 1
        else:
            operators[node.op] = 1

        assignment = True

        if node.lvalue:
            traverse(node.lvalue)
        if node.rvalue:
            traverse(node.rvalue)
        assignment = False


    elif isinstance(node, c_ast.BinaryOp):
        #print("Binary op")
        # BinaryOp[op, left*, right*]
        # a = 5
        # a = b = i + 5 - l/3

        binary_op = True

        if node.op in operators:
            operators[node.op] += 1
        else:
            operators[node.op] = 1

        # moraju da postoje left i right, provera je suvisna
        if node.left:
            traverse(node.left)
        if node.right:
            traverse(node.right)
        binary_op = False

    elif isinstance(node, c_ast.Break):
        #print("Break")
        # Break[]

        loc_exec += 1

        if "break" in operators:
            operators["break"] += 1
        else:
            operators["break"] = 1

    elif isinstance(node, c_ast.Case):
        #print("Case")
        # Case[expr*, stmts**]

        if "case" in operators:
            operators["case"] += 1
        else:
            operators["case"] = 1

        if node.expr:
            traverse(node.expr)
        if node.stmts:
            for stmt in node.stmts:
                traverse(stmt)


    elif isinstance(node, c_ast.Cast):
        #print("Cast")
        # Cast[to_type*, expr*] -> (int) l

        if node.to_type:
            traverse(node.to_type)
        if node.expr:
            traverse(node.expr)

    elif isinstance(node, c_ast.Compound):
        #print("Compound")
        # Compound[block_items**]
        # ->  {
        #       ..., ...,
        #       ...
        #      }

        if node.block_items:
            for item in node.block_items:
                traverse(item)

    elif isinstance(node, c_ast.CompoundLiteral):
        #print("Compound literal")
        # CompoundLiteral[type*, init*]

        if node.type:
            traverse(node.type)
        if node.init:
            traverse(node.init)

    elif isinstance(node, c_ast.Constant):
        #print("Constant: " + str(node.value))
        # Const[type, value]
        # U ovom slucaju ne treba nista da se radi jer je konstanta npr. karakter 'a' ili broj 5, ...
        return

    elif isinstance(node, c_ast.Continue):
        #print("Continue")
        # Continue[]

        loc_exec += 1

        if "continue" in operators:
            operators["continue"] += 1
        else:
            operators["continue"] = 1

    elif isinstance(node, c_ast.Decl):
        #print("Decl")
        # Decl[name, quals, storage, funspace, type*, init*, bitsize*]

        if num_params:
            if "None" not in str(node.name):
                #print("Node name: " + str(node.name))
                if node.name in operands:
                    #print("Dodajem node name: " + str(node.name))
                    operands[node.name] += 1
                else:
                    #print("Dodajem node name: " + str(node.name))
                    operands[node.name] = 1
            num_params -= 1

        # name parametar nije znacajan zato sto imena funkcija i promenljivih prilikom deklaracija
        # ne spadaju u operatore/operande

        # const, volatile
        quals = node.quals
        if quals:  # if true
            if (len(quals) == 2):
                # print(quals[0]+"   "+quals[1])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1
                if (quals[1] in operators):
                    operators[quals[1]] += 1
                else:
                    operators[quals[1]] = 1
            else:  # (node.quals() == 1):
                # print(quals[0])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1

        # extern, register
        storage = node.storage
        if storage:  # if true
            if (len(storage) == 2):
                # print(storage[0]+"   "+storage[1])
                if (storage[0] in operators):
                    operators[storage[0]] += 1
                else:
                    operators[storage[0]] = 1
                if (storage[1] in operators):
                    operators[storage[1]] += 1
                else:
                    operators[storage[1]] = 1
            else:  # (len(storage) == 1):
                # print(storage[0])
                if (storage[0] in operators):
                    operators[storage[0]] += 1
                else:
                    operators[storage[0]] = 1

                    # funspec
        funcspec = node.funcspec
        if funcspec:
            print(funcspec[0])
            if (funcspec[0] in operators):
                operators[funcspec[0]] += 1
            else:
                operators[funcspec[0]] = 1

        if node.type:
            traverse(node.type)
        if node.init:
            if '=' in operators:
                operators['='] += 1
            else:
                operators['='] = 1
            traverse(node.init)
        if node.bitsize:
            traverse(node.bitsize)

    elif isinstance(node, c_ast.DeclList):
        #print("Decl list")
        # DeclList[decls**]

        if node.decls:
            for decl in node.decls:
                traverse(decl)

    elif isinstance(node, c_ast.Default):
        #print("Default")
        # Default[stmts**]

        if "default" in operators:
            operators["default"] += 1
        else:
            operators["default"] = 1

        if node.stmts:
            for stmt in node.stmts:
                traverse(stmt)

    elif isinstance(node, c_ast.DoWhile):
        #print("Do while")
        # DoWhile[cond*, stmt*]
        '''
        do {
           statement(s);
        } while( condition );
        '''

        if "do while" in operators:
            operators["do while"] += 1
        else:
            operators["do while"] = 1

        if node.cond:
            traverse(node.cond)
        if node.stmt:
            traverse(node.stmt)

    elif isinstance(node, c_ast.EllipsisParam):
        #print("Ellipsis param")
        # EllipsisParam[]
        # ( ... ) deo u deklaraciji funkcije
        return

    elif isinstance(node, c_ast.EmptyStatement):
        #print("Empty statement")
        # EmptyStatement[]
        return

    elif isinstance(node, c_ast.Enum):
        #print("Enum")
        # Enum[name, values*]
        # enum week{Mon, Tue, Wed, Thur, Fri, Sat, Sun};

        if "enum" in operators:
            operators["enum"] += 1
        else:
            operators["enum"] = 1

        if node.values:
            traverse(node.values)

    elif isinstance(node, c_ast.Enumerator):
        #print("Enumerator: ")
        # Enumerator[name, values*]
        # A name/value pair for enumeration values
        return

    elif isinstance(node, c_ast.EnumeratorList):
        #print("Enumerator list")
        # EnumeratorList[enumerators**]
        # A list of enumerators

        if node.enumerators:
            for enumerator in node.enumerators:
                traverse(enumerator)

    elif isinstance(node, c_ast.ExprList):
        #print("Expr list")
        # ExprList[exprs**]
        # izrazi razdvojeni zarezom

        expr_list = True

        if node.exprs:
            l = len(node.exprs)
            for expr in node.exprs:
                traverse(expr)

        expr_list = False

    elif isinstance(node, c_ast.For):
        #print("For")
        # for (init; cond; next) stmt
        # For: [init*, cond*, next*, stmt*]
        # () se ne racuna

        if "for" in operators:
            operators["for"] += 1
        else:
            operators["for"] = 1

        if node.init:
            traverse(node.init)
        if node.cond:
            traverse(node.cond)
        if node.next:
            traverse(node.next)
        if node.stmt:
            traverse(node.stmt)

    elif isinstance(node, c_ast.FuncCall):
        #print("Func call")
        # FuncCall[name*, args*]
        # name: Id
        # args: ExprList

        loc_exec += 1

        func_call = True

        if node.name:
            traverse(node.name)
        if node.args:
            traverse(node.args)

            # func_call = False

    elif isinstance(node, c_ast.FuncDecl):
        #print("Func decl")

        func_decl = True

        # FuncDecl[args*, type*]
        if node.args:
            traverse(node.args)
        if node.type:
            traverse(node.type)

    elif isinstance(node, c_ast.FuncDef):
        #print("FuncDef")
        # FuncDef [decl*, param_decls**, body*]
        #node.decl.show(attrnames=True, nodenames=True)

        if node.decl:
            traverse(node.decl)
        if node.param_decls:
            for pd in node.param_decls:
                if pd:
                    traverse(pd)
        if node.body:
            traverse(node.body)

        #print('-----------------')
    elif isinstance(node, c_ast.Goto):
        #print("goto")
        # Goto[name]
        # goto label;

        loc_exec += 1

        if "goto" in operators:
            operators["goto"] += 1
        else:
            operators["goto"] = 1

        if node.name:
            if node.name in operators:
                operators[node.name] += 1
            else:
                operators[node.name] = 1

    elif isinstance(node, c_ast.ID):
        #print("ID (", end='')
        # ID[name]

        if assignment:
            #print("assignment): " + str(node.name))
            if node.name in operands:
                operands[node.name] += 1
            else:
                operands[node.name] = 1
            # assignment = False
            return

        if is_return:
            #print("return): " + str(node.name))
            if node.name in operands:
                operands[node.name] += 1
            else:
                operands[node.name] = 1
            is_return = 0
            return

        if array_ref:
            #print("array_ref): " + str(node.name))
            if node.name in operands:
                operands[node.name] += 1
            else:
                operands[node.name] = 1
            array_ref = False
            return

        if func_call:
            #print("func_call): " + str(node.name))
            if node.name in operators:
                operators[node.name] += 1
            else:
                operators[node.name] = 1
            func_call = False
            return

        if binary_op:
            #print("binary_op): " + str(node.name))
            if node.name in operands:
                operands[node.name] += 1
            else:
                operands[node.name] = 1
            return

        if unary_op:
            #print("unary_op): " + str(node.name))
            if node.name in operands:
                operands[node.name] += 1
            else:
                operands[node.name] = 1
            unary_op = False
            return

        if expr_list:
            #print("expr_list): " + str(node.name))
            if node.name in operands:
                operands[node.name] += 1
            else:
                operands[node.name] = 1
            # expr_list = False
            return

        if func_decl:
            #print("func_decl): " + str(node.name))
            func_decl = False
            return

    elif isinstance(node, c_ast.IdentifierType):
        #print("Identifier Type")
        # IdentifierType[names] [long long int]

        id_type = ""
        if node.names:
            for name in node.names:
                id_type += name
                id_type += ' '

        # ako postoje oba, prvo se razresava tpoint
        if tpoint and fpoint:
            #print("tpoint i fpoint")
            for i in range(0, type_pointer):
                id_type += '*'
            #print("id_type: " + id_type)
            type_pointer = 0
            tpoint = False
            if id_type in operands:
                operands[id_type] += 1
            else:
                operands[id_type] = 1
            return

        elif tpoint:
            #print("----> Usao u tpoint: ")
            for i in range(0, type_pointer):
                id_type += '*'
            #print("id_type: " + id_type)
            type_pointer = 0
            tpoint = False
            if id_type in operands:
                operands[id_type] += 1
            else:
                operands[id_type] = 1
            return

        elif fpoint:
            #print("----> Usao u fpoint: ")
            # for i in range(0, func_pointer):
            #    id_type += '*'
            #print("id_type: " + id_type)
            func_pointer = 0
            fpoint = False
            if id_type in operands:
                operands[id_type] += 1
            else:
                operands[id_type] = 1
            return

        else:
            #print("id_type: " + str(id_type))
            if id_type in operands:
                operands[id_type] += 1
            else:
                operands[id_type] = 1
            return

    elif isinstance(node, c_ast.If):
        #print("If")
        # If: [cond*, iftrue*, iffalse*]
        # if (cond*)
        # {
        #   iftrue*
        # }
        # iffalse* -> else {}

        if "if" in operators:
            operators["if"] += 1
        else:
            operators["if"] = 1

        if node.cond:
            traverse(node.cond)
        if node.iftrue:
            traverse(node.iftrue)

        if node.iffalse:
            if "else" in operators:
                operators["else"] += 1
            else:
                operators["else"] = 1

            traverse(node.iffalse)

    elif isinstance(node, c_ast.InitList):
        #print("Init list")
        # InitList: [exprs**]
        if node.exprs:
            for expr in node.exprs:
                traverse(expr)


    elif isinstance(node, c_ast.Label):
        #print("Label")
        # Label[name, stmt*]

        if node.stmt:
            traverse(node.stmt)

    elif isinstance(node, c_ast.NamedInitializer):
        #print("Named Initializer ?")
        # NamedInitializer[name**, expr*]

        if node.name:
            for n in node.name:
                traverse(n)
        if node.expr:
            traverse(node.expr)

    elif isinstance(node, c_ast.ParamList):
        #print("Param list")
        # ParamList[params**]

        if node.params:
            num_params = len(node.params)
            for param in node.params:
                print(param)
                traverse(param)

    elif isinstance(node, c_ast.Pragma):
        #print("Pragma")
        # Pragma[string]

        if "pragma" in operators:
            operators["pragma"] += 1
        else:
            operators["pragma"] = 1

    elif isinstance(node, c_ast.PtrDecl):
        #print("PtrDecl")
        # PtrDecl[quals, type*]

        # const, volatile
        quals = node.quals
        if quals:  # if true
            if (len(quals) == 2):
                # print(quals[0]+"   "+quals[1])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1
                if (quals[1] in operators):
                    operators[quals[1]] += 1
                else:
                    operators[quals[1]] = 1
            else:  # (node.quals() == 1):
                # print(quals[0])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1

        if node.type:
            if isinstance(node.type, c_ast.TypeDecl) or isinstance(node.type, c_ast.PtrDecl):
                tpoint = True
                type_pointer += 1
            elif isinstance(node.type, c_ast.FuncDecl):
                fpoint = True
                func_pointer += 1
            traverse(node.type)

    elif isinstance(node, c_ast.Return):
        #print("Return")

        loc_exec += 1

        is_return = True
        # Return[expr*]
        if "return" in operators:
            operators["return"] += 1
        else:
            operators["return"] = 1

        if node.expr:
            traverse(node.expr)

    elif isinstance(node, c_ast.Struct):
        #print("Struct")
        # Struct[name, decls**]
        '''
            struct Books {
               char  title[50];
               char  author[50];
               char  subject[100];
               int   book_id;
            } book; 
        '''
        if "struct" in operators:
            operators["struct"] += 1
        else:
            operators["struct"] = 1
        # sa struct definisemo tip. ime tipa je operand
        # mozda ne treba da bude operand posto je deklaracija

        if node.name:
            id_type = "" + node.name + " "
            if tpoint:
                # print("----> Usao u tpoint: ")
                for i in range(0, type_pointer):
                    id_type += '*'
                #print("id_type: " + id_type)
                type_pointer = 0
                tpoint = False
                if id_type in operands:
                    operands[id_type] += 1
                else:
                    operands[id_type] = 1
                return

        if node.decls:
            for decl in node.decls:
                traverse(decl)

    elif isinstance(node, c_ast.StructRef):
        #print("Struct ref")
        # #type: . or ->
        # name.field or name->field
        # StructRef: [name*, type, field*]

        if node.type:
            if node.type in operators:
                operators[node.type] += 1
            else:
                operators[node.type] = 1

        if node.name:
            traverse(node.name)
        if node.field:
            traverse(node.field)

    elif isinstance(node, c_ast.Switch):
        #print("Switch")
        # Switch[cond*, stmt*]

        if "switch" in operators:
            operators["switch"] += 1
        else:
            operators["switch"] = 1

        if node.cond:
            traverse(node.cond)
        if node.stmt:
            traverse(node.stmt)

    elif isinstance(node, c_ast.TernaryOp):
        #print("Ternary operator")
        # TernaryOperator[cond*, iftrue*, iffalse*]

        if "?:" in operators:
            operators["?:"] += 1
        else:
            operators["?:"] = 1

        if node.cond:
            traverse(node.cond)
        if node.iftrue:
            traverse(node.iftrue)
        if node.iffalse:
            traverse(node.iffalse)

    elif isinstance(node, c_ast.TypeDecl):
        #print("Type Decl")
        # TypeDecl[declname, quals, type*]

        # node.declname nije bitan jer je u pitanju deklaracija

        if node.type:
            traverse(node.type)
            return

    elif isinstance(node, c_ast.Typedef):
        #print("Typedef")
        # Typedef[name, quals, storage, type*]

        # const, volatile
        quals = node.quals
        if quals:  # if true
            if (len(quals) == 2):
                # print(quals[0]+"   "+quals[1])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1
                if (quals[1] in operators):
                    operators[quals[1]] += 1
                else:
                    operators[quals[1]] = 1
            else:  # (node.quals() == 1):
                # print(quals[0])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1

        # extern, register
        storage = node.storage
        if storage:  # if true
            if (len(storage) == 2):
                # print(storage[0]+"   "+storage[1])
                if (storage[0] in operators):
                    operators[storage[0]] += 1
                else:
                    operators[storage[0]] = 1
                if (storage[1] in operators):
                    operators[storage[1]] += 1
                else:
                    operators[storage[1]] = 1
            else:  # (len(storage) == 1):
                # print(storage[0])
                if (storage[0] in operators):
                    operators[storage[0]] += 1
                else:
                    operators[storage[0]] = 1

        if node.type:
            traverse(node.type)

        # name ne bi trebalo da se racuna u deklaraciji

    elif isinstance(node, c_ast.Typename):
        #print("Typename")
        # Typename[name, quals, type*]

        name = node.name
        if name:
            if name in operands:
                operands[name] += 1
            else:
                operands[name] = 1

        # const, volatile
        quals = node.quals
        if quals:  # if true
            if (len(quals) == 2):
                #print(quals[0] + "   " + quals[1])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1
                if (quals[1] in operators):
                    operators[quals[1]] += 1
                else:
                    operators[quals[1]] = 1
            else:  # (node.quals() == 1):
                # print("******************  "+node.quals[0])
                if (quals[0] in operators):
                    operators[quals[0]] += 1
                else:
                    operators[quals[0]] = 1

        # ! bila neka greska ranije
        if node.type:
            traverse(node.type)

    elif isinstance(node, c_ast.UnaryOp):
        #print("Unary operator")
        # UnaryOperator[op, epxr*]
        unary_op = True

        if "++" in node.op:
            loc_exec += 1
        if "--" in node.op:
            loc_exec += 1

        if node.op:
            if node.op in operators:
                operators[node.op] += 1
            else:
                operators[node.op] = 1

        if node.expr:
            traverse(node.expr)

    elif isinstance(node, c_ast.Union):
        #print("Union")
        # Union[name, decls**]
        '''
        union Data {
           int i;
           float f;
           char str[20];
        };
        '''

        if "union" in operators:
            operators["union"] += 1
        else:
            operators["union"] = 1

            # name ne bi trebalo da se racuna u deklaraciji

        if node.decls:
            for decl in node.decls:
                traverse(decl)

    elif isinstance(node, c_ast.While):
        #print("while")
        # While: [cond*, stmt*]

        if "while" in operators:
            operators["while"] += 1
        else:
            operators["while"] = 1

        if node.cond:
            traverse(node.cond)
        if node.stmt:
            traverse(node.stmt)

    else:
        #print("Error!")
        return

    return

# end traverse

# -------------------------




'''
#----------------------

#ast = parse_file('./pycparser-master/examples/c_files/hash.c', use_cpp=True,
#        cpp_path='gcc',
#        cpp_args=['-E', r'-Iutils/fake_libc_include']
#        )

#ast = parse_file('./pycparser-master/examples/c_files/funky.c', use_cpp=True,
#        cpp_path='gcc',
#        cpp_args=['-E', r'-Iutils/fake_libc_include']
#        )


#ast = parse_file('./pycparser-master/examples/c_files/year.c', use_cpp=True,
#        cpp_path='gcc',
#        cpp_args=['-nostdinc', '-E', r'-Iutils/fake_libc_include']
#        )

# ast = parse_file('./pycparser-master/examples/c_files/memmgr.c', use_cpp=True,
#        cpp_path='gcc',
#        cpp_args=['-nostdinc', '-E', r'-Iutils/fake_libc_include']
#        )


ast = parse_file('./c_files/helloworld.c', use_cpp=True,
        cpp_path='gcc',
        cpp_args=['-nostdinc', '-E', r'-I./pycparser-master/utils/fake_libc_include']
        )

# FileAst[ext**]
for node in ast.ext:
    # print(node)
    traverse(node)
'''

'''
# -----------------------------------------
# file = open("./pycparser-master/examples/c_files/funky.c")

# file = open("./pycparser-master/examples/c_files/hash.c")

# file = open("./pycparser-master/examples/c_files/year.c")

# file = open("./pycparser-master/examples/c_files/memmgr.c")

file = open("./c_files/helloworld.c")
# global loc_total

# file_string = file.read() <-- ovako ne radi kako treba

ff = file.readlines()

loc_total = len(ff)
#print("len(ff): "+str(len(ff)))

file.close()

# file = open("./pycparser-master/examples/c_files/hash.c")

# file = open("./pycparser-master/examples/c_files/year.c")

file = open("./c_files/helloworld.c")

f = file.read()
file.close()

# global loc_blanc
# global ff

loc_blanc = 0
for line in ff:
    if "\n" == line:
        loc_blanc += 1

# import re

# global loc_comments
loc_comments = 0
# prebrojavam komentare
comments = re.findall("(\/\*([^*]|[\r\n]|(\*+([^*\/]|[\r\n])))*\*+\/)|(\/\/.*)", f)
#print(comments)

for comment in comments:
    #print(len(comment[0].split('\n')))
    loc_comments += len(comment[0].split('\n'))

# uklanjamo komentare

file_string = ""
for f in ff:
    file_string += re.sub("(?:\/\/(?:\\\n|[^\n])*\n)|(?:\/\*[\s\S]*?\*\/)|((?:R\"([^(\\\s]{0,16})\([^)]*\)\2\")|(?:@\"[^\"]*?\")|(?:\"(?:\?\?'|\\\\|\\\"|\\\n|[^\"])*?\")|(?:'(?:\\\\|\\'|\\\n|[^'])*?'))", '', f)
#print(file_string)

# num = re.subn("(?:\/\/(?:\\\n|[^\n])*\n)|(?:\/\*[\s\S]*?\*\/)|((?:R\"([^(\\\s]{0,16})\([^)]*\)\2\")|(?:@\"[^\"]*?\")|(?:\"(?:\?\?'|\\\\|\\\"|\\\n|[^\"])*?\")|(?:'(?:\\\\|\\'|\\\n|[^'])*?'))", '', file_string)[1]
# print(str(num))

file_string = re.sub("(?:\/\/(?:\\\n|[^\n])*\n)|(?:\/\*[\s\S]*?\*\/)|((?:R\"([^(\\\s]{0,16})\([^)]*\)\2\")|(?:@\"[^\"]*?\")|(?:\"(?:\?\?'|\\\\|\\\"|\\\n|[^\"])*?\")|(?:'(?:\\\\|\\'|\\\n|[^'])*?'))", '', file_string)
# print(file_string)

# ---------------------

# global operators
# global operands

# parentheses ()
parentheses_left = re.findall("\(", file_string)
parentheses_right = re.findall("\)", file_string)
# print(str(len(parentheses_left)))

# broj () je broj zagrada umanjen za broj zagrada koje se nalaze uz for, if, ...
parentheses_to_deduct = 0
if "for" in operators.keys():
    parentheses_to_deduct += operators["for"]
if "if" in operators.keys():
    parentheses_to_deduct += operators["if"]
if "while" in operators.keys():
    parentheses_to_deduct += operators["while"]
if "do while" in operators.keys():
    parentheses_to_deduct += operators["do while"]
if "switch" in operators.keys():
    parentheses_to_deduct += operators["switch"]
if "sizeof" in operators.keys():
    parentheses_to_deduct += operators["sizeof"]

# print(parentheses_to_deduct)

operators['('] = len(parentheses_left) - parentheses_to_deduct
operators[')'] = len(parentheses_right) - parentheses_to_deduct

# braces {}
braces_left = re.findall("\{", file_string)
operators['{'] = len(braces_left)
braces_right = re.findall("\}", file_string)
operators['}'] = len(braces_right)

# brackets []
brackets_left = re.findall("\[", file_string)
if len(brackets_left):
    operators['['] = len(brackets_left)

brackets_right = re.findall("\]", file_string)
if len(brackets_right):
    operators[']'] = len(brackets_right)

# comma ,
comma = re.findall("\,", file_string)
if len(comma):
    operators[','] = len(comma)

# semicolon ;
semicolon = re.findall("\;", file_string)
if len(semicolon):
    operators[';'] = len(semicolon)

# colon :
colon = re.findall("\:", file_string)
if len(colon):
    ternary_num = 0
    case_num = 0
    default_num = 0
    if "?:" in operators:
        ternary_num = operators["?:"]
    if "case" in operators:
        case_num = operators["case"]
    if "default" in operators:
        default_num = operators["default"]
    deduct_num = ternary_num + case_num + default_num
    if len(colon) - deduct_num:
        operators[':'] = len(colon) - deduct_num

# apostrophe ;
apostrophe = re.findall("\'", file_string)
if len(apostrophe):
    operators['\''] = len(apostrophe)

# quotation :
quotation = re.findall("\"", file_string)
if len(quotation):
    operators['\"'] = len(quotation)

# hashtag #;
hashtag = re.findall("\#", file_string)
if len(hashtag):
    operators['\#'] = len(hashtag)

# double_hashtag ## :
double_hashtag = re.findall("\#\#", file_string)
if len(double_hashtag):
    operators['\#\#'] = len(double_hashtag)

print("--> {operators} : " + str(operators) + '\n')
print("--> {operands} : " + str(operands))

# ----------------------------
# import math

# Halstead metrics
# global operators
# global operands
# global loc_exec
# global loc_total
# global loc_blanc
# global loc_code_and_comment
# global loc_comments

# number of distinct operators n1
n1 = len(operators)
print("* Number of distinct operators (n1): "+str(n1))

# number of distinct operands n2
n2 = len(operands)
print("* Number of distinct operands (n2): "+str(n2))

# number of operators N1
N1 = 0
for key in operators:
    N1 += operators[key]
print("* Number of operators (N1): "+str(N1))

# number of operands N2
N2 = 0
for key in operands:
    N2 += operands[key]
print("* Number of operands (N2): "+str(N2))

# Halstead Length n = N1+N2  | N = N1+N2
N = N1+N2
print("* Halstead Length (N): "+str(N))

# Halstead Volume V = (N1+N2)*(log_2(n1+n2))*N*log_2(n)
V = (N1+N2)*(math.log2(n1+n2))*N*math.log2(N)
print("* Halstead Volume (V): "+str(V))

# ne zanima me Halstead Level / Program Level L = (2*n2)/(n1*N2)
L = (2*n2)/(n1*N2)
print("Halstead Level / Program Level (L): "+str(L))

# Halstead Inteligent Content I = L*V
I = L*V
print("* Halstead Inteligent Content (I): "+str(I))

# Halstead Difficulty D = 1/L = (n1/2)*(N2/n2))
D = 1/L
print("* Halstead Difficulty (D): "+str(D))

# Halstead Error Estimate / Delivered Bugs B = V/3000
B = V/3000
print("* Halstead Error Estimate / Delivered Bugs (B): "+str(B))

# ne zanima me Halstead Effort E = V/L = D*V
E = V/L
print("Halstead Effort (E): "+str(E))

# ne zanima me Halstead Prog Time / Time To Write Program T = E/18
T = E/18
print("Halstead Prog Time / Time To Write Program (T): "+str(T))


# LOC Executable
# Number of executable statements, where an executable statement is a statement specifying an explicit
# action to be taken; i.e. imperative statement
print("LOC_Exec: "+str(loc_exec))
print("LOC_Total: "+str(loc_total))
print("LOC_Blanc: "+str(loc_blanc))

loc_code_and_comment = loc_total - loc_blanc

print("LOC_Code_and_Comment: "+str(loc_code_and_comment))
print("LOC_Comments: "+str(loc_comments))

# --------------------------


new_instance = [loc_blanc, loc_code_and_comment, loc_comments, loc_exec, I, D, E, B, N, L, T, V, N2, N1, n2, n1, loc_total]
print(new_instance)

'''

# loc_exec se racuna u traverse()
# loc_total, loc_blanc, loc_comments, loc_code_and_comment
def loc_metrics(filename):
    global loc_exec
    global loc_total
    global loc_blanc
    global loc_code_and_comment
    global loc_comments

    file = open(filename)
    file_lines = file.readlines()
    file.close()

    file = open(filename)
    file_read = file.read()
    file.close()

    loc_total = len(file_lines)

    loc_blanc = 0
    for line in file_lines:
        if "\n" == line:
            loc_blanc += 1

    loc_comments = 0
    comments = re.findall("(\/\*([^*]|[\r\n]|(\*+([^*\/]|[\r\n])))*\*+\/)|(\/\/.*)", file_read)

    for comment in comments:
        loc_comments += len(comment[0].split('\n'))

    loc_code_and_comment = loc_total - loc_blanc

def Halstead_metrics(filename):
    global operators
    global operands

    global n1
    global n2
    global N1
    global N2
    global N
    global V
    global L
    global I
    global D
    global B
    global T
    global E

    file = open(filename)
    file_lines = file.readlines()
    file.close()

    # uklanjamo komentare
    file_string = ""
    for f in file_lines:
        file_string += re.sub(
            "(?:\/\/(?:\\\n|[^\n])*\n)|(?:\/\*[\s\S]*?\*\/)|((?:R\"([^(\\\s]{0,16})\([^)]*\)\2\")|(?:@\"[^\"]*?\")|(?:\"(?:\?\?'|\\\\|\\\"|\\\n|[^\"])*?\")|(?:'(?:\\\\|\\'|\\\n|[^'])*?'))",
            '', f)

    file_string = re.sub(
        "(?:\/\/(?:\\\n|[^\n])*\n)|(?:\/\*[\s\S]*?\*\/)|((?:R\"([^(\\\s]{0,16})\([^)]*\)\2\")|(?:@\"[^\"]*?\")|(?:\"(?:\?\?'|\\\\|\\\"|\\\n|[^\"])*?\")|(?:'(?:\\\\|\\'|\\\n|[^'])*?'))",
        '', file_string)

    # parentheses ()
    parentheses_left = re.findall("\(", file_string)
    parentheses_right = re.findall("\)", file_string)
    # print(str(len(parentheses_left)))

    # broj () je broj zagrada umanjen za broj zagrada koje se nalaze uz for, if, ...
    parentheses_to_deduct = 0
    if "for" in operators.keys():
        parentheses_to_deduct += operators["for"]
    if "if" in operators.keys():
        parentheses_to_deduct += operators["if"]
    if "while" in operators.keys():
        parentheses_to_deduct += operators["while"]
    if "do while" in operators.keys():
        parentheses_to_deduct += operators["do while"]
    if "switch" in operators.keys():
        parentheses_to_deduct += operators["switch"]
    if "sizeof" in operators.keys():
        parentheses_to_deduct += operators["sizeof"]

    # print(parentheses_to_deduct)

    operators['('] = len(parentheses_left) - parentheses_to_deduct
    operators[')'] = len(parentheses_right) - parentheses_to_deduct

    # braces {}
    braces_left = re.findall("\{", file_string)
    operators['{'] = len(braces_left)
    braces_right = re.findall("\}", file_string)
    operators['}'] = len(braces_right)

    # brackets []
    brackets_left = re.findall("\[", file_string)
    if len(brackets_left):
        operators['['] = len(brackets_left)

    brackets_right = re.findall("\]", file_string)
    if len(brackets_right):
        operators[']'] = len(brackets_right)

    # comma ,
    comma = re.findall("\,", file_string)
    if len(comma):
        operators[','] = len(comma)

    # semicolon ;
    semicolon = re.findall("\;", file_string)
    if len(semicolon):
        operators[';'] = len(semicolon)

    # colon :
    colon = re.findall("\:", file_string)
    if len(colon):
        ternary_num = 0
        case_num = 0
        default_num = 0
        if "?:" in operators:
            ternary_num = operators["?:"]
        if "case" in operators:
            case_num = operators["case"]
        if "default" in operators:
            default_num = operators["default"]
        deduct_num = ternary_num + case_num + default_num
        if len(colon) - deduct_num:
            operators[':'] = len(colon) - deduct_num

    # apostrophe ;
    apostrophe = re.findall("\'", file_string)
    if len(apostrophe):
        operators['\''] = len(apostrophe)

    # quotation :
    quotation = re.findall("\"", file_string)
    if len(quotation):
        operators['\"'] = len(quotation)

    # hashtag #;
    hashtag = re.findall("\#", file_string)
    if len(hashtag):
        operators['\#'] = len(hashtag)

    # double_hashtag ## :
    double_hashtag = re.findall("\#\#", file_string)
    if len(double_hashtag):
        operators['\#\#'] = len(double_hashtag)

    # print("--> {operators} : " + str(operators) + '\n')
    # print("--> {operands} : " + str(operands))

    # number of distinct operators n1
    n1 = len(operators)
    #print("* Number of distinct operators (n1): " + str(n1))

    # number of distinct operands n2
    n2 = len(operands)
    #print("* Number of distinct operands (n2): " + str(n2))

    # number of operators N1
    N1 = 0
    for key in operators:
        N1 += operators[key]
    #print("* Number of operators (N1): " + str(N1))

    # number of operands N2
    N2 = 0
    for key in operands:
        N2 += operands[key]
    #print("* Number of operands (N2): " + str(N2))

    # Halstead Length n = N1+N2  | N = N1+N2
    N = N1 + N2
    #print("* Halstead Length (N): " + str(N))

    # Halstead Volume V = (N1+N2)*(log_2(n1+n2))*N*log_2(n)
    V = (N1 + N2) * (math.log2(n1 + n2)) * N * math.log2(N)
    #print("* Halstead Volume (V): " + str(V))

    # ne zanima me Halstead Level / Program Level L = (2*n2)/(n1*N2)
    L = (2 * n2) / (n1 * N2)
    #print("Halstead Level / Program Level (L): " + str(L))

    # Halstead Inteligent Content I = L*V
    I = L * V
    #print("* Halstead Inteligent Content (I): " + str(I))

    # Halstead Difficulty D = 1/L = (n1/2)*(N2/n2))
    D = 1 / L
    #print("* Halstead Difficulty (D): " + str(D))

    # Halstead Error Estimate / Delivered Bugs B = V/3000
    B = V / 3000
    #print("* Halstead Error Estimate / Delivered Bugs (B): " + str(B))

    # ne zanima me Halstead Effort E = V/L = D*V
    E = V / L
    #print("Halstead Effort (E): " + str(E))

    # ne zanima me Halstead Prog Time / Time To Write Program T = E/18
    T = E / 18
    #print("Halstead Prog Time / Time To Write Program (T): " + str(T))


