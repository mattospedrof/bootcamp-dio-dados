menu = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldo = 0
limite_max = 500
extrato = []
saques_realizados = 0
limite_saques = 3
numero_operacao = 0

def formatar_extrato(dados_extrato):
    extrato_formatado = "Extrato Bancário:\n"
    for transacao in dados_extrato:
        tipo_operacao = "Depósito" if transacao.get('Depósito') else "Saque"
        valor_transacao = transacao.get('Depósito') if transacao.get('Depósito') else -transacao.get('Saque')
        extrato_formatado += f"Operação {transacao['Operação']} - {tipo_operacao} - R${abs(valor_transacao):.2f}\n"
    extrato_formatado += f"\nSaldo: R${saldo}"
    return extrato_formatado

while True:
    opcao = input(menu)
    
    if opcao == "d":
        deposito = float(input("Digite o valor que deseja depositar: "))

        saldo += deposito
        numero_operacao += 1
        extrato.append({'Operação': numero_operacao, 'Depósito': deposito})
        print(f"\nDepósito de R${deposito} realizado com sucesso.")
        
    elif opcao == "s":
        
        if saques_realizados > 3:
            print("\nVocê atingiu o limite diário de 3 saques.")
        else:
            saque = float(input("Digite o valor que deseja depositar: "))    
            if saque > saldo:
                print("Você não possui saldo suficiente.\n"
                    f"Seu saldo é de R${saldo:.2f}"
                )
            elif saque > limite_max:
                print(f"O valor máximo para um saque é de R${limite_max}")
            else:
                saldo -= saque
                numero_operacao += 1
                saques_realizados += 1
                extrato.append({'Operação': numero_operacao, 'Saque': saque})
                print(f"\nSaque de R${saque:.2f} realizado com sucesso.")
        
    elif opcao == "e":
        if len(extrato) == 0:
            print("Não foram realizadas movimentações.\n")
        else:
            print(formatar_extrato(extrato))
    
    elif opcao == "q":
        print("Realizando a saída do sistema...")
        break
    
    else:
        print("Opção inválida, insira um caractere válido.")