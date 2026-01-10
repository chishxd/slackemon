import os
import re
import logging
import pokebase as pb

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Initializes the app with bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

player_pokedex : dict[str, str] = {}

@app.message("sm.choose")
def choose_pokemon(message, say, logger):
    user_id = message['user']
    logger.info(f"Received 'choose' message from user {user_id}")

    if user_id in player_pokedex:
        chosen_pokemon = player_pokedex[user_id].capitalize()
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

    player_pokedex[user_id] = chosen_pokemon_name
    logger.info(f"User {user_id} successfully chose {chosen_pokemon_name}. Pokedex updated.")
    say(text=f"<@{user_id}> has chosen {chosen_pokemon_name.capitalize()}! Their adventure begins now!")


def get_pokemon_details(name):
    pokemon_obj = pb.pokemon(name)
    details = {
        "name" : pokemon_obj.name.capitalize(),
        "sprite": pokemon_obj.sprites.front_default,
        "hp": pokemon_obj.stats[0].base_stat * 2,
        "moves": [
            pokemon_obj.moves[0].move.name,
            pokemon_obj.moves[1].move.name
        ]
    }
    return details

# Start the app
if __name__ == "__main__":
    logging.info("Starting Slackemon bot in Socket Mode...")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()