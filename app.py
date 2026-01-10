import os
import re
import logging
import pokebase as pb
from pprint import pprint

from typing import TypedDict
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Initializes the app with bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


class PokemonData(TypedDict):
    """
    Structure of Pokemon data stored per user.
    
    Example:
    {
        'User_ID': {
            'pkmn_name': 'charmander',
            'level': 5
        }
    }
    """
    pkmn_name: str
    level: int


player_pokedex: dict[str, PokemonData] = {}


@app.message("sm.choose")
def choose_pokemon(message, say, logger):
    user_id = message['user']
    logger.info(f"Received 'choose' message from user {user_id}")

    if user_id in player_pokedex:
        chosen_pokemon = player_pokedex[user_id]['pkmn_name'].capitalize()
        logger.warning(f"User {user_id} has already chosen {chosen_pokemon}. Denying request.")
        say(text=f"You have already chosen your partner, {chosen_pokemon}! Your journey has already begun.")
        return
    
    logger.info(f"Presenting starter choices to user {user_id}")
    say(
        text="Welcome to the world of Pokémon! It's time to choose your first partner.",
        blocks=[
            {
                "type":"section",
                "text": {
                    "type" : "mrkdwn",
                    "text" : "Welcome to the world of Pokémon! It's time to choose your first partner."
                }
            },
            {
                "type" : "actions",
                "elements" : [
                   {
                        "type": "button",
                        "text": { "type": "plain_text", "text": "Bulbasaur 🌱", "emoji": True },
                        "action_id": "choose_bulbasaur",
                        "value": "bulbasaur"
                    },
                    {
                        "type": "button",
                        "text": { "type": "plain_text", "text": "Charmander 🔥", "emoji": True },
                        "action_id": "choose_charmander",
                        "value": "charmander"
                    },
                    {
                        "type": "button",
                        "text": { "type": "plain_text", "text": "Squirtle 💧", "emoji": True },
                        "action_id": "choose_squirtle",
                        "value": "squirtle"
                    }

                ]
            }
        ]
    )
        

@app.action(re.compile(r'^choose_'))
def handle_starter_choice(ack, body, say, logger):
    ack()

    user_id = body["user"]["id"]
    chosen_pokemon_name : str = body["actions"][0]["value"]
    logger.info(f"Received action '{body['actions'][0]['action_id']}' from user {user_id}")

    if user_id in player_pokedex:
        logger.warning(f"User {user_id} tried to choose again after already having a Pokémon.")
        say(text="You've already made your choice, trainer!")
        return

    player_pokedex[user_id] = {'pkmn_name' : chosen_pokemon_name, 'level': 5}
    logger.info(f"User {user_id} successfully chose {chosen_pokemon_name}. Pokedex updated.")
    say(text=f"<@{user_id}> has chosen {chosen_pokemon_name.capitalize()}! Their adventure begins now!")


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

# Start the app
if __name__ == "__main__":
    logging.info("Starting Slackemon bot in Socket Mode...")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

# if __name__ == "__main__":
#     print("--- Testing get_pokemon_details() ---")
    
#     # Test with a name
#     bulbasaur_base_stats = get_pokemon_details("bulbasaur")
#     print("Bulbasaur's Base Stats:")
#     pprint(bulbasaur_base_stats)
    
#     # Test with an ID to be sure
#     squirtle_base_stats = get_pokemon_details(7)
#     print("\nSquirtle's Base Stats:")
#     pprint(squirtle_base_stats)

#     print("--- Testing get_pokemon_details() ---")
#     bulbasaur_base_stats = get_pokemon_details("bulbasaur")
#     print("Bulbasaur's Base Stats:")
#     pprint(bulbasaur_base_stats)
#     squirtle_base_stats = get_pokemon_details(7)
#     print("\nSquirtle's Base Stats:")
#     pprint(squirtle_base_stats)

#     print("\n--- Testing calculate_battle_stats() ---")
    
#     # Let's use Bulbasaur's data to test a few levels
#     level_1_stats = calculate_stats(bulbasaur_base_stats, 1)
#     print("Level 1 Bulbasaur's Battle Stats:")
#     pprint(level_1_stats)

#     level_5_stats = calculate_stats(bulbasaur_base_stats, 5)
#     print("\nLevel 5 Bulbasaur's Battle Stats:")
#     pprint(level_5_stats)