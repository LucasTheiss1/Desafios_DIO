import textwrap
from abc import ABC, abstractclassmethod, abstractmethod
from datetime import datetime

class Conta:
    def __init__(self, numero, cliente):
        self.__saldo = 0
        self.__numero = numero
        self.__agencia = "0001"
        self.__cliente = cliente
        self.__historico = Historico()
    
    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)
    

    @property
    def saldo(self):
        return self.__saldo

    @property
    def numero(self):
        return self.__numero
    
    @property
    def agencia(self):
        return self.__agencia
    
    @property
    def cliente(self):
        return self.__cliente
    
    @property
    def historico(self):
        return self.__historico
    
    def depositar(self, valor, origem="Depósito"):
        if valor > 0:
            self.__saldo += valor
            print(f"\n=== {origem} realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        
        return False

    def sacar(self, valor, origem="Saque"):
        saldo = self.saldo
        execedeu_limite = valor > saldo

        if execedeu_limite:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
        elif valor > 0:
            self.__saldo -= valor
            print(f"\n=== {origem} realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        
        return False        
    
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saque=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saque = limite_saque 
    
    def sacar(self, valor, origem="Saque"):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        execedeu_limite = valor > self.limite
        execedeu_saque = numero_saques >= self.limite_saque
        
        if execedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        
        elif execedeu_saque:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        
        else:
            return super().sacar(valor, origem=origem)
        
        return False


    def __str__(self):
        return f"""\
        Agência:\t{self.agencia}
        C/C:\t\t{self.numero}
        Titular:\t{self.cliente.nome}
        """
    
    def ajustar_limite(self, novo_limite):
        if novo_limite > 0:
            self.limite = novo_limite
            print(f"\n=== Limite ajustado para R$ {self.limite:.2f} ===")
        else:
            print("\n@@@ Operação falhou! O limite deve ser maior que zero. @@@")
    
    def ajustar_limite_saque(self, novo_limite_saque):
        if novo_limite_saque > 0:
            self.limite_saque = novo_limite_saque
            print(f"\n=== Limite de saques ajustado para {self.limite_saque} ===")
        else:
            print("\n@@@ Operação falhou! O limite de saques deve ser maior que zero. @@@")
            
class Historico:
    def __init__(self):
        self.__transacoes = []
    
    @property
    def transacoes(self):
        return self.__transacoes

    def adicionar_transacao(self, transacao):
        self.__transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })

    def extrato(self):
        pass

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractclassmethod
    def registrar(self, conta):
        pass
 
class Deposito(Transacao):
    def __init__(self, valor):
        self.__valor = valor
        
    @property
    def valor(self):
        return self.__valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self.__valor = valor
        
    @property
    def valor(self):
        return self.__valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Transferencia(Transacao):
    def __init__(self, valor, conta_destino):
        self.__origem = "Transferência"
        self.__valor = valor
        self.__conta_destino = conta_destino
        
    @property
    def valor(self):
        return self.__valor
    
    @property
    def conta_destino(self):
        return self.__conta_destino

    @property
    def origem(self):
        return self.__origem

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor, origem=self.origem)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            self.__conta_destino.depositar(self.valor, origem=self.origem)
            self.__conta_destino.historico.adicionar_transacao(self)
       
class Cliente:
    def __init__ (self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        pass

def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [aj]\tAjustar limite
    [l]\tListar clientes
    [r]\tRemover cliente
    [ac]\tAcessar conta
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

def depositar(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)
    
    if not cliente:
        print("\n@@@ Usuário não encontrado! @@@")
        return
    valor = float(input("Informe o valor do depósito: R$ "))

    transacao = Deposito(valor)
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        print("\n@@@ Usuário não possui conta! @@@")
        return
    
    cliente.realizar_transacao(conta, transacao)
    
def sacar(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Usuário não encontrado! @@@")
        return
    
    valor = float(input("Informe o valor do saque: R$ "))

    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        print("\n@@@ Usuário não possui conta! @@@")
        return
    
    cliente.realizar_transacao(conta, transacao)
    
def listar_conta(contas):
    for conta in contas:
        print("=" * 48)
        print(textwrap.dedent(str(conta)))

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Usuário não possui conta! @@@")
        return None
     
    if len(cliente.contas) == 1:
        return cliente.contas[0]
    
    print("\n=== Contas disponiveis: ===")
    for i, conta in enumerate(cliente.contas, 1):
        print(f"{i} - Conta: {conta.numero} | Tipo: {type(conta).__name__}")
    
    try:
        escolha = int(input("Escolha a conta desejada: "))
        if 1 <= escolha <= len(cliente.contas):
            return cliente.contas[escolha - 1]
        else:
            print("\n@@@ Opção inválida! @@@")
            return None
    except ValueError:
        print("\n@@@ Opção inválida! @@@")
        return None
    
def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None
        
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    

    print("\n=== Conta criada com sucesso! ===")
    print(f"Agência: {conta.agencia} - Conta: {conta.numero}, Cliente: {conta.cliente.nome}")

def exibir_extrato_conta(conta):
    print("=" * 48)
    print(f"=== Extrato da conta {conta.numero} ===")
    print("=" * 48)
    
    transacoes = conta.historico.transacoes
    extrato = ""

    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n{transacao['data']}\n\tR$ {transacao['valor']:.2f}"
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("=" * 48)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Usuário não encontrado! @@@")
        return
    
    conta = recuperar_conta_cliente(cliente)
    
    if not conta:
        print("\n@@@ Usuário não possui conta! @@@")
        return
    
    print("=" * 48)
    print(f"=== Extrato da conta {conta.numero} ===")
    print("=" * 48)

    exibir_extrato_conta(conta)

    #transacoes = conta.historico.transacoes
    #extrato = ""

    #if not transacoes:
    #    extrato = "Não foram realizadas movimentações."
    #else:
    #    for transacao in transacoes:
    #        extrato += f"\n{transacao['tipo']}:\n{transacao['data']}\n\tR$ {transacao['valor']:.2f}"
                
    #print(extrato)
    #print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    #print("=" * 48)

def criar_cliente(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = cliente_existe(cpf, clientes)
    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return
    
    nome = input("Informe o nome do cliente: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    
    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)
    print("\n=== Usuário criado com sucesso! ===")

def obter_cliente_cpf(cpf, clientes):
    cliente = filtrar_cliente(cpf, clientes)
    
    if cliente:
        return cliente
    else:
        print("\n@@@ Usuário não encontrado! @@@")
        return None
    
def cliente_existe(cpf, clientes):
    return filtrar_cliente(cpf, clientes) is not None

def ajustar_limites_conta_corrente(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Usuário não encontrado! @@@")
        return
    
    conta = recuperar_conta_cliente(cliente)
    
    if not conta:
        print("\n@@@ Usuário não possui conta! @@@")
        return
    
    novo_limite = float(input("Informe o novo limite: R$ "))
    conta.ajustar_limite(novo_limite)
    
    novo_limite_saque = int(input("Informe o novo limite de saques: "))
    conta.ajustar_limite_saque(novo_limite_saque)

def listar_clientes(clientes):
    if not clientes:
        print("\n@@@ Não existem clientes cadastrados! @@@")
        return
    
    print("\n=== Clientes cadastrados: ===")
    for cliente in clientes:
        print(f"Nome: {cliente.nome} - CPF: {cliente.cpf} - Endereço: {cliente.endereco}")
    
    print("=" * 48)

def remover_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = obter_cliente_cpf(cpf, clientes)

    if not cliente:
        return cliente
    else:
        answer = input(f"Tem certeza que deseja remover o cliente {cliente.nome} (s/n)? ").lower()
        if answer != "s":
            print("\n@@@ Remoção cancelada! @@@")
            return
    clientes.remove(cliente)
    print(f"\n@@@ Cliente: {cliente.nome} removido com sucesso! @@@")

def transferir(conta_origem, cliente_origem, clientes):
   
    print("Destino:")
    cliente_destino = obter_cliente_cpf(input("Informe o CPF do conta de destino: "), clientes)
    
    if not cliente_destino:
        return cliente_destino
    
    conta_destino = recuperar_conta_cliente(cliente_destino)
    if not conta_destino:
        print("\n@@@ Usuário não possui conta! @@@")
        return
    
    try:
        valor = float(input("Informe o valor da transferência: R$ "))
        if valor <= 0:
            print("\n@@@ Valor deve ser maior que zero! @@@")
            return
        
        transferencia = Transferencia(valor, conta_destino)
        cliente_origem.realizar_transacao(conta_origem, transferencia)
        
    except ValueError:
        print("\n@@@ Valor inválido! @@@")
        
def acessar_conta(clientes):
    cliente = obter_cliente_cpf(input("Informe o CPF do cliente: "), clientes)
    if not cliente:
        return cliente
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        print("\n@@@ Usuário não possui conta! @@@")
        return
    
    while True:
        print("\n=== Acesso à conta ===")
        print("[1] - Depositar")
        print("[2] - Sacar")
        print("[3] - Extrato")
        print("[4] - Transferencia")
        print("[5] - Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            valor = float(input("Informe o valor do depósito: R$ "))
            transacao = Deposito(valor)
            cliente.realizar_transacao(conta, transacao)
        
        elif opcao == "2":
            valor = float(input("Informe o valor do saque: R$ "))
            transacao = Saque(valor)
            cliente.realizar_transacao(conta, transacao)
        
        elif opcao == "3":
            exibir_extrato_conta(conta)
        
        elif opcao == "4":
            transferir(conta, cliente, clientes)
        
        elif opcao == "5":
            print("\n=== Saindo da conta... ===")
            break
        
def main():
    clientes = []
    contas = []
    
    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)


        elif opcao == "s":
            sacar(clientes)


        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_conta(contas)

        elif opcao == "aj":
            ajustar_limites_conta_corrente(clientes)

        elif opcao == "l":
            listar_clientes(clientes)
        
        elif opcao == "r":
            remover_cliente(clientes)

        elif opcao == "ac":
            acessar_conta(clientes)

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")

main()

