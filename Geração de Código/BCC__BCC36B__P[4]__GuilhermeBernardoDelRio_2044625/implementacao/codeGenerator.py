import sys
import numpy as np
import subprocess

from llvmlite import ir
from llvmlite import binding as llvm
import itertools


import tppSemantic

escopo = 'global'
list_var = {'global': []}
list_func = dict()
funcao_saida = False


def retornaTipoLLVM(type):
    if type == "inteiro":
        tipo = ir.IntType(32)
    elif type == "flutuante":
        tipo = ir.FloatType()
    else:
        tipo = ir.VoidType()

    return tipo


def retorna_variavel_lista(variavel):
    global escopo

    nao_encontrado = True
    if escopo in list_var:
        if any(variavel in var for var in list_var[escopo]):
            for var in list_var[escopo]:
                if variavel in var:
                    nao_encontrado = False
                    variavel = var[variavel]
                    break
        else:
            for var in list_var['global']:
                if variavel in var:
                    nao_encontrado = False
                    variavel = var[variavel]
                    break
    else:
        for var in list_var['global']:
            if variavel in var:
                nao_encontrado = False
                variavel = var[variavel]
                break

    if nao_encontrado:
        return None

    return variavel


def declara_variavel_global(node):
    encontrado = False
    tipo_variavel = node.children[0].name
    nome_variavel = node.children[1].name
    dimensao_variavel = 0
    lista_dimensoes = list()

    for var in var_list[nome_variavel]:
        if var[1] == tipo_variavel and var[4] == 'global':
            encontrado = True
            dimensao_variavel = var[2]
            lista_dimensoes = var[3]

    if encontrado:
        # pega o tipo da váriavel
        aux_tipo_variavel = retornaTipoLLVM(tipo_variavel)
        if dimensao_variavel > 0:
            aux_tipo_variavel = retornaTipoLLVM('inteiro')
            for dim in lista_dimensoes:
                aux_tipo_variavel = ir.ArrayType(aux_tipo_variavel, int(dim[0]))

        # Variável global
        aux_variavel = ir.GlobalVariable(modulo, aux_tipo_variavel, nome_variavel)

        if dimensao_variavel == 0:
            # Inicializa a variavel
            if tipo_variavel == 'inteiro':
                aux_variavel.initializer = ir.Constant(aux_tipo_variavel, 0)
            else:
                aux_variavel.initializer = ir.Constant(aux_tipo_variavel, 0.0)
        else:
            aux_variavel.initializer = ir.Constant(aux_tipo_variavel, None)

        # Linkage = common
        aux_variavel.linkage = "common"
        # Define o alinhamento em 4
        aux_variavel.align = 4
        list_var['global'].append({nome_variavel: aux_variavel})

    return encontrado


def declara_variavel_local(var, builder):
    # pega o tipo da váriavel
    aux_tipo_variavel = retornaTipoLLVM(var[1])
    if var[2] > 0:
        aux_tipo_variavel = retornaTipoLLVM('inteiro')
        for dim in var[3]:
            aux_tipo_variavel = ir.ArrayType(aux_tipo_variavel, int(dim[0]))

    # Variável local
    aux_variavel = builder.alloca(aux_tipo_variavel, name=var[0])

    # Inicializa a variavel
    if var[2] == 0:
        if var[1] == 'inteiro':
            aux_variavel.initializer = ir.Constant(aux_tipo_variavel, 0)
        else:
            aux_variavel.initializer = ir.Constant(aux_tipo_variavel, 0.0)
    else:
        aux_variavel.initializer = ir.Constant(aux_tipo_variavel, None)

    # Define o alinhamento em 4
    aux_variavel.align = 4

    if var[4] not in list_var:
        list_var[var[4]] = []
    list_var[var[4]].append({var[0]: aux_variavel})


def gera_retorna(node, builder, tipo_funcao, func):

    # Declara o bloco de fim.
    bloco_saida = func.append_basic_block('exit')

    # Cria um salto para o bloco de saída
    builder.branch(bloco_saida)

    # Adiciona o bloco de saida
    builder.position_at_end(bloco_saida)
    print("node.name", node.name)
    if len(node.children) > 1:
        variavel = node.children[0].name
        operador = node.children[1].name
        var2 = node.children[2].name

        variavel = retorna_variavel_lista(variavel)
        var2 = retorna_variavel_lista(var2)

        if operador == '+':
            builder.ret(builder.add(variavel, var2))
    else:
        is_num = False
        if node.children[0].name.isnumeric():
            is_num = True
            if tipo_funcao == 'inteiro':
                dado_nome = int(node.children[0].name)
            else:
                dado_nome = float(node.children[0].name)
        else:
            dado_nome = node.children[0].name
            print("dado_nome", dado_nome)
        if is_num:
            # Cria um valor zero para colocar no retorno.
            dado = ir.Constant(retornaTipoLLVM(tipo_funcao), dado_nome)

            # Cria o valor de retorno e inicializa com zero.
            # returnVal = builder.alloca(retornaTipoLLVM(tipo_funcao), name='retorno')
            # builder.store(dado, returnVal)

            # Cria o return
            builder.ret(dado)
        else:
            try:
                var = builder.load(retorna_variavel_lista(dado_nome))
            except:
                var = retorna_variavel_lista(dado_nome)
            builder.ret(var)
            print("var", var)


def gera_leia(node, builder):
    variavel = node.children[0].name

    variavel = retorna_variavel_lista(variavel)
    tipo_variavel = variavel.type.pointee.intrinsic_name
    if tipo_variavel == 'i32':
        result_read = builder.call(leiaInteiro, args=[])
    else:
        result_read = builder.call(leiaFlutuante, args=[])

    builder.store(result_read, variavel, align=4)


def gera_escreva(node, builder):
    if len(node.children) == 1:
        variavel = node.children[0].name

        variavel = retorna_variavel_lista(variavel)
        try:
            tipo_variavel = variavel.type.pointee.intrinsic_name
        except:
            tipo_variavel = variavel.type.intrinsic_name

        if tipo_variavel == 'i32':
            try:
                builder.call(escrevaInteiro, args=[variavel])
            except:
                builder.call(escrevaInteiro, args=[builder.load(variavel)])
        else:
            try:
                builder.call(escrevaFlutuante, args=[variavel])
            except:
                builder.call(escrevaFlutuante, args=[builder.load(variavel)])
    elif len(node.children) == 2:
        nome_funcao = node.children[0].name
        tipo_funcao = list_func[nome_funcao].type.pointee.return_type.intrinsic_name

        var1_arg = node.children[1].name
        var1_arg = retorna_variavel_lista(var1_arg)

        escreva_arg = builder.call(list_func[nome_funcao], args=[builder.load(var1_arg)])
        if tipo_funcao == 'i32':
            builder.call(escrevaInteiro, args=[escreva_arg])
        else:
            builder.call(escrevaFlutuante, args=[escreva_arg])

    elif len(node.children) == 4:
        int_ty = ir.IntType(32)

        array_var_name = node.children[0].name
        index_var = node.children[2].name

        array_var = retorna_variavel_lista(array_var_name)
        index_var_load = builder.load(retorna_variavel_lista(index_var))
        array_var_pos = builder.gep(array_var, [int_ty(0), index_var_load], name=f'{array_var_name}[{index_var}]')
        temp_expression = builder.load(array_var_pos, align=4)

        type_array = array_var.type.pointee.element.intrinsic_name
        if type_array == 'i32':
            builder.call(escrevaInteiro, args=[temp_expression])
        else:
            builder.call(escrevaFlutuante, args=[temp_expression])


def gera_atribuicao(node, builder):
    dad = node.parent

    float_ty = ir.FloatType()
    int_ty = ir.IntType(32)

    recive = True
    left = list()
    right = list()
    for children in dad.children:
        if children.name != ':=':
            if recive:
                left.append(children.name)
            else:
                right.append(children.name)
        else:
            recive = False

    variavel = None
    if len(left) == 1:
        variavel = retorna_variavel_lista(left[0])
    else:
        array_left = retorna_variavel_lista(left[0])
        if len(left) == 4:
            expression = builder.load(retorna_variavel_lista(left[2]))
            variavel = builder.gep(array_left, [int_ty(0), expression], name=left[0]+'_'+left[2])
        else:
            expressions = list()
            for indice in [left[2], left[4]]:
                if indice.isnumeric():
                    expressions.append(int_ty(indice))
                else:
                    expressions.append(builder.load(retorna_variavel_lista(indice)))

            operador = left[3]
            if operador == '+':
                expression = builder.add(expressions[0], expressions[1],
                                         name=left[0]+'_'+left[2]+left[3]+left[4], flags=())
            else:
                expression = builder.sub(expressions[0], expressions[1],
                                         name=left[0] + '_' + left[2] + left[3] + left[4], flags=())

            variavel = builder.gep(array_left, [int_ty(0), expression], name=left[0] + '_' + left[2] + left[3] + left[4])

    try:
        tipo_variavel = variavel.type.pointee.intrinsic_name
    except:
        tipo_variavel = variavel.type.intrinsic_name

    next_operation = 'add'
    if tipo_variavel == 'i32':
        expression = ir.Constant(ir.IntType(32), 0)
    else:
        expression = ir.Constant(ir.FloatType(), float(0))

    index = 0
    while index < len(right):
        if tipo_variavel == 'i32':
            temp_expression = ir.Constant(ir.IntType(32), 0)
        else:
            temp_expression = ir.Constant(ir.FloatType(), float(0))

        if right[index] != '+' and right[index] != '-' and right[index] != '*':

            if tipo_variavel != 'i32':
                if right[index] not in list_func and retorna_variavel_lista(right[index]) is None:
                    dado = float(right[index])
                    temp_expression = ir.Constant(ir.FloatType(), dado)
            if right[index].isnumeric():
                dado = int(right[index])
                temp_expression = ir.Constant(ir.IntType(32), dado)

            elif right[index] in list_func:
                num_vars = func_list[right[index]][0][2]
                func = list_func[right[index]]
                args = list()
                aux = 0

                for next_index in range(index + 1, index + num_vars + 1):
                    if right[next_index].isnumeric():
                        param_name = func_list[right[index]][0][3][aux]
                        type_param_name = var_list[param_name][0][1]
                        if type_param_name == 'inteiro':
                            dado = int(right[next_index])
                            args.append(ir.Constant(ir.IntType(32), dado))
                        else:
                            dado = float(right[next_index])
                            args.append(ir.Constant(ir.FloatType(), dado))

                    elif retorna_variavel_lista(right[next_index]) is None:
                        if right[next_index] == "soma":
                            print("right[next_index-1]", right[next_index-1])
                            print("right[next_index]", right[next_index])
                            print("right[next_index]", right[next_index1])


                            right[next_index] = "+"
                        dado = float(right[next_index])
                        args.append(ir.Constant(ir.FloatType(), dado))

                    else:
                        args.append(builder.load(retorna_variavel_lista(right[next_index])))

                    aux += 1

                temp_expression = builder.call(func, args=args)
                index = index + num_vars
            elif retorna_variavel_lista(right[index]) is not None:
                if tipo_variavel == 'i32':
                    if len(right) > index + 1 and right[index + 1] == '[':
                        array_var = right[index]
                        index_var = right[index + 2]

                        array_var = retorna_variavel_lista(array_var)
                        index_var_load = builder.load(retorna_variavel_lista(index_var))
                        array_var_pos = builder.gep(array_var, [int_ty(0), index_var_load], name=f'{right[index]}[{right[index + 2]}]')
                        temp_expression = builder.load(array_var_pos, align=4)

                        index += 3
                    else:
                        try:
                            temp_expression = builder.load(retorna_variavel_lista(right[index]))
                        except:
                            temp_expression = retorna_variavel_lista(right[index])

            if next_operation == 'add':
                if expression.type.intrinsic_name != 'i32' or temp_expression.type.intrinsic_name != 'i32':
                    expression = builder.fadd(expression, temp_expression, name='expression', flags=())
                else:
                    expression = builder.add(expression, temp_expression, name='expression', flags=())
            if next_operation == 'sub':
                expression = builder.sub(expression, temp_expression, name='expression', flags=())
            elif next_operation == 'mul':
                expression = builder.mul(expression, temp_expression, name='expression', flags=())
        else:
            if right[index] == '+':
                next_operation = 'add'
            elif right[index] == '-':
                next_operation = 'sub'
            elif right[index] == '*':
                next_operation = 'mul'

        index += 1

    try:
        builder.store(expression, variavel)
    except:
        builder.store(expression, variavel)
        # builder.store(var_pointer, variavel)


def gera_se(node, builder, tipo_funcao, func):
    if node.children[1].name == 'corpo':
        corps = 2
    else:
        corps = 1

    iftrue = func.append_basic_block('iftrue')
    iffalse = func.append_basic_block('iffalse')
    ifend = func.append_basic_block('ifend')

    comparation_list = list()
    comparation_list.append(node.children[2].name)
    type_comparation = node.children[3].name
    comparation_list.append(node.children[4].name)

    int_ty = ir.IntType(32)
    var_comper_right = builder.alloca(ir.IntType(32), name='var_comper_right')
    var_comper_left = builder.alloca(ir.IntType(32), name='var_comper_left')

    print("comparation_list", comparation_list)
    for index in range(len(comparation_list)):
        if comparation_list[index] in list_func:
            pass
        elif retorna_variavel_lista(comparation_list[index]) is None:
            dado = int(comparation_list[index])
            builder.store(int_ty(dado), var_comper_right)
            comparation_list[index] = ir.Constant(int_ty, int_ty(dado))
        else:
            comparation_list[index] = retorna_variavel_lista(comparation_list[index])
            if comparation_list[index].type.intrinsic_name == 'p0i32':
                var_comper_left = comparation_list[index]
            else:
                builder.store(comparation_list[index], var_comper_left)

    print("type_comparation", type_comparation)
    if_state = builder.icmp_signed(type_comparation, var_comper_left, var_comper_right, name='if_test')
    print("if_state", if_state)
    builder.cbranch(if_state, iftrue, iffalse)

    builder.position_at_end(iftrue)
    percorre_arvore(node.children[0], builder, tipo_funcao, func)
    try:
        builder.branch(ifend)
    except:
        pass

    if corps == 2:
        builder.position_at_end(iffalse)

        percorre_arvore(node.children[1], builder, tipo_funcao, func)
        try:
            builder.branch(ifend)
        except:
            pass

    builder.position_at_end(ifend)


def gera_repita(node, builder, tipo_funcao, func):

    comparation_list = list()
    comparation_list.append(node.children[2].name)
    type_comparation = node.children[3].name
    comparation_list.append(node.children[4].name)

    if type_comparation == '=':
        type_comparation = '=='

    int_ty = ir.IntType(32)
    var_comper = builder.alloca(ir.IntType(32), name='var_comper')
    any_value = True

    for index in range(len(comparation_list)):
        if comparation_list[index] in list_func:
            pass
        elif retorna_variavel_lista(comparation_list[index]) is None:
            any_value = False
            dado = int(comparation_list[index])
            builder.store(int_ty(dado), var_comper)
            comparation_list[index] = ir.Constant(ir.IntType(32), int_ty(dado))
        else:
            comparation_list[index] = retorna_variavel_lista(comparation_list[index])

    loop = builder.append_basic_block('loop')
    lopp_val = builder.append_basic_block('loop_val')
    loop_end = builder.append_basic_block('loop_end')

    # if type_comparation == '==':
    #     builder.cbranch(builder.not_(expression), loop, loop_end)
    # else:
    #     builder.cbranch(expression, loop, loop_end)
    # builder.position_at_end(loop)
    builder.branch(loop)

    builder.position_at_end(loop)
    percorre_arvore(node.children[0], builder, tipo_funcao, func)
    builder.branch(lopp_val)

    builder.position_at_end(lopp_val)
    if any_value:
        if comparation_list[0].type.is_pointer and not comparation_list[1].type.is_pointer:
            expression = builder.icmp_signed(type_comparation, builder.load(comparation_list[0]),
                                             comparation_list[1], name='expression')
        elif comparation_list[0].type.is_pointer and comparation_list[1].type.is_pointer:
            expression = builder.icmp_signed(type_comparation, builder.load(comparation_list[0]),
                                             builder.load(comparation_list[1]), name='expression')
        else:
            expression = builder.icmp_signed(type_comparation, comparation_list[0], comparation_list[1], name='expression')
    else:
        if comparation_list[0].type.is_pointer and var_comper.type.is_pointer:
            expression = builder.icmp_signed(type_comparation, builder.load(comparation_list[0]),
                                             builder.load(var_comper), name='expression')
        elif not comparation_list[0].type.is_pointer and var_comper.type.is_pointer:
            expression = builder.icmp_signed(type_comparation, comparation_list[0],
                                             builder.load(var_comper), name='expression')

    if type_comparation == '==':
        builder.cbranch(expression, loop_end, loop)
    else:
        builder.cbranch(expression, loop, loop_end)
    # builder.position_at_end(loop)

    # expression = builder.icmp_signed(type_comparation, comparation_list[0], var_comper, name='expression')
    # builder.cbranch(builder.not_(expression), loop, loop_end)
    builder.position_at_end(loop_end)


def gera_funcao(node, builder):
    int_ty = ir.IntType(32)
    func_name = node.name

    node_params = []
    dad = node.parent
    for children in dad.children:
        if children != node:
            node_params.append(children)

    if len(node_params) == 1:
        param = node_params[0].name

        if param.isnumeric():
            func_aux = list_func[func_name]
            param_type = func_aux.args[0].type.intrinsic_name
            if param_type == 'i32':
                dado = int_ty(int(param))
            else:
                dado = ir.Constant(ir.FloatType(), float(param))
            builder.call(func_aux, [dado])
        else:
            pass
    else:
        pass


def percorre_arvore(node, builder, tipo_funcao, func):
    global funcao_saida
    if node.name == 'retorna':
        funcao_saida = True
        gera_retorna(node, builder, tipo_funcao, func)
        return
    if node.name == 'leia':
        gera_leia(node, builder)
        return
    if node.name == 'escreva':
        gera_escreva(node, builder)
        return
    if node.name == ':=':
        gera_atribuicao(node, builder)
        return
    if node.name == 'se':
        gera_se(node, builder, tipo_funcao, func)
        return
    if node.name == 'repita':
        gera_repita(node, builder, tipo_funcao, func)
        return
    if node.name in list_func:
        gera_funcao(node, builder)
        return

    for no in node.children:
        percorre_arvore(no, builder, tipo_funcao, func)


def declara_funcoes(node):
    global escopo, funcao_saida
    funcao_saida = False
    tipo_funcao = node.children[0].name
    if tipo_funcao != 'inteiro' and tipo_funcao != 'flutuante':
        tipo_funcao = 'vazio'

    if tipo_funcao != 'vazio':
        nome_funcao = node.children[1].name
    else:
        nome_funcao = node.children[-2].name

    escopo = nome_funcao
    # Declara o tipo do retorno da função.
    tipo_retorno_funcao = retornaTipoLLVM(tipo_funcao)
    # Cria a função.
    lista_parametros = list()
    for var_param in func_list[nome_funcao][0][3]:
        for var in var_list[var_param]:
            if var[4] == nome_funcao:
                lista_parametros.append(retornaTipoLLVM(var[1]))

    t_func = ir.FunctionType(tipo_retorno_funcao, lista_parametros)

    # Declara a função.
    if nome_funcao == 'principal':
        func = ir.Function(modulo, t_func, name='main')
    else:
        func = ir.Function(modulo, t_func, name=nome_funcao)

    for index in range(len(func_list[nome_funcao][0][3])):
        func.args[index].name = func_list[nome_funcao][0][3][index]
        if nome_funcao not in list_var:
            list_var[nome_funcao] = []
        list_var[nome_funcao].append({func_list[nome_funcao][0][3][index]: func.args[index]})

    # Declara o bloco de  inicio.
    bloco_entrada = func.append_basic_block('entry')

    # Adiciona o bloco de entrada.
    builder = ir.IRBuilder(bloco_entrada)

    for elemento in var_list:
        for var in var_list[elemento]:
            if var[4] == nome_funcao:
                if var[0] not in func_list[var[4]][0][3]:
                    declara_variavel_local(var, builder)

    percorre_arvore(node, builder, tipo_funcao, func)

    if not funcao_saida:
        # Declara o bloco de fim.
        bloco_saida = func.append_basic_block('exit')
        # Cria um salto para o bloco de saída
        builder.branch(bloco_saida)

        # Adiciona o bloco de saida
        builder.position_at_end(bloco_saida)

        if tipo_funcao != 'vazio':
            # Cria um valor zero para colocar no retorno.
            Zero64 = ir.Constant(tipo_retorno_funcao, 0)

            # Cria o valor de retorno e inicializa com zero.
            returnVal = builder.alloca(tipo_retorno_funcao, name='retorno')
            builder.store(Zero64, returnVal)

            # Cria o return
            returnVal_temp = builder.load(returnVal, name='ret_temp', align=4)
            builder.ret(returnVal_temp)
        else:
            builder.ret_void()

    list_func[nome_funcao] = func
    escopo = 'global'


def generate_code(root):
    for children in root.children:
        if children.name == 'declaracao_variaveis':
            declara_variavel_global(children)
        if children.name == 'declaracao_funcao':
            declara_funcoes(children)


if __name__ == '__main__':
    root, func_list, var_list, message_list = tppSemantic.main()
    for message in message_list:
        if message[0] == 'ERROR':
            print('Não foi possível gerar o código intermediário devido a erros no código!')
            exit()

    file_name = sys.argv[1].split('/')[-1].split('.')[0]

    llvm.initialize()
    llvm.initialize_all_targets()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    # Cria o módulo.
    modulo = ir.Module(f'{file_name}.bc')
    modulo.triple = llvm.get_default_triple()

    target = llvm.Target.from_triple(modulo.triple)
    target_machine = target.create_target_machine()

    modulo.data_layout = target_machine.target_data

    escrevaInteiro = ir.Function(modulo, ir.FunctionType(ir.VoidType(), [ir.IntType(32)]), name="escrevaInteiro")
    escrevaFlutuante = ir.Function(modulo, ir.FunctionType(ir.VoidType(), [ir.FloatType()]), name="escrevaFlutuante")
    leiaInteiro = ir.Function(modulo, ir.FunctionType(ir.IntType(32), []), name="leiaInteiro")
    leiaFlutuante = ir.Function(modulo, ir.FunctionType(ir.FloatType(), []), name="leiaFlutuante")

    generate_code(root)

    # Salva o Módulo
    arquivo = open(f'geracao-codigo-testes/{file_name}.ll', 'w')
    print(str(modulo))
    arquivo.write(str(modulo))
    arquivo.close()

    bashCommands = ["clang -emit-llvm -S io.c", "llc -march=x86-64 -filetype=obj io.ll -o io.o",
                    f'llvm-link geracao-codigo-testes/{file_name}.ll io.ll -o geracao-codigo-testes/{file_name}.bc',
                    f'clang geracao-codigo-testes/{file_name}.bc -o geracao-codigo-testes/{file_name}.o',
                    f'rm geracao-codigo-testes/{file_name}.bc']
    for bashCommand in bashCommands:
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()