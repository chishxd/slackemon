import pokebase as pb


def get_pokemon_details(name_or_id : str | int) -> dict:
    """Fetches and standardizes base pokemon data

    This function queries the PokeAPI (via the pokebase library) to retrieve 
    the full data for a single Pokemon. It then extracts and
    simplifies this data into a dictionary containing only the essential
    base stats needed for our game.

    Args:
        name_or_id (str): Unique Identifier of a pokemon, can be it's name(e.g pikachu) or national pokedex ID (i.e 27)

    Returns:
        dict: A Dictionary with some base stats
              - name (str): The capitalized species name.
              - sprite (str): The URL to the default front sprite.
              - hp (int): The base HP stat.
              - moves (list): A list of the Pokémon's first two move names.
        None: Returns None if the Pokémon data cannot be fetched.
    """
    pokemon_obj = pb.pokemon(name_or_id)
    details = {
        "name" : pokemon_obj.name.capitalize(),
        "sprite": pokemon_obj.sprites.front_default,
        # This is just a placeholder for now
        "hp": pokemon_obj.stats[0].base_stat * 2,
        "moves": [
            pokemon_obj.moves[0].move.name,
            pokemon_obj.moves[1].move.name
        ]
    }
    return details

def calculate_stats(pkmn_base: dict[str, str | int], lvl):
    """Calculates battle stats of a pokemon based on it's level

    Applies a simple stat formula to a Pokemon's base stat to determine
    final stuff like HP, Attack and Defense(Only HP for now, Imma work
    on everything else soon) 

    The formula used is: `Max HP = Base HP + (Level * 5)`

    Args:
        pkmn_base (dict): A dictionary of a pokemon's base stat ,
                            as generated from get_pokemon_details()
        lvl (int): Current Level of the Pokemon

    Returns:
        dict: A new dictionary containing the final battle stats.
              Currently, this only includes 'hp', but can be expanded.
    """

    max_hp = int(pkmn_base["hp"]) + (lvl * 5)
    return {"hp": max_hp}