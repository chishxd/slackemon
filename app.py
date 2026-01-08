import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# This sample slack application uses SocketMode
# For the companion getting started setup guide,
# see: https://docs.slack.dev/tools/bolt-python/getting-started

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

player_pokedex : dict[str, str] = {}

@app.message("slackemon.choose")
def choose_pokemon(message, say):
    user_id = message['user']

    if user_id in player_pokedex:
        chosen_pokemon = player_pokedex[user_id].capitalize()
        say(text=f"You have already chosen your partner, {chosen_pokemon}! Your journey has already begun.")
        return
    
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
def handle_starter_choice(ack, body, say):
    ack()

    user_id = body["user"]["id"]

    chosen_pokemon_name : str = body["actions"][0]["value"]

    if user_id in player_pokedex:
        say(text="You've already made your choice, trainer!")
        return

    player_pokedex[user_id] = chosen_pokemon_name

    say(text=f"<@{user_id}> has chosen {chosen_pokemon_name.capitalize()}! Their adventure begins now!")

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click",
                },
            }
        ],
        text=f"Hey there <@{message['user']}>!",
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()