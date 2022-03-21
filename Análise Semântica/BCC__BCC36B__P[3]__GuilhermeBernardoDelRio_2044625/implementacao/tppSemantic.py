import sys
import numpy as np

from tabulate import tabulate
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter

import tppparser

def encontra_parametros(root, escopo, lista_nos):
    
    for no in root.children:
        if no.label == 'chamada_funcao':
            nome_funcao = no.descendants[1].label
            tipo_funcao = function_list[nome_funcao][0][1]
            lista_nos.append((nome_funcao, tipo_funcao))
            return lista_nos
        elif no.label == 'ID':
            nome_variavel = no.children[0].label
            tipo_variavel = ''
            if nome_variavel in var_list:
                for variavel in var_list[nome_variavel]:
                    if variavel[4] == escopo:
                        tipo_variavel = variavel[1]
                        break

                if tipo_variavel == '':
                    for variavel in var_list[nome_variavel]:
                        if variavel[4] == 'global':
                            tipo_variavel = variavel[1]
                            break

                lista_nos.append((nome_variavel, tipo_variavel))
                return lista_nos
        elif no.label == 'numero':
            tipo_numero = no.children[0].label

            if tipo_numero == 'NUM_INTEIRO':
                num = int(no.descendants[1].label)
                tipo_numero = 'inteiro'
            else:
                tipo_numero = 'flutuante'
                num = float(no.descendants[1].label)

            lista_nos.append((num, tipo_numero))
            return lista_nos

        lista_nos = encontra_parametros(no, escopo, lista_nos)

    return lista_nos


def encontra_funcoes_chamadas(linha, function_list):
    for elemento in function_list:
        for funcao in function_list[elemento]:
            if funcao[5] <= linha < funcao[6]:
                return funcao[0]

def encontra_todos_nos(root, label, lista_nos):
    for no in root.children:
        lista_nos = encontra_todos_nos(no, label, lista_nos)
        if no.label == label:
            lista_nos.append(no)

    return lista_nos

def encontra_nos_pais(filho, label, lista_nos):
    for index in range(len(filho.anchestors)-1, -1, -1):
        if filho.anchestors[index].label == label:
            lista_nos.append(filho.anchestors[index])

    return lista_nos

def corrige_tupla(lst):
    return [t for t in (set(tuple(i) for i in lst))]

def checa_vetor_variaveis(var_list, message_list):
    for elemento in var_list:
        for variavel in var_list[elemento]:
            if variavel[2] != 0:
                for dimensao in variavel[3]:
                    tamanho_vetor = 0
                    if dimensao[1] != 'NUM_INTEIRO':
                        tamanho_vetor = float(dimensao[0])
                        mensagem = ('ERROR',
                                   f'Erro na linha {variavel[5]}: Índice de array ‘{variavel[0]}’ não inteiro.')
                        message_list.append(mensagem)
                    else:
                        tamanho_vetor = int(dimensao[0])
                for chamada in variavel[-1]:
                    numero = encontra_todos_nos(chamada[1].descendants[3], 'numero', list())
                    if len(numero) > 0:
                        if len(encontra_todos_nos(numero[0], 'NUM_PONTO_FLUTUANTE', list())) > 0:
                            mensagem = ('ERROR',
                                       f'Erro na linha {variavel[5]}: Índice de array ‘{variavel[0]}’ não inteiro.')
                            message_list.append(mensagem)
                        else:
                            numero = int(numero[0].descendants[-1].label)
                            if numero > tamanho_vetor - 1:
                                mensagem = ('ERROR',
                                           f'Erro na linha {variavel[5]}: Índice de array ‘{variavel[0]}’ fora do intervalo (out of range).')
                                message_list.append(mensagem)

def checa_tipo_atribuicao(var_list, message_list, root):
    nos = encontra_todos_nos(root, 'atribuicao', list())

    for index in range(len(nos)):
        try:
            escopo_lido = encontra_nos_pais(nos[index], 'cabecalho', list())[0].descendants[1].label
        except:
            escopo_lido = 'global'

        direita = encontra_parametros(nos[index], escopo_lido, list())
        esquerda = direita.pop(0)

        tipo_diferente = False
        for variavel in direita:
            if variavel[1] != esquerda[1] and variavel[1] != '':

                tipo_diferente = variavel[1]
                mensagem = ('WARNING',
                           f'Aviso: Coerção implícita do valor atribuído para ‘{esquerda[0]}’, variavel {esquerda[0]} {esquerda[1]} recebendo um {variavel[-1]}.')
                message_list.append(mensagem)

        if tipo_diferente and tipo_diferente != esquerda[1]:
            mensagem = ('WARNING',
                       f'Aviso: Atribuição de tipos distintos ‘{esquerda[0]}’ {esquerda[1]} e ‘{variavel[0]}’ {tipo_diferente}')
            message_list.append(mensagem)

def checa_chamada_variaveis(var_list, message_list, root):
    nos_lidos = encontra_todos_nos(root, 'LEIA', list())

    for index in range(len(nos_lidos)):
        nos_lidos[index] = nos_lidos[index].anchestors[-1]
        escopo_lido = encontra_nos_pais(nos_lidos[index], 'cabecalho', list())[0].descendants[1].label
        id_lido = encontra_todos_nos(nos_lidos[index], 'ID', list())[0].children[0].label

        for variavel in var_list[id_lido]:
            encontra = False
            if variavel[4] == escopo_lido:
                encontra = True
                if len(variavel[-1]) == 0:
                    mensagem = ('WARNING',
                               f'Aviso na linha {variavel[5]}: Variável ‘{id_lido}’ declarada e não utilizada. ')
                    message_list.append(mensagem)

            if not encontra:
                for variavel in var_list[id_lido]:
                    if variavel[4] == 'global':
                        if len(variavel[-1]) == 0:
                            mensagem = ('WARNING',
                                       f'Aviso na linha {variavel[5]}: Variável ‘{id_lido}’ declarada e não utilizada. ')
                            message_list.append(mensagem)

    for elemento in var_list:
        for variavel in var_list[elemento]:
            if len(variavel[-1]) == 0:
                mensagem = ('WARNING',
                           f'Aviso na linha {variavel[5]}: Variável ‘{variavel[0]}’ declarada e não utilizada. ')
                message_list.append(mensagem)

            if len(var_list[elemento]) > 1:
                for variavel_duplicada in var_list[elemento]:
                    if variavel_duplicada != variavel and variavel_duplicada[4] == variavel[4]:
                        mensagem = ('WARNING', f'Aviso na linha {variavel[5]}: Variável ‘{variavel_duplicada[0]}‘ já declarada anteriormente.')
                        message_list.append(mensagem)

def checa_chamada_funcoes(function_list, message_list):
    mensagem = ''
    for elemento in function_list:
        for funcao in function_list[elemento]:
            if not funcao[-2]:
                mensagem = ('ERROR',
                           f'Erro na linha {funcao[-1][0][0]}: Chamada a função {elemento} que não foi declarada.')
                message_list.append(mensagem)

            else:
                if len(funcao[-1]) == 0 and elemento != 'principal':
                    mensagem = ('WARNING',
                               f'Aviso na linha {funcao[5]}: Função {elemento} declarada, mas não utilizada.')
                    message_list.append(mensagem)
                else:
                    chamadas = 0
                    recursao = 0
                    for chamar_funcao in funcao[-1]:
                        funcoes_chamadas = encontra_funcoes_chamadas(chamar_funcao[0], function_list)
                        if funcoes_chamadas != elemento:
                            chamadas += 1
                        else:
                            recursao += 1

                    if elemento == 'principal':
                        chamadas += 1

                    if chamadas == 0:
                        mensagem = ('WARNING',
                                   f'Aviso na linha {funcao[5]}: Função {elemento} declarada, mas não utilizada.')
                        message_list.append(mensagem)

                    elif recursao > 0:
                        mensagem = ('WARNING',
                                   f'Aviso na linha {funcao[5]}: Chamada recursiva para {elemento}.')
                        message_list.append(mensagem)

                for chamada in funcao[-1]:
                    lista_parametros = encontra_parametros(chamada[1].children[2], funcao[0], list())

                    if len(lista_parametros) > funcao[2]:
                        mensagem = ('ERROR',
                                   f'Erro na linha {funcao[-1][0][0]}: Chamada à função {funcao[0]} com número de parâmetros maior que o declarado.')
                        message_list.append(mensagem)
                    elif len(lista_parametros) < funcao[2]:
                        mensagem = ('ERROR',
                                   f'Erro na linha {funcao[-1][0][0]}: Chamada à função {funcao[0]} com número de parâmetros menor que o declarado.')
                        message_list.append(mensagem)
                    else:
                        parametros = []
                        for funcao in function_list[chamada[1].descendants[1].label]:
                            for var_func in funcao[3]:
                                for index in range(len(var_list[var_func])):
                                    if var_list[var_func][index][4] == chamada[1].descendants[1].label:
                                        parametros.append((var_list[var_func][index][0], var_list[var_func][index][1]))
                                        break

                        for index in range(len(parametros)):
                            index_tipo = lista_parametros[index][1]
                            if index_tipo == 'NUM_PONTO_FLUTUANTE':
                                index_tipo = 'flutuante'
                            else:
                                index_tipo = 'inteiro'
                            if parametros[index][1] != index_tipo:
                                mensagem = ('WARNING',
                                           f'Aviso: Coerção implícita do valor passado para váriavel ' +
                                           f'‘{parametros[index][0]}‘ da função ‘{chamada[1].descendants[1].label}’.')
                                message_list.append(mensagem)


def checa_retorno(function_list, message_list):
    mensagem = ''
    for elemento in function_list:
        for function in function_list[elemento]:
            tipo_funcao = function[1]

            retorna_tipo = list()
            for tipo_retorno in function[4]:
                retorna_tipo.append(tipo_retorno[0])

            retorna_tipo = list(set(retorna_tipo))

            if tipo_funcao == 'vazio':
                if len(retorna_tipo) > 0:
                    if len(retorna_tipo) > 1:
                        mensagem = ('ERROR',
                                   f'Erro na linha {function[6]-1}: Função {elemento} deveria retornar vazio, mas retorna {retorna_tipo[0]} e {retorna_tipo[1]}.')
                    else:
                        mensagem = ('ERROR',
                                   f'Erro na linha {function[6]-1}: Função {elemento} deveria retornar vazio, mas retorna {retorna_tipo[0]}.')
            elif tipo_funcao == 'inteiro':
                if len(retorna_tipo) == 0:
                    mensagem = ('ERROR',
                               f'Erro na linha {function[6]-1}: Função {elemento} deveria retornar inteiro, mas retorna vazio.')
                else:
                    for tipo_retorno in retorna_tipo:
                        if tipo_retorno != 'inteiro' and tipo_retorno != 'ERROR':
                            mensagem = ('ERROR',
                                       f'Erro na linha {function[6]-1}: Função {elemento} deveria retornar inteiro, mas retorna flutuante.')
                            break
            elif tipo_funcao == 'flutuante':
                if len(retorna_tipo) == 0:
                    mensagem = ('ERROR',
                               f'Erro na linha {function[6]-1}: Função {elemento} deveria retornar flutuante, mas retorna vazio.')
                else:
                    for tipo_retorno in retorna_tipo:
                        if tipo_retorno != 'flutuante' and tipo_retorno != 'ERROR':
                            mensagem = ('ERROR',
                                       f'Erro na linha {function[6]-1}: Função {elemento} deveria retornar flutuante, mas retorna inteiro.')
                            break

            if mensagem != '':
                message_list.append(mensagem)


def checa_principal(function_list, message_list):
    if 'principal' not in function_list or not function_list['principal'][0][7]:
        mensagem_erro = (
            'ERROR', f'Erro: Função principal não declarada.')
        message_list.append(mensagem_erro)
    else:
        inicio_linha = function_list['principal'][0][5]
        finao_linha = function_list['principal'][0][6]

        for chamada in function_list['principal'][0][-1]:
            if not inicio_linha <= chamada[0] < finao_linha:
                mensagem_erro = (
                    'ERROR', f'Erro na linha {chamada[0]}: Chamada para a função principal não permitida.')
                message_list.append(mensagem_erro)

def checa_semantica(function_list, var_list, message_list, tabela_funcoes, tabela_variaveis, root):
    checa_principal(function_list, message_list)
    checa_retorno(function_list, message_list)
    checa_chamada_funcoes(function_list, message_list)
    checa_chamada_variaveis(var_list, message_list, root)
    checa_tipo_atribuicao(var_list, message_list, root)
    checa_vetor_variaveis(var_list, message_list)

def get_var_escopo(elemento, escopo):
    for variavel in var_list[elemento]:
        if variavel[4] == escopo:
            return variavel

def gera_tabela_funcoes(list, header, index_lista):
    tabela = [header]

    for elemento in list:
        for function in list[elemento]:
            aux_array = []
            for index in index_lista:
                aux_array.append(function[index])
            tabela.append(aux_array)
    return tabela

def gera_tabela_variaveis(list, header, list_index):
    table = [header]

    for element in list:
        for func in list[element]:
            aux_array = []
            for index in list_index:
                if index == 3:
                    dim_tam = []
                    for j in range(len(func[index])):
                        if func[index][j][1] == 'NUM_PONTO_FLUTUANTE':
                            value = float(func[index][j][0])
                        else:
                            value = int(func[index][j][0])
                        dim_tam.append(value)
                    aux_array.append(dim_tam)
                else:
                    aux_array.append(func[index])
            table.append(aux_array)

    return table

def verifica_escopo(var_list, function_list):
    # Verifica se o escopo está correto, ou seja, se a variavel foi declarada dentro do escopo da função
    for elemento in var_list:
        for index_var in range(len(var_list[elemento])):
            escopo_atual = var_list[elemento][index_var][4]
            if escopo_atual != 'global':
                tamanho_lista = len(var_list[elemento][index_var][-1])
                index_tupla = 0
                while index_tupla < tamanho_lista:
                    tupla = var_list[elemento][index_var][-1][index_tupla]
                    if not (function_list[escopo_atual][0][5] <= tupla[0] < function_list[escopo_atual][0][6]):
                        novo_escopo = get_var_escopo(elemento, 'global')
                        novo_escopo =[-1].append(tupla)
                        var_list[elemento][index_var][-1].pop(index_tupla)
                        tamanho_lista -= 1
                        index_tupla -= 1
                    index_tupla += 1

def gera_tabelas(function_list, var_list):
    tabela_funcoes = gera_tabela_funcoes(function_list, ['Lexema', 'Tipo', 'Número de Parâmetros', 'Parâmetros', 
                                                            'Init', 'Linha Inicial', 'Linha Final'], 
                                                            [0, 1, 2, 3, 7, 5, 6])

    tabela_variaveis =  gera_tabela_variaveis(var_list, ['Lexema', 'Tipo', 'Dimensões', 'Tamanho Dimensões', 
                                                            'Escopo', 'Linha'], [0, 1, 2, 3, 4, 5])

    print(f'TABELA DE FUNÇÕES:\n{tabulate(tabela_funcoes, headers="firstrow", tablefmt="fancy_grid")}')
    print('\n\n')
    print(f'TABELA DE VARIÁVEIS:\n{tabulate(tabela_variaveis, headers="firstrow", tablefmt="fancy_grid")}')
    print('\n\n')

    return tabela_funcoes, tabela_variaveis

def poda_arvore(root, labels):
    for no in root.children:
        poda_arvore(no, labels)

    if root.label in labels:
        pai = root.parent
        aux = []
        for children in pai.children:
            if children != root:
                aux.append(children)
        for children in root.children:
            aux.append(children)
        root.children = aux
        pai.children = aux

    if root.label == 'declaracao_funcao':
        corpo = root.children[1]
        aux = []
        for children in root.children:
            if children.label == 'fim':
                aux.append(corpo)
            if children != corpo:
                aux.append(children)
        root.children = aux

    if root.label == 'corpo' and len(root.children) == 0:
        pai = root.parent
        aux = []
        for children in pai.children:
            if children != root:
                aux.append(children)
        for children in root.children:
            aux.append(children)
        root.children = aux
        pai.children = aux

def ajusta_arvore(root, ajusta_labels):
    for no in root.children:
        ajusta_arvore(no, ajusta_labels)

    pai = root.parent
    aux = []

    if root.label == 'repita' and len(root.children) > 0:
        for children in root.children:
            if children.label != 'repita':
                aux.append(children)
        root.children = aux
        aux = []

    if root.label == 'e' and root.children[0].label == '&&':
        root.children = []
        root.label = '&&'
        root.name = '&&'

    if root.label == 'ou' and root.children[0].label == '||':
        root.children = []
        root.label = '||'
        root.name = '||'


    if root.label == 'se' and len(root.children) > 0:
        for children in root.children:
            if children.label != 'se':
                aux.append(children)

        root.children = aux
        aux = []

    if root.label == 'ATE':
        root.children = []
        root.label = 'até'
        root.name = 'até'

    if root.label == 'leia' or root.label == 'escreva' or root.label == 'retorna':
        if len(root.children) == 0:
            for children in pai.children:
                if children != root:
                    aux.append(children)

            pai.children = aux

def arruma_arvore(root):
    print('\n\n')
    
    labels = ['ID', 'var', 'lista_variaveis', 'dois_pontos', 'tipo',
                        'INTEIRO', 'FLUTUANTE', 'NUM_INTEIRO', 'NUM_PONTO_FLUTUANTE',
                        'NUM_NOTACAO_CIENTIFICA', 'LEIA', 'abre_parentese', 'fecha_parentese',
                        'lista_declaracoes', 'declaracao', 'indice', 'numero', 'fator',
                        'abre_colchete', 'fecha_colchete', 'expressao', 'expressao_logica',
                        'expressao_simples', 'expressao_aditiva', 'expressao_multiplicativa',
                        'expressao_unaria', 'inicializacao_variaveis', 'ATRIBUICAO', 'atribuicao',
                        'operador_soma', 'mais', 'chamada_funcao', 'lista_argumentos', 'VIRGULA',
                        'virgula', 'fator', 'cabecalho', 'FIM', 'lista_parametros', 'vazio',
                        '(', ')', ':', ',', 'RETORNA', 'ESCREVA', 'SE', 'ENTAO', 'SENAO', 'maior',
                        'menor', 'REPITA', 'igual', 'menos', 'menor_igual', 'maior_igual', 'operador_logico',
                        'operador_multiplicacao', 'vezes']
    ajusta_labels = [':=', '+', '*', '-', '/']
    poda_arvore(root, labels)
    ajusta_arvore(root, ajusta_labels)
    UniqueDotExporter(root).to_picture(f"{sys.argv[1]}.cut.unique.ast.png")
    print(f"Poda da árvore gerada\nArquivo de destino: {sys.argv[1]}.cut.unique.ast.png")

def main():
    global root, function_list, var_list, message_list

    root, function_list, var_list, message_list = tppparser.main()

    
    verifica_escopo(var_list, function_list)

    tabela_funcoes, tabela_variaveis = gera_tabelas(function_list, var_list)
    
    checa_semantica(function_list, var_list, message_list, tabela_funcoes, tabela_variaveis, root)

    erros = 0
    message_list = corrige_tupla(message_list)
    for mensagem in message_list:
        print(mensagem[-1])
        if mensagem[0] == 'ERROR':
            erros += 1

    arruma_arvore(root)


if __name__ == '__main__':
    main()