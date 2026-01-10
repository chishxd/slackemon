import sys
from pathlib import Path

# Add the parent directory to sys.path to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers import get_pokemon_details, calculate_stats

def test_get_pokemon_details():
    """
    Tests that we can properly fetch data and parse it
    """

    details = get_pokemon_details('bulbasaur')

    assert details is not None
    assert details['name'] == 'Bulbasaur'
    assert isinstance(details['hp'], int)
    assert isinstance(details['moves'], list)
    assert len(details['moves']) >= 2


def test_calculate_stats():
    """
    Tests our custom calculation logic
    """ 

    sample_base_stats: dict[str, str | int] = {'hp': 45}
    level = 5

    expected_hp = 70

    battle_stats = calculate_stats(sample_base_stats, level)

    assert battle_stats['hp'] == expected_hp

