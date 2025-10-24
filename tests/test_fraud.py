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
    assert result.is_fraudulent is False
    assert result.is_blocked is False
    assert result.verification_required is False 
    assert result.risk_score == 0


def test_amount_equal_to_limit_not_fraudulent(system):
    """Verifica se transações com valor exatamente 10000 NÃO são marcadas como fraude."""
    tx = Transaction(10000, datetime.now(), "BR")
    result = system.check_for_fraud(tx, [], [])
    assert result.is_fraudulent is False
    assert result.verification_required is False
    assert result.risk_score == 0


def test_high_value_transaction(system):
    """Verifica se uma transação de valor muito alto é identificada como potencial fraude"""
    tx = Transaction(10001, datetime.now(), "BR") 
    result = system.check_for_fraud(tx, [], [])
    assert result.is_fraudulent is True
    assert result.verification_required is True
    assert result.risk_score == 50 


def test_frequent_transactions(system):
    """Verifica se várias transações em curto período de tempo (11 transações) ativam o bloqueio"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*5), "BR") for i in range(11)]
    tx = Transaction(100, now, "BR")
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_blocked is True
    assert result.risk_score == 30 


def test_location_change_active(system):
    """Verifica se a Regra 3 é ativada quando a mudança de localização ocorre em menos de 30 minutos"""
    now = datetime.now()
    last = [Transaction(100, now - timedelta(minutes=10), "US")]
    tx = Transaction(100, now, "BR")
    result = system.check_for_fraud(tx, last, [])
    assert result.is_fraudulent is True
    assert result.verification_required is True
    assert result.risk_score == 20


def test_location_change_boundary(system):
    """Verifica se a Regra 3 NÃO é ativada quando a transação anterior foi a EXATOS 30 minutos (limite)"""
    now = datetime.now()
    last = [Transaction(100, now - timedelta(minutes=30), "US")]
    tx = Transaction(100, now, "BR")
    result = system.check_for_fraud(tx, last, [])
    assert result.is_fraudulent is False
    assert result.risk_score == 0


def test_high_value_and_location_change(system):
    """Verifica se a soma de riscos é acumulativa quando duas regras disparam."""
    now = datetime.now()
    last = [Transaction(20000, now - timedelta(minutes=10), "US")]
    tx = Transaction(20000, now, "BR")
    result = system.check_for_fraud(tx, last, [])
    assert result.is_fraudulent is True
    assert result.verification_required is True
    assert result.risk_score == 70


def test_frequent_transactions_and_high_value(system):
    """Verifica se o risco é acumulado quando duas regras disparam simultaneamente."""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*5), "BR") for i in range(11)]
    tx = Transaction(20000, now, "BR")
    result = system.check_for_fraud(tx, prev, [])
    assert result.risk_score == 80


def test_blacklisted_location(system):
    """Verifica se uma transação feita em local que está na lista negra é bloqueada automaticamente"""
    tx = Transaction(100, datetime.now(), "US")
    result = system.check_for_fraud(tx, [], ["US"])
    assert result.is_blocked is True
    assert result.risk_score == 100


def test_transactions_exactly_60_minutes_are_counted(system):
    """Verifica se transações com exatamente 60 minutos ainda contam para a regra de frequência."""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*6), "BR") for i in range(10)]
    prev.append(Transaction(100, now - timedelta(minutes=60), "BR"))
    tx = Transaction(100, now, "BR")
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_blocked is True
    assert result.risk_score == 30


def test_frequent_transactions_limit_case(system):
    """
    Verifica o caso limite de 60 minutos e a contagem. 
    """
    now = datetime.now() 
    prev_safe = [Transaction(100, now - timedelta(minutes=59), "BR") for _ in range(10)]
    tx_limit_out = Transaction(100, now - timedelta(minutes=60, seconds=1), "BR")
    prev_all = prev_safe + [tx_limit_out]
    tx_current = Transaction(100, now, "BR")
    result = system.check_for_fraud(tx_current, prev_all, []) 
    
    assert result.is_blocked is False
    assert result.risk_score == 0