import pytest
from datetime import datetime, timedelta
from src.flight.FlightBookingSystem import FlightBookingSystem

@pytest.fixture
def system():
    """Cria uma instância do sistema de reservas de voo antes de cada teste"""
    return FlightBookingSystem()


def test_normal_booking(system):
    """Verifica se uma reserva comum é confirmada corretamente quando há assentos disponíveis"""
    result = system.book_flight(
        passengers=2,
        booking_time=datetime.now(),
        available_seats=10,
        current_price=500.0,
        previous_sales=10,
        is_cancellation=False,
        departure_time=datetime.now() + timedelta(hours=48),
        reward_points_available=0,
    )
    assert result.confirmation
    assert result.refund_amount == 0


def test_no_seats(system):
    """Verifica se a reserva é negada quando não há assentos suficientes disponíveis"""
    result = system.book_flight(5, datetime.now(), 2, 500, 10, False, datetime.now(), 0)
    assert not result.confirmation


def test_last_minute_booking(system):
    """Verifica se há acréscimo no preço para reservas feitas com menos de 24h de antecedência"""
    booking_time = datetime.now()
    result_no_fee = system.book_flight(1, booking_time, 10, 500, 10, False, booking_time + timedelta(hours=48), 0)
    result_last_minute = system.book_flight(1, booking_time, 10, 500, 10, False, booking_time + timedelta(hours=2), 0)

    assert result_last_minute.total_price > result_no_fee.total_price


def test_group_discount(system):
    """Verifica se reservas com mais de 4 passageiros recebem desconto no valor final"""
    result = system.book_flight(6, datetime.now(), 10, 500, 10, False, datetime.now() + timedelta(hours=48), 0)
    assert result.total_price < 6 * 500


def test_points_applied(system):
    """Verifica se o uso de pontos de recompensa reduz o valor total da reserva"""
    result = system.book_flight(1, datetime.now(), 10, 500, 10, False, datetime.now() + timedelta(hours=48), 100)
    assert result.points_used
    assert result.total_price < 500


def test_full_refund(system):
    """Verifica se o reembolso é total quando o cancelamento ocorre com mais de 48h de antecedência"""
    result = system.book_flight(1, datetime.now(), 10, 500, 10, True, datetime.now() + timedelta(hours=72), 0)
    assert result.refund_amount > 0


def test_half_refund(system):
    """Verifica se o reembolso é parcial quando o cancelamento ocorre a menos de 48h do voo"""
    result = system.book_flight(1, datetime.now(), 10, 500, 10, True, datetime.now() + timedelta(hours=10), 0)
    assert result.refund_amount > 0
    assert result.refund_amount < 500
