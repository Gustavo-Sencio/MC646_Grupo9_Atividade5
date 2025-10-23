import pytest 
from datetime import datetime, timedelta
from src.fraud.Transaction import Transaction
from src.fraud.FraudDetectionSystem import FraudDetectionSystem

@pytest.fixture
def system():
    """Cria uma instância do sistema de detecção de fraudes antes de cada teste"""
    return FraudDetectionSystem()


def test_normal_transaction(system):
    """Verifica se uma transação comum, de valor baixo e local válido, não é marcada como fraude"""
    tx = Transaction(500, datetime.now(), "BR")
    result = system.check_for_fraud(tx, [], ["US"])

    assert result.is_fraudulent is False  # Mutante 65
    assert result.is_blocked is False      # Mutante 67
    assert result.risk_score == 0


def test_high_value_transaction(system):
    """Verifica se uma transação de valor muito alto é identificada como potencial fraude"""
    tx = Transaction(10001, datetime.now(), "BR") # Mutante 73
    result = system.check_for_fraud(tx, [], [])

    assert result.is_fraudulent
    assert result.verification_required
    assert result.risk_score == 50 #Mutante 80


def test_frequent_transactions(system):
    """Verifica se várias transações em curto período de tempo fazem o sistema bloquear a conta"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*5), "BR") for i in range(11)]
    tx = Transaction(100, now, "BR")
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_blocked
    assert result.risk_score >= 30


def test_location_change(system):
    """Verifica se mudanças rápidas de localização entre transações geram alerta de fraude"""
    now = datetime.now()
    last = [Transaction(100, now - timedelta(minutes=10), "US")]
    tx = Transaction(100, now, "BR")
    result = system.check_for_fraud(tx, last, [])
    assert result.is_fraudulent
    assert result.verification_required
    assert result.risk_score >= 20


def test_blacklisted_location(system):
    """Verifica se uma transação feita em local que está na lista negra é bloqueada automaticamente"""
    tx = Transaction(100, datetime.now(), "US")
    result = system.check_for_fraud(tx, [], ["US"])
    assert result.is_blocked
    assert result.risk_score == 100

def test_frequent_transactions_limit_case(system):
    """
    NOVO TESTE: Verifica o caso limite de 60 minutos e a contagem. 
    Mata Mutantes 86, 88, 89 (Boundary) e 92 (Contagem).
    """
    now = datetime.now()
    
    # 10 transações passadas a 59 minutos (para que a contagem seja EXATAMENTE 10)
    prev_safe = [Transaction(100, now - timedelta(minutes=59), "BR") for _ in range(10)]
    
    # Transação LIMITE: Exatamente 60 minutos e 1 segundo atrás (DEVE ser ignorada pelo código original)
    tx_limit_out = Transaction(100, now - timedelta(minutes=60, seconds=1), "BR")
    
    prev_all = prev_safe + [tx_limit_out] # Total de 11 transações passadas
    tx_current = Transaction(100, now, "BR")
    
    # CÓDIGO ORIGINAL: A contagem deve ser 10 (a tx_limit_out é excluída por ser > 60 min).
    # Como a regra é ativada se CONTADOR > 10, o bloqueio NÃO DEVE ocorrer.
    result = system.check_for_fraud(tx_current, prev_all, [])
    
    # O teste deve garantir que o bloqueio NÃO ocorreu.
    # Mutantes 88 e 89: Falham, pois contam a tx_limit_out, fazendo a contagem ser 11, o que ATIVA o bloqueio.
    assert result.is_blocked is False 
    
    # Mutantes 86 e 92 (Contagem e Score): Como o bloqueio não ocorreu, o risk_score por frequência não é adicionado.
    # O assert deve garantir que o score é 0.
    assert result.risk_score == 0