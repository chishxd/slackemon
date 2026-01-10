import os
import re
import logging

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