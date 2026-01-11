# Slackemon

A Slack Bot to Play Pokemon!

## Running locally

### 1. Setup environment variables

```zsh
# Replace with your tokens
export SLACK_BOT_TOKEN=<your-bot-token>
export SLACK_APP_TOKEN=<your-app-level-token>
```

### 2. Setup your local project

```zsh
# Clone this project onto your machine
git clone https://github.com/chishxd/slackemon.git

# Change into this project
cd slackemon/

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### 3. Start servers

```zsh
python3 app.py
```

## Contributing

### Issues and questions

Found a bug or have a question about this project? We'd love to hear from you!

1. Browse to [slackapi/bolt-python/issues](https://github.com/slackapi/bolt-python/issues/new/choose)
1. Create a new issue
1. Mention that you're using this example app

See you there and thanks for helping to improve Bolt for everyone!
