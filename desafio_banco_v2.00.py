from datetime import datetime


def mostra_menu(menu):

    menu = """
    MENU    

    [1] Criar Usuário
    [2] Criar Conta
    [3] Depósito
    [4] Saque
    [5] Extrato
    [6] Listar Usuários
    [7] Listar Contas
    [8] Sair


Qual opção desejada?: """

    return menu


def data_hora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def criar_usuario(usuarios):
    cpf = input("\nInforme o CPF do usuário: ")
    usuario = filtrar_usuario(usuarios, cpf)

    
    if usuario:
        print("\nUsuario ja registrado com esse CPF.")
        return
    
    nome = input("\nInforme o nome do usuário: ")
    nascimento = input("\nInforme a data de nascimento do usuário (dd-mm-aaaa): ")
    endereco = input("\nInforme o seu endereco(logradouro, nro-bairro-cidade/sigla): ")   

    usuarios.append({
        "nome": nome,
        "nascimento": nascimento,
        "cpf": cpf,
        "endereco": endereco
        })
    
    
    
    print("\nUsuario cadastrado com sucesso!")


def criar_conta(usuarios, conta, AGENCIA):
    cpf = input("\nInforme o CPF do usuário: ")
    usuario = filtrar_usuario(usuarios, cpf)
    
    if not usuario:
        print("\nUsuario nao encontrado. Registre-se antes de criar uma conta.")
        return
    
    numero_conta = len(conta) + 1
    conta.append({
        "nome": usuario["nome"],
        "numero": numero_conta,
        "agencia": AGENCIA,
        "cpf": usuario["cpf"],
        "saldo": 0,
        "extrato": [],
        "limite_saque": 500,
        "numero_saques": 0
    })
    print(f"\nConta criada com sucesso! Numero da conta: {numero_conta} - Agencia: {AGENCIA}.")   


def filtrar_usuario(usuarios, cpf):
    filtro_usuario = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return filtro_usuario[0] if filtro_usuario else None


def filtrar_conta(conta, numero, agencia):
    #print(f"DEBUG: conta = {conta}, tipo = {type(conta)}")
    filtro_conta = [c for c in conta if c["numero"] == numero and c["agencia"] == agencia]
    return filtro_conta[0] if filtro_conta else None


def buscar_conta(conta):
    numero = int(input("\nInforme o número da conta: "))
    agencia = input("\nInforme a agência da conta: ")
    contas = filtrar_conta(conta, numero, agencia)

    if not contas:
        print("\nConta não encontrada. Verifique o número e a agência informados.")
        return
    
    return contas


def deposito(conta, /):
 
    contas = buscar_conta(conta)
    valor = float(input("\nInforme o valor do depósito: R$ " ))

    if valor <= 0:
        print("\nNão é possível efetuar depósitos menores que zero ou negativos.")
    else:
        contas["saldo"] += valor  
        contas["extrato"].append(f"Depositado R$ {valor:.2f} - {data_hora()}") 
        print("\nDepósito efetuado com sucesso!")

    return conta


def saque(*, limite_saques, conta):
    
    contas = buscar_conta(conta)
    valor = float(input("\nInforme o valor que deseja sacar: R$ "))
    
    sem_saldo = contas["saldo"] < valor
    limite_excedido = valor > contas["limite_saque"]
    execeu_saque = contas["numero_saques"] == limite_saques

    if sem_saldo: 
        print("\nOperação falhou! Saldo insuficiente!")
    elif limite_excedido: 
        print("\nOperação falhou! Voce excedeu o valor de limite para saque.")
    elif execeu_saque: 
        print("\nOperação falhou! Voce excedeu a quantidade de limite para saque.")
    elif valor > 0:
        #print(f"DEBUG: conta = {conta}, tipo = {type(conta)}") 
        
        contas["numero_saques"] += 1               
        contas["saldo"] -= valor  
        contas["extrato"].append(f"Saque realizado R$ {valor:.2f} - {data_hora()}")
        #print(f"DEBUG: conta = {conta}, tipo = {type(conta)}") 
        print("\nSaque autorizado.")
    else:
        print("\nOperação falhou! Valor inválido para saque.")

    return conta


def exibir_extrato(conta, /, *, title_extrato):

    #print(f"DEBUG: conta = {conta}, tipo = {type(conta)}")
    contas = buscar_conta(conta)
    print(f"\n{title_extrato.center(58, '=')}")
    print(f"\nConta: {contas['numero']} - Agencia: {contas['agencia']}")

    if not contas["extrato"]:  
        print("Não foram realizadas movimentações.")
    else:   
        for transaction in contas["extrato"]:    
            print(f"\n{transaction}")  
        
    print(f"\nSaldo R$ {contas['saldo']:.2f}")  
    print("==========================================================")


def exibir_usuarios(usuarios, title_listar_usuarios):
    if not usuarios:
        print("\nNenhum usuario cadastrado.")
    else:
        print(f"\n{title_listar_usuarios.center(58, '=')}")
        for usuario in usuarios:
            print(f"\nNome: {usuario['nome']} - " 
                  f"Data nascimento: {usuario['nascimento']} - " 
                  f"CPF: {usuario['cpf']} - "
                  f"Endereco: {usuario['endereco']}"
                )
        print("==========================================================")


def exibir_contas(conta, title_listar_contas):
    if not conta:
        print("\nNenhuma conta cadastrada!.")
    else:
        print(f"\n{title_listar_contas.center(58, '=')}")
        for c in conta:
            print(
                f"\nNome: {c['nome']}"
                f"\nNumero da conta: {c['numero']} - " 
                f"Agencia: {c['agencia']} - " 
                f"CPF: {c['cpf']} - "
                f"Saldo R$: {c['saldo']}"
                )
        print("==========================================================")


def main():
    LIMITE_SAQUES = 3  
    AGENCIA = "0001" 

     
    #limite = 500  
    #numero_saques = 0  
    title_extrato = "Extrato de transações:"
    title_listar_contas = "Listagem de contas:"
    title_listar_usuarios = "Listagem de usuários:"  
    usuarios = []
    conta = []

    while True:
        opcao = int(input((mostra_menu(menu=None)))) 

        if opcao == 3:   
            
            conta = deposito(conta)          


        elif opcao == 1:
            
            criar_usuario(usuarios)


        elif opcao == 2:
            criar_conta(usuarios, conta, AGENCIA)


        elif opcao == 4:
            
            conta = saque(
                 
                limite_saques=LIMITE_SAQUES, 
                conta=conta
            )
            
        elif opcao == 5:
            exibir_extrato(conta, title_extrato=title_extrato)


        elif opcao == 6:
            exibir_usuarios(usuarios, title_listar_usuarios)


        elif opcao == 7:
            exibir_contas(conta, title_listar_contas)


        elif opcao == 8:
            print("\nSaindo do sistema...")
            break  
        
        
        else:
            print("Opção inválida, por favor selecione novamente a operação desejada.")


if __name__ == "__main__":
    main()