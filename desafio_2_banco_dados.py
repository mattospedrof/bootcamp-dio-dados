import pymysql
import pymysql.cursors
import random
import hashlib
import getpass
import time
import os
import dotenv
from datetime import datetime
from decimal import Decimal

TABLE_NAME = 'users'
TABLE_NAME_2 = 'info_conta'
AGENCIA = '0007'

menu_geral = """
### MATTOS FINANCEIRA ###

[A] Criar conta
[B] Já sou cliente
[C] Sair do sistema

=> """

menu_interno_login = """
[1] Fazer login
[2] Voltar

=> """
                    
dotenv.load_dotenv()

connection = pymysql.connect(
    host = os.environ['MYSQL_HOST'],
    user = os.environ['MYSQL_USER'],
    password = os.environ['MYSQL_PASSWORD'],
    database = os.environ['MYSQL_DATABASE'],
    cursorclass = pymysql.cursors.DictCursor,
)

def verifica_nome_usuario(connection, nome_usuario):
    while True:
        if not nome_usuario:
            print("Digite um nome de usuário válido!")
            continue
        
        query = "SELECT COUNT(*) FROM users WHERE usuario = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (nome_usuario,))
            result = cursor.fetchone()
        
        if result['COUNT(*)'] > 0:
            print("Nome de usuário já existe.")
        else:
            return nome_usuario

def gerar_numero_conta(cursor):
    with connection.cursor() as cursor:
        while True:    
            digitos = [random.randint(0, 9) for _ in range(9)]
            
            multiplicacao = 1
            soma = 0
            
            for digito in digitos:
                multiplicacao *= digito
                soma += digito
            
            digito_verificador = 2 if soma % 2 == 0 else 7
            numero_conta = "".join(map(str, digitos)) + str(digito_verificador)
            
            query_conta = "SELECT COUNT(*) FROM info_conta WHERE conta = %s"
            
            cursor.execute(query_conta, (numero_conta,))
            result = cursor.fetchone()
                
            if result['COUNT(*)'] == 0:
                return numero_conta

def verifica_senha(cursor, nome_usuario, senha):
    query_verifica_senha = "SELECT senha FROM users WHERE usuario = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(query_verifica_senha, (nome_usuario,))
        result = cursor.fetchone()
    
    if result:
        stored_password = result['senha']
        hashed_password = hashlib.sha256(senha.encode()).hexdigest()
        return hashed_password == stored_password
    else:
        return False
    
def deposito(cursor, user_id, numero_conta):
    while True:   
        deposito = input( 
            "\nDepósito limitado a R$1000,00 por vez\n"
            "Digite o valor que deseja depositar: "
        )
        deposito = Decimal(deposito)
        
        if deposito <= 0:
            print("Digite um valor válido")
        elif deposito > 1000:
            print("Digite um valor abaixo de R$1000")
        else:
            with connection.cursor() as cursor:
                query_saldo = "SELECT saldo FROM info_conta WHERE user_id = %s ORDER BY data DESC LIMIT 1"
                cursor.execute(query_saldo, (user_id,))
                result = cursor.fetchone()
                saldo_atual = result['saldo']
                saldo_atual = Decimal(saldo_atual)

                mov = 'Depósito'
                saldo_momento = saldo_atual + deposito        
                query_movimentacao = (
                    "INSERT INTO info_conta (user_id, agencia, conta, data, movimentacao, valor, saldo) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                )
                values_movimentacao = (
                    user_id, AGENCIA, numero_conta, datetime.now(), mov, deposito, saldo_momento
                )
                cursor.execute(query_movimentacao, values_movimentacao)
                
                last_insert_id = cursor.lastrowid
                
                connection.commit()
                
                print(f"\nDepósito de R${deposito:.2f} realizado com sucesso.")
                
            with connection.cursor() as cursor:
                query_atualiza_saldo = "UPDATE info_conta SET saldo = %s WHERE id = %s"
                cursor.execute(query_atualiza_saldo, (saldo_momento, last_insert_id))
                connection.commit()
                
                break

def saque(cursor, user_id, numero_conta):
    with connection.cursor() as cursor:
        query_saldo = "SELECT saldo FROM info_conta WHERE user_id = %s ORDER BY data DESC LIMIT 1 "
        cursor.execute(query_saldo, (user_id,))
        result = cursor.fetchone()
            
        saldo_atual = result['saldo']
        saldo_atual = Decimal(saldo_atual)
        connection.commit()
        
    with connection.cursor() as cursor:    
        query_saques = "SELECT saques_mensais FROM info_conta WHERE user_id = %s "
        cursor.execute(query_saques, (user_id,))
        result_saque = cursor.fetchone()
        
        saques_mensais = result_saque['saques_mensais']
        saque_atualizado = saques_mensais + 1
        connection.commit()
            
        if saque_atualizado > 10:
            print("\nVocê atingiu o limite mensal de 10 saques.")
        else:
            while True:
                saque_valor = input(
                                    "\nLimitado a R$10000,00 por saque\n"
                                    "Digite o valor que deseja sacar: "
                                )
                saque_valor = Decimal(saque_valor)
                
                if saque_valor <= 0:
                    print("Digite um valor válido!")
                
                elif saque_valor > saldo_atual:
                    print(
                        "Você não possui saldo suficiente.\n"
                        f"Seu saldo é de R${saldo_atual:.2f}"
                    )
                
                elif saque_valor > 10000:
                    print("O valor de saque solicitado excede o limite permitido de R$10000")
                
                else:
                    saldo_momento = saldo_atual - saque_valor   
                    
                    with connection.cursor() as cursor:
                        mov = 'Saque '
                        query_movimentacao = (
                            "INSERT INTO info_conta (user_id, agencia, conta, data, movimentacao, valor, saldo, saques_mensais) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                        )
                        values_movimentacao = (
                            user_id, AGENCIA, numero_conta, datetime.now(), mov, saque_valor, saldo_momento, saque_atualizado
                        )
                        cursor.execute(query_movimentacao, values_movimentacao)

                        last_insert_id = cursor.lastrowid
                
                        connection.commit()
                
                        print(f"\nSaque de R${saque_valor:.2f} realizado com sucesso.")
                
                    with connection.cursor() as cursor:
                        query_atualiza_saldo = "UPDATE info_conta SET saldo = %s WHERE id = %s"
                        cursor.execute(query_atualiza_saldo, (saldo_momento, last_insert_id))
                        connection.commit()
                        
                    with connection.cursor() as cursor:
                        query_atualiza_saque = "UPDATE info_conta SET saques_mensais = %s WHERE user_id = %s"
                        cursor.execute(query_atualiza_saque, (saque_atualizado, user_id))
                        connection.commit()
                        break

def extrato(cursor, user_id, nome_usuario):
    with connection.cursor() as cursor:
        opcao_extrato = input("\nDeseja ver o extrato de Dia (D) ou Período (P)? ").lower()[:1]

        if opcao_extrato == 'd':
            data_consulta = input("\nDigite a data no formato DD-MM-AAAA: ")[:10]
            data_formatada = data_consulta
            nome_arquivo_diario = f'extrato_{nome_usuario}_{data_consulta}.txt'
            
            try:
                data_consulta = datetime.strptime(data_consulta, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                print("Formato de data inválido. Use o formato DD-MM-AAAA.")
                return
        
            query_diario = (
                "SELECT data, movimentacao, valor, saldo "
                "FROM info_conta "
                "WHERE user_id = %s AND DATE(data) = %s "
                "ORDER BY data "
            )
            cursor.execute(query_diario, ((user_id,), data_consulta))
            extrato_data = cursor.fetchall()
            
            print("\nMovimento\t\tValor(R$)\tSaldo\t\tData e Horário\n")
            for row in extrato_data:
                print(f"{row['movimentacao']:<20}\t{row['valor']:<15}\t{row['saldo']:<15}\t{row['data']}\n")

            salvar_extrato = input("\nDeseja salvar o extrato em um arquivo? (S/N) ").lower()[:1]
            if salvar_extrato == 's':
                with open(nome_arquivo_diario, 'w') as arquivo:
                    arquivo.write(
                                "Mattos Financeira\n"
                                f"Usuário: {nome_usuario}\n"
                                f"Agência: {AGENCIA}\n"
                                f"Conta-Corrente: {numero_conta[:9]}-{numero_conta[9]}\n"
                                f"\nExtrato do dia {data_formatada}\n"
                                "\nMovimento\t\tValor(R$)\tSaldo(R$)\t\tData - Horário\n"
                            )
                    
                    for row in extrato_data:
                        arquivo.write(f"{row['movimentacao']:<20}\t{row['valor']:<15}\t{row['saldo']:<15}\t{row['data']}\n")
                
                print(f"\nExtrato salvo no arquivo {nome_arquivo_diario}")
            
        elif opcao_extrato == 'p':
            data_inicio = input("Digite a data de início no formato DD-MM-AAAA: ")[:10]
            data_ini_format = data_inicio
            data_fim = input("Digite a data de fim no formato DD-MM-AAAA: ")[:10]
            data_fim_format = data_fim
            nome_arquivo_periodo = f'extrato_{nome_usuario}_{data_inicio[:5]}/{data_fim[:5]}.txt'
            
            try:
                data_inicio = datetime.strptime(data_inicio, "%d-%m-%Y").strftime("%Y-%m-%d")
                data_fim = datetime.strptime(data_fim, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                print("Formato de data inválido. Use o formato DD-MM-AAAA.")
                return
            
            query_periodo = (
                "SELECT data, movimentacao, valor, saldo "
                "FROM info_conta "
                "WHERE user_id = %s AND DATE(data) BETWEEN %s AND %s "
                "ORDER BY data "
            )
            cursor.execute(query_periodo, (user_id, f"{data_inicio} 00:00:00", f"{data_fim} 23:59:59"))
            extrato_data = cursor.fetchall()
            
            for row in extrato_data:
                print(f"{row['data']} \t {row['movimentacao']} \t {row['valor']} \t {row['saldo']}")

            salvar_extrato = input("Deseja salvar o extrato em um arquivo? (S/N) ").lower()[:1]
            if salvar_extrato == 's':
                with open(nome_arquivo_diario, 'w') as arquivo:
                    arquivo.write(
                                "Mattos Financeira\n"
                                f"Usuário: {nome_usuario}\n"
                                f"Agência: {AGENCIA}\n"
                                f"Conta-Corrente: {numero_conta[:9]}-{numero_conta[9]}\n"
                                f"\nExtrato do período: {data_ini_format} a {data_fim_format}\n"
                                "\nMovimento\t\tValor(R$)\tSaldo(R$)\t\tData - Horário\n"
                            )
                    
                    for row in extrato_data:
                        arquivo.write(f"{row['movimentacao']:<20}\t{row['valor']:<15}\t{row['saldo']:<15}\t{row['data']}\n")
                print(f"Extrato salvo no arquivo {nome_arquivo_periodo}")
        else:
            print("Opção inválida.")
            return
        
        connection.commit()

def saldo(cursor, user_id):
    with connection.cursor() as cursor:
        query_saldo = "SELECT saldo FROM info_conta WHERE user_id = %s ORDER BY data DESC LIMIT 1"
        cursor.execute(query_saldo, (user_id,))
        result = cursor.fetchone()
        
        saldo_atual = result['saldo']
        print(f"\nSaldo atual: R${saldo_atual:.2f}")
        time.sleep(1)
        connection.commit()
        
def menu_interno_usuario(nome_usuario, numero_conta):
    print(
        f"\nUsuário: {nome_usuario}\n"
        f"Conta: {numero_conta[:9]}-{numero_conta[9]}\n"
                            
        "\n[d] Depositar\n"
        "[s] Sacar\n"
        "[e] Extrato\n"
        "[t] Saldo\n"
        "[q] Sair da conta" 
    )
    
with connection.cursor() as cursor:
    cursor.execute(
        f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} ('
        'id INT NOT NULL AUTO_INCREMENT, '
        'usuario VARCHAR(50) NOT NULL, '
        'senha CHAR(64) NOT NULL, '
        'PRIMARY KEY (id)'
        ') '    
    )
    cursor.execute(
        f'CREATE TABLE IF NOT EXISTS {TABLE_NAME_2} ('
        'id INT NOT NULL AUTO_INCREMENT, '
        'user_id INT NOT NULL, '
        'agencia INT(4) NOT NULL, '
        'conta VARCHAR(10) NOT NULL, '
        'data DATETIME, '
        'movimentacao VARCHAR(15), '
        'valor DECIMAL(10, 2), '
        'saldo DECIMAL (10, 2) NOT NULL DEFAULT 0, '
        'saques_mensais INT NOT NULL DEFAULT 0, '
        'PRIMARY KEY (id), '
        'FOREIGN KEY (user_id) REFERENCES users(id) '
        ') '    
    )
    connection.commit()

while True:
    opcao_entrada = input(menu_geral)[:1]
    
    if opcao_entrada.upper() == 'A':
        nome_usuario = input("Digite o nome de usuário que deseja: ")
        nome_usuario = verifica_nome_usuario(connection, nome_usuario)
        senha = getpass.getpass("Digite uma nova senha: ")
                
        hashed_senha = hashlib.sha256(senha.encode()).hexdigest()
        numero_conta = gerar_numero_conta(connection)
                
        with connection.cursor() as cursor:    
            insert_query = "INSERT INTO users (usuario, senha) VALUES (%s, %s) "
            values = (nome_usuario, hashed_senha)
            cursor.execute(insert_query, values)
            connection.commit()
        
        with connection.cursor() as cursor:
            query_user_id = "SELECT id FROM users WHERE usuario = %s "
            cursor.execute(query_user_id, (nome_usuario,))
            user_id = cursor.fetchone()['id']
            connection.commit()
            
        with connection.cursor() as cursor:
            insert_query_2 = (
                "INSERT INTO info_conta "
                "(user_id, agencia, conta) "
                "VALUES (%s, %s, %s) "
            )
            values_2 = (user_id, AGENCIA, numero_conta)
            cursor.execute(insert_query_2, values_2)
            connection.commit()    
            
            print(
                "\nParabéns por confiar em nosso trabalho!!\n"
                f"Sua agência é {AGENCIA}\n" 
                f"CC:{numero_conta}\n"
            )
    
    elif opcao_entrada.upper() == 'B':
        while True:
            with connection.cursor() as cursor:          
                opcao_interno_usuario = input(menu_interno_login)[:1]
                        
                if opcao_interno_usuario == '1':
                    nome_usuario_verificacao = input("\nDigite o nome de usuário: ")
                    senha_verificacao = getpass.getpass("Digite a senha: ")

                    if verifica_senha(cursor, nome_usuario_verificacao, senha_verificacao):
                        time.sleep(1)
                        print("\nLogin bem sucedido.")
                        time.sleep(1)
                        
                        query_user_id = "SELECT id FROM users WHERE usuario = %s "
                        cursor.execute(query_user_id, (nome_usuario_verificacao,))
                        user_id = cursor.fetchone()['id']
                        
                        query_numero_conta = "SELECT conta FROM info_conta WHERE user_id = %s "
                        cursor.execute(query_numero_conta, (user_id,))
                        numero_conta = cursor.fetchone()['conta']
                        
                        query_nome_usuario = "SELECT usuario FROM users WHERE id = %s "
                        cursor.execute(query_nome_usuario, (user_id,))
                        nome_usuario = cursor.fetchone()['usuario']
                        
                        while True:
                            time.sleep(1)
                            menu_interno_usuario(nome_usuario, numero_conta)
                            time.sleep(0.5)
                            opcao_usuario = input("\n=> ")[:1]
                            
                            if opcao_usuario.lower() == 'd':
                                deposito(cursor, user_id, numero_conta)
                                connection.commit()
                            
                            elif opcao_usuario.lower() == 's':
                                saque(cursor, user_id, numero_conta)
                                connection.commit()
                            
                            elif opcao_usuario.lower() == 'e':
                                extrato(cursor, user_id, nome_usuario)
                                
                            elif opcao_usuario.lower() == 't':
                                saldo(cursor, user_id)
                                
                            elif opcao_usuario.lower() == 'q':
                                print("Saindo da conta...")
                                time.sleep(1)
                                break
                            
                            else:
                                print("Digite uma opção válida!")
                    
                    else:
                        print("Usuário ou senha inválidos.")

                elif opcao_interno_usuario == '2':
                    break
                        
                else:
                    print("Digite uma opção válida!")
                    
    elif opcao_entrada.upper() == 'C':
        print("Volte sempre!")
        time.sleep(1)
        break
    
    else:
        print("Digite uma opção válida!")