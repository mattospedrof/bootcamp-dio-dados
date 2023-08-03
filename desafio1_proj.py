import time

menu_1 = """
[A] Já sou cliente
[B] Quero criar minha conta
[C] Sair do sistema
=> """

menu_2 = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldo = 0
limite_max = 500
saques_realizados = 0
limite_saques = 3
numero_operacao = 0

extrato = []
info_usuario = {}
info_contas = {}


def novo_cliente():
    usuario_criar_conta = input("Digite o nome de usuário que deseja: ")
    nome = input("Digite seu nome completo: ")
    data_nascimento = input("Digite sua data de nascimento no formato dd/mm/aaaa: ")
    cpf = input("Digite o número do seu CPF: ")
    cpf = ''.join(filter(str.isdigit, cpf))
    logradouro = input("Informe o logradouro: ")
    numero = input("Número: ")
    bairro = input("Bairro: ")
    cidade = input("Cidade: ")
    estado = input("Sigla do estado: ")
    endereco = f"{logradouro}, {numero} - {bairro} - {cidade}/{estado}"

    if cpf in info_usuario:
        print("Esse número de CPF já está atribuído a outro usuário.")
    else:
        info_usuario[usuario_criar_conta] = { 
            "usuario": usuario_criar_conta,
            "nome": nome,
            "data_nascimento": data_nascimento,
            "endereco": endereco
        }
    
    return usuario_criar_conta

def conta_corrente(usuario):
    agencia = "0001"
    usuario_info = info_usuario.get(usuario)

    if usuario_info is None:
        print("Usuário não encontrado. Crie um novo cliente antes de abrir a conta.")
    else:
        numero_conta = len(info_contas) + 1
        info_contas[numero_conta] = {
            "agencia": agencia,
            "numero_conta": numero_conta,
            "usuario": usuario
        }

        print(f"Parabéns, você possui uma nova conta em nosso banco.\n"
            f"Seu usuário é: {usuario_info['usuario']}\n"
            f"Sua conta é: {numero_conta}\n"
            f"Agência: {agencia}"
        )

def deposito(saldo, numero_operacao, extrato):
    deposito = float(input("Digite o valor que deseja depositar: "))

    saldo += deposito
    numero_operacao += 1
    extrato.append({'Operação': numero_operacao, 'Depósito': deposito})
    print(f"\nDepósito de R${deposito:.2f} realizado com sucesso.")
    
    return saldo, numero_operacao, extrato

def saque(saldo, saques_realizados, limite_max, numero_operacao, extrato):
    if saques_realizados > 3:
        print("\nVocê atingiu o limite diário de 3 saques.")
    else:
        saque = float(input("Digite o valor que deseja sacar: "))
        if saque > saldo:
            print("Você não possui saldo suficiente.\n"
                  f"Seu saldo é de R${saldo:.2f}"
                 )
        elif saque > limite_max:
            print(f"O valor máximo para um saque é de R${limite_max:.2f}")
        else:
            saldo -= saque
            numero_operacao += 1
            saques_realizados += 1
            extrato.append({'Operação': numero_operacao, 'Saque': saque})
            print(f"\nSaque de R${saque:.2f} realizado com sucesso.")

    return saldo, saques_realizados, extrato

def criar_extrato(extrato):
    if len(extrato) == 0:
        print("Não foram realizadas movimentações.\n")
    else:
        print(formatar_extrato(extrato))
                
def formatar_extrato(dados_extrato):
    extrato_formatado = "Extrato Bancário:\n"
    for transacao in dados_extrato:
        tipo_operacao = "Depósito" if transacao.get('Depósito') else "Saque"
        valor_transacao = transacao.get('Depósito') if transacao.get('Depósito') else -transacao.get('Saque')
        extrato_formatado += f"Operação {transacao['Operação']} - {tipo_operacao} - R${abs(valor_transacao):.2f}\n"
    extrato_formatado += f"\nSaldo: R${saldo}"
    return extrato_formatado
    
while True:
    opcao = input(menu_1)
    if opcao == "A":
        while True:    
            opcao_menu_2 = input(menu_2)
            if opcao_menu_2 == "d":
                saldo, numero_operacao, extrato = deposito(saldo, numero_operacao, extrato)
            elif opcao_menu_2 == "s":
                saldo, saques_realizados, extrato = saque(saldo, saques_realizados, limite_max, numero_operacao, extrato)
            elif opcao_menu_2 == "e":
                criar_extrato(extrato)
            elif opcao_menu_2 == "q":
                print("Voltando para o menu principal...")
                time.sleep(2)
                break
            else:
                print("Opção inválida, insira um caractere válido.")
    elif opcao == "B":
        usuario_criar_conta = novo_cliente()
        conta_corrente(usuario_criar_conta)
    elif opcao == "C":
        break
    else:
        print("Opção inválida, insira um caractere válido.")