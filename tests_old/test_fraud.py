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
    assert not result.is_fraudulent
    assert not result.is_blocked
    assert result.risk_score == 0


def test_high_value_transaction(system):
    """Verifica se uma transação de valor muito alto é identificada como potencial fraude"""
    tx = Transaction(15000, datetime.now(), "BR")
    result = system.check_for_fraud(tx, [], [])
    assert result.is_fraudulent
    assert result.verification_required
    assert result.risk_score >= 50


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
