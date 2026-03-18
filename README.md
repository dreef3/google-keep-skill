# google-keep-skill

A REST API for reading and managing Google Keep notes, exposed as a Claude skill.

## Setup

### 1. Get a Google master token

The API authenticates using a Google master token rather than your password. To obtain one, use [gpsoauth](https://github.com/simon-weber/gpsoauth) or a tool like [get-google-token](https://github.com/bryanadamson/get-google-token):

```bash
pip install gpsoauth
python3 -c "
import gpsoauth
email = 'your@gmail.com'
password = input('App password: ')
res = gpsoauth.perform_master_login(email, password, 'your-device-id')
print(res.get('Token'))
"
```

Use an [app password](https://myaccount.google.com/apppasswords) if you have 2FA enabled.

### 2. Configure environment variables

```bash
export GOOGLE_EMAIL=your@gmail.com
export GOOGLE_MASTER_TOKEN=<token from step 1>
```

Or create a `.env` file:

```
GOOGLE_EMAIL=your@gmail.com
GOOGLE_MASTER_TOKEN=your_master_token_here
```

### 3. Start the service

```bash
docker compose up -d
```

The API will be available at `http://localhost:8080`.

### 4. Install the Claude skill

Copy `SKILL.md` to your Claude skills directory (typically `~/.claude/skills/`):

```bash
cp SKILL.md ~/.claude/skills/google-keep.md
```

## API

See [SKILL.md](SKILL.md) for the full API reference and usage examples.
