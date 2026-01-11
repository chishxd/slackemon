import os
import re
import logging
import random

from typing import TypedDict, Callable, Any
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from helpers import get_pokemon_details, calculate_stats

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
active_battles = {}

@app.message("sm.choose")
def choose_pokemon(message: dict, say: Callable, logger: logging.Logger) -> None:
    """ Handle the initial Pokemon selection for a new player.

    This function presents starter Pokemon choices (Bulbasaur, Charmander, or Squirtle) 
    to users who haven't chosen a partner yet. If the user has already chosen a Pokemon, 
    they are notified that their journey has begun.
    Args:
        message (dict): The incoming Slack message object containing user information.
            Expected to have a 'user' key with the user ID.
        say (callable): Slack say function used to send messages back to the channel/user.
        logger (logging.Logger): Logger instance for recording function events and errors.
    Returns:
        None: Returns early if the user has already chosen a Pokemon, otherwise presents
            the selection interface via Slack blocks.
    Side Effects:
        - Logs info and warning messages about user actions
        - Sends Slack messages with interactive button blocks for Pokemon selection
        - Checks global player_pokedex dictionary for existing user choices
    Note:
        Depends on the global 'player_pokedex' dictionary to track user selections.
        The actual Pokemon selection is handled by action handlers for the button interactions.
    """

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
def handle_starter_choice(ack: Callable, body: dict, say: Callable, logger: logging.Logger):
    """    Handle the user's selection of a starter Pokémon.

        This function processes the user's choice of a starter Pokémon. 
        It validates that the user hasn't already chosen a starter, then adds the
        chosen Pokémon to the player's Pokédex at level 5 and announces their choice.

            ack: Acknowledgment function from Slack that must be called to confirm receipt
                of the interaction.
            body (dict): The interaction payload from Slack containing user information and
                the selected action details.
            say: Slack function to send a message to the channel where the interaction occurred.
            logger: Logger instance for recording events and debugging information.

        Returns:
            None

        Side Effects:
            - Acknowledges the Slack interaction
            - Updates the global player_pokedex dictionary with the user's starter Pokémon
            - Sends a message to the channel announcing the user's choice
            - Logs the interaction and any warnings/errors

        Raises:
            None explicitly, but may raise KeyError if expected keys are missing from body.
    """
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


@app.message("sm.challenge")
def handle_challenge_message(message: dict, say: Callable, logger: logging.Logger):
    """Handle the pokemon battle initiation logic

    This function initiates a pokemon battle after validating if they have any pokemon in party

    Args:
        message (dict): The incoming slack message object containing user inforrmation
        say (Callable): A slack function to send messages in channels
        logger (logging.Logger): The Logger to log stuff
    """

    user_id = message["user"]
    if user_id not in player_pokedex:
        say("You haven't chose a pokemon yet... Please choose one!")
        return
    
    player_pkmn = get_pokemon_details(player_pokedex[user_id]["pkmn_name"])
    player_pkmn_stats = calculate_stats(player_pkmn, player_pokedex[user_id]["level"])

    rndm_pkmn_id = random.randint(1, 151)
    rndm_pkmn_lvl = random.randint(3, 7)

    rndm_pkmn = get_pokemon_details(rndm_pkmn_id)
    rndm_pkmn_stats = calculate_stats(rndm_pkmn, rndm_pkmn_lvl)

    active_battles[user_id] = {"player_pkmn": player_pkmn, "player_pkmn_stats": player_pkmn_stats,
                                "enemy_pkmn": rndm_pkmn, "enemy_pkmn_stats": rndm_pkmn_stats}
    
    
    blocks =  [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"A wild {rndm_pkmn["name"]} has appeared!"
			}
		},
		{
			"type": "image",
			"title": {
				"type": "plain_text",
				"text": f"{rndm_pkmn["name"]}!",
				"emoji": True
			},
			"image_url": rndm_pkmn["sprite"],
			"alt_text": rndm_pkmn["name"]
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": f"{rndm_pkmn['name']} *HP*: {rndm_pkmn_stats["hp"]}/{rndm_pkmn_stats["hp"]}"
				},
                {
					"type": "mrkdwn",
					"text": f"{player_pkmn['name']} *HP*: {player_pkmn_stats["hp"]}/{player_pkmn_stats["hp"]}"
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": player_pkmn['moves'][0].capitalize(),
						"emoji": True
					},
					"value": player_pkmn['moves'][0],
					"action_id": "move_0"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": player_pkmn['moves'][1].capitalize(),
						"emoji": True
					},
					"value": player_pkmn['moves'][1],
					"action_id": "move_1"
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Run",
						"emoji": True
					},
					"value": "run",
					"action_id": "run",
					"style": "danger"
				}
			]
		}
	]

    say(
        blocks = blocks,
    )



# Start the app
if __name__ == "__main__":
    logging.info("Starting Slackemon bot in Socket Mode...")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
