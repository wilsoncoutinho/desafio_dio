from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao, tipo_override=None):
        tipo = tipo_override if tipo_override else transacao.__class__.__name__
        self._transacoes.append(
            {
                "tipo": tipo,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @property
    def numero(self):
        return self._numero

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > self._saldo:
            print("Operação falhou: Saldo insuficiente.")
            return False
        if valor > 0:
            self._saldo -= valor
            print(f"Saque/Débito de R$ {valor:.2f} realizado com sucesso.")
            return True
        print("Operação falhou: Valor inválido.")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"Depósito/Crédito de R$ {valor:.2f} realizado com sucesso.")
            return True
        print("Operação falhou: Valor inválido.")
        return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500.0, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([t for t in self.historico.transacoes if t["tipo"] == "Saque"])
        
        if valor > self.limite:
            print("Operação falhou: O valor excede o limite da conta.")
            return False
        if numero_saques >= self.limite_saques:
            print("Operação falhou: Número máximo de saques excedido.")
            return False
        
        return super().sacar(valor)

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        taxa = 2.00
        valor_total = self.valor + taxa
        sucesso = conta.sacar(valor_total)
        if sucesso:
            self._valor = valor_total
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)

class Transferencia(Transacao):
    def __init__(self, valor, conta_destino):
        self._valor = valor
        self._conta_destino = conta_destino

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta_origem):
        print(f"Iniciando transferência para conta {self._conta_destino.numero}...")
        sucesso_saque = conta_origem.sacar(self.valor)

        if sucesso_saque:
            self._conta_destino.depositar(self.valor)
            conta_origem.historico.adicionar_transacao(self, tipo_override="Transferência Enviada")
            self._conta_destino.historico.adicionar_transacao(self, tipo_override="Transferência Recebida")

def menu():
    menu_text = """\n
    ================ MENU ================
    [n]\tNovo Cliente
    [c]\tNova Conta
    [l]\tListar Contas
    [d]\tDepositar
    [s]\tSacar
    [t]\tTransferir
    [e]\tExtrato
    [q]\tSair
    => """
    return input(menu_text)

def buscar_conta_por_numero(numero, contas_existentes):
    for conta in contas_existentes:
        if conta.numero == numero:
            return conta
    return None

def buscar_cliente_por_cpf(cpf, clientes):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

# --- Inicialização ---
if __name__ == "__main__":
    clientes = [] # Lista para armazenar os objetos Cliente
    contas = []   # Lista para armazenar os objetos Conta
    numero_conta_sequencial = 1

    print("Bem-vindo ao Sistema Bancário!")

    while True:
        opcao = menu()

        if opcao == "n":
            cpf = input("CPF (somente números): ")
            if buscar_cliente_por_cpf(cpf, clientes):
                print("Operação falhou: Cliente já cadastrado!")
                continue
            
            nome = input("Nome completo: ")
            data_nasc = input("Data de nascimento (dd-mm-aaaa): ")
            endereco = input("Endereço: ")
            
            # Instancia e armazena o objeto
            novo_cliente = PessoaFisica(cpf, nome, data_nasc, endereco)
            clientes.append(novo_cliente) 
            print("Cliente criado com sucesso!")

        elif opcao == "c":
            cpf = input("CPF do titular: ")
            cliente = buscar_cliente_por_cpf(cpf, clientes)
            
            if not cliente:
                print("Operação falhou: Cliente não encontrado!")
                continue
                
            # Instancia e armazena o objeto
            nova_conta = ContaCorrente.nova_conta(cliente, numero_conta_sequencial)
            contas.append(nova_conta) 
            cliente.adicionar_conta(nova_conta)
            
            print(f"Conta {numero_conta_sequencial} criada com sucesso!")
            numero_conta_sequencial += 1
            
        elif opcao == "l":
            print("\n================ CONTAS ================")
            for c in contas:
                print(f"Agência: {c._agencia} | Conta: {c.numero} | Titular: {c._cliente.nome}")
            print("========================================")

        elif opcao in ["d", "s", "t", "e"]:
            if not contas:
                print("Nenhuma conta cadastrada no sistema.")
                continue
                
            try:
                num_conta = int(input("Informe o número da sua conta para a operação: "))
                conta_atual = buscar_conta_por_numero(num_conta, contas)
                
                if not conta_atual:
                    print("Conta não encontrada!")
                    continue
                    
                cliente_atual = conta_atual._cliente # Acessa o objeto Cliente através do objeto Conta

                if opcao == "d":
                    valor = float(input("Valor do depósito: "))
                    cliente_atual.realizar_transacao(conta_atual, Deposito(valor))

                elif opcao == "s":
                    valor = float(input("Valor do saque: "))
                    cliente_atual.realizar_transacao(conta_atual, Saque(valor))

                elif opcao == "t":
                    valor = float(input("Valor da transferência: "))
                    num_destino = int(input("Número da conta de destino: "))
                    
                    conta_destino = buscar_conta_por_numero(num_destino, contas)
                    if conta_destino and conta_destino != conta_atual:
                        cliente_atual.realizar_transacao(conta_atual, Transferencia(valor, conta_destino))
                    else:
                        print("Conta de destino inválida ou inexistente.")

                elif opcao == "e":
                    print("\n================ EXTRATO ================")
                    transacoes = conta_atual.historico.transacoes
                    if not transacoes:
                        print("Não foram realizadas movimentações.")
                    else:
                        for t in transacoes:
                            print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")
                    print(f"\nSaldo Atual: R$ {conta_atual.saldo:.2f}")
                    print("==========================================")

            except ValueError:
                print("Entrada inválida.")

        elif opcao == "q":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")