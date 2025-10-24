import pytest
from src.energy.EnergyManagementResult import EnergyManagementResult 

def test_energy_management_result_integrity():
    """
    Testa a inicialização e a representação string (repr) da classe EnergyManagementResult.
    """
    
    expected_status = "Standby"
    expected_saving_mode = True
    expected_temp_active = False
    expected_total_used = 150.75
    
    result = EnergyManagementResult(
        device_status=expected_status, 
        energy_saving_mode=expected_saving_mode, 
        temperature_regulation_active=expected_temp_active, 
        total_energy_used=expected_total_used
    )
    
    assert result.device_status == expected_status 
    assert result.energy_saving_mode is expected_saving_mode 
    assert result.temperature_regulation_active is expected_temp_active
    assert result.total_energy_used == expected_total_used

    repr_string = repr(result)

    assert repr_string.startswith("EnergyManagementResult(")
    assert f"device_status={expected_status}" in repr_string
    assert f"energy_saving_mode={expected_saving_mode}" in repr_string
    assert f"temperature_regulation_active={expected_temp_active}" in repr_string
    assert f"total_energy_used={expected_total_used}" in repr_string
    assert "XX" not in repr_string