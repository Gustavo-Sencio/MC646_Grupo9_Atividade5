import pytest
from datetime import datetime, timedelta
from src.flight.FlightBookingSystem import FlightBookingSystem
from src.flight.BookingResult import BookingResult


@pytest.fixture
def system():
   
    return FlightBookingSystem()



def test_normal_booking_precise(system):
 
    passengers = 2
    current_price = 500.0
    previous_sales = 10
   
    price_factor_calc = (previous_sales / 100.0) * 0.8 
    expected_price = (current_price * passengers) * price_factor_calc 
    
    result = system.book_flight(
        passengers=passengers, booking_time=datetime.now(), available_seats=10,
        current_price=current_price, previous_sales=previous_sales, is_cancellation=False,
        departure_time=datetime.now() + timedelta(hours=72), reward_points_available=0,
    )
    assert result.confirmation is True
    assert result.total_price == pytest.approx(expected_price) 
    assert result.refund_amount == pytest.approx(0.0)
    assert result.points_used is False

def test_no_seats_should_return_all_defaults(system):
  
    result = system.book_flight(5, datetime.now(), 2, 500.0, 10, False, datetime.now(), 0)
    
    assert result.confirmation is False
    assert result.total_price == pytest.approx(0.0)
    assert result.refund_amount == pytest.approx(0.0)
    assert result.points_used is False

def test_last_minute_booking_fee_is_exact(system):
 
    booking_time = datetime.now()
    passengers = 1
    current_price = 500.0
    previous_sales = 10
    
    price_factor_calc = (previous_sales / 100.0) * 0.8
   
    expected_base_price = (current_price * passengers) * price_factor_calc 
    expected_final_price = expected_base_price + 100.0 # Regra 2.2.4 No. 3

    result = system.book_flight(1, booking_time, 10, current_price, previous_sales, False, booking_time + timedelta(hours=2), 0)

    assert result.total_price == pytest.approx(expected_final_price)

def test_group_discount_is_exact(system):
    
    passengers = 6 # Mais de 4 passageiros
    current_price = 500.0
    previous_sales = 10

    price_factor_calc = (previous_sales / 100.0) * 0.8
   
    price_before_discount = (current_price * passengers) * price_factor_calc 
    expected_price = price_before_discount * 0.95 

    result = system.book_flight(passengers, datetime.now(), 10, current_price, previous_sales, False, datetime.now() + timedelta(hours=72), 0)

    assert result.total_price == pytest.approx(expected_price)

def test_points_applied_is_exact(system):
    
    passengers = 1
    current_price = 500.0
    previous_sales = 10
    reward_points = 1000

    price_factor_calc = (previous_sales / 100.0) * 0.8
    
    base_price = (current_price * passengers) * price_factor_calc 
    expected_price = base_price - (reward_points * 0.01) 

    result = system.book_flight(passengers, datetime.now(), 10, current_price, previous_sales, False, datetime.now() + timedelta(hours=72), reward_points)
    
    assert result.points_used is True
    
    assert result.total_price == pytest.approx(max(0.0, expected_price))

def test_full_refund_is_exact_and_correct_return_values(system):
   
    passengers = 1
    current_price = 500.0
    previous_sales = 0 
    price_factor_calc = (previous_sales / 100.0) * 0.8

    expected_refund_base = (current_price * passengers) * price_factor_calc 
    
    result = system.book_flight(passengers, datetime.now(), 10, current_price, previous_sales, True, datetime.now() + timedelta(hours=72), 0)
    
  
    assert result.refund_amount == pytest.approx(expected_refund_base if expected_refund_base > 0 else 0.0) 
    assert result.confirmation is False
    assert result.total_price == pytest.approx(0.0)
    assert result.points_used is False

def test_half_refund_is_exact_and_correct_return_values(system):
 
    passengers = 1
    current_price = 500.0
    previous_sales = 0 

    expected_refund = 50.0 
   
    
    result = system.book_flight(passengers, datetime.now(), 10, current_price, previous_sales, True, datetime.now() + timedelta(hours=10), 0)

   
    assert result.refund_amount == pytest.approx(expected_refund) 
    assert result.confirmation is False
    assert result.total_price == pytest.approx(0.0)
    assert result.points_used is False



def test_kill_mutant_17_exact_seats(system):
    
    result = system.book_flight(10, datetime.now(), 10, 500.0, 10, False, datetime.now() + timedelta(hours=72), 0)
    assert result.confirmation is True

def test_kill_mutants_19_20_21_23_24_price_factor_calculation(system):
    
    passengers = 2
    current_price = 500.0
    previous_sales = 10
   
    price_factor_calc = (previous_sales / 100.0) * 0.8
    expected_price = (current_price * passengers) * price_factor_calc 

    result = system.book_flight(passengers, datetime.now(), 20, current_price, previous_sales, False, datetime.now() + timedelta(hours=72), 0)
    assert result.total_price == pytest.approx(expected_price)

def test_kill_mutant_29_hours_calculation(system):
    
    booking_time = datetime.now()
    departure_time = booking_time + timedelta(hours=23, minutes=59, seconds=59) 
    passengers = 1
    current_price = 500.0
    previous_sales = 0
    price_factor_calc = (previous_sales / 100.0) * 0.8
    
    base_price = (current_price * passengers) * price_factor_calc
    expected_price_with_fee = base_price + 100.0

    result = system.book_flight(passengers, booking_time, 10, current_price, previous_sales, False, departure_time, 0)
    assert result.total_price == pytest.approx(expected_price_with_fee)

def test_kill_mutants_31_32_last_minute_boundary(system):
    
    booking_time = datetime.now()
    departure_time = booking_time + timedelta(hours=24) 
    passengers = 1
    current_price = 500.0
    previous_sales = 0
    price_factor_calc = (previous_sales / 100.0) * 0.8
    
    expected_price_without_fee = (current_price * passengers) * price_factor_calc 

    result = system.book_flight(passengers, booking_time, 10, current_price, previous_sales, False, departure_time, 0)
    assert result.total_price == pytest.approx(expected_price_without_fee)

def test_kill_mutants_36_37_group_discount_boundary(system):

    current_price = 500.0
    previous_sales = 0
    price_factor_calc = (previous_sales / 100.0) * 0.8
    
    
    passengers_4 = 4 
  
    expected_price_4 = (current_price * passengers_4) * price_factor_calc 
    result_4 = system.book_flight(passengers_4, datetime.now(), 10, current_price, previous_sales, False, datetime.now() + timedelta(hours=72), 0)
    assert result_4.total_price == pytest.approx(expected_price_4)

    
    passengers_5 = 5 
   
    price_before_discount_5 = (current_price * passengers_5) * price_factor_calc 
    expected_price_5 = price_before_discount_5 * 0.95
    result_5 = system.book_flight(passengers_5, datetime.now(), 10, current_price, previous_sales, False, datetime.now() + timedelta(hours=72), 0)
    assert result_5.total_price == pytest.approx(expected_price_5)


def test_kill_mutants_41_42_reward_points_boundary(system):
  
    passengers = 1
    current_price = 500.0
    previous_sales = 0
    price_factor_calc = (previous_sales / 100.0) * 0.8
   
    expected_price_base = (current_price * passengers) * price_factor_calc 

 
    result_0 = system.book_flight(passengers, datetime.now(), 10, current_price, previous_sales, False, datetime.now() + timedelta(hours=72), 0)
    assert result_0.points_used is False
    assert result_0.total_price == pytest.approx(expected_price_base) 

   
    result_1 = system.book_flight(passengers, datetime.now(), 10, current_price, previous_sales, False, datetime.now() + timedelta(hours=72), 1)
    expected_price_1 = expected_price_base - (1 * 0.01)
    assert result_1.points_used is True
    
    assert result_1.total_price == pytest.approx(max(0.0, expected_price_1)) 

def test_kill_mutants_49_to_52_negative_price_becomes_zero(system):
 
    result_neg = system.book_flight(1, datetime.now(), 10, 100.0, 0, False, datetime.now() + timedelta(hours=72), 11000) 
    assert result_neg.total_price == pytest.approx(0.0)

    
    result_zero = system.book_flight(1, datetime.now(), 10, 100.0, 0, False, datetime.now() + timedelta(hours=72), 10000) 
    assert result_zero.total_price == pytest.approx(0.0) 

def test_kill_mutants_53_54_full_refund_at_exactly_48_hours(system):
    
    booking_time = datetime.now()
    departure_time = booking_time + timedelta(hours=48)
    passengers = 1
    current_price = 500.0
    previous_sales = 0
    price_factor_calc = (previous_sales / 100.0) * 0.8
   
    expected_refund_base = (current_price * passengers) * price_factor_calc 
    
    result = system.book_flight(passengers, booking_time, 10, current_price, previous_sales, True, departure_time, 0)
   
    assert result.refund_amount == pytest.approx(expected_refund_base if expected_refund_base > 0 else 0.0)
