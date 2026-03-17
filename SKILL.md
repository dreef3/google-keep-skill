---
name: google-keep
description: Read notes, lists, and labels from Google Keep via a local REST API.
allowed-tools: Bash
---

# Google Keep (Read-Only)

Use this skill to read the user's Google Keep notes and lists.

The API runs at `http://google-keep-api:8080` (docker-compose service name) or `http://localhost:8080` when running locally.

## Available Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notes` | List all notes |
| GET | `/notes/{id}` | Get a single note by ID |
| GET | `/notes/search/query?q=<text>` | Search notes by text |
| GET | `/labels` | List all labels |
| POST | `/sync` | Force sync with Google Keep |

### Query Parameters for `GET /notes`

- `pinned=true|false` — filter pinned notes
- `archived=true|false` — filter archived notes
- `trashed=true|false` — include trashed notes (default: false)
- `label=<name>` — filter by label name

## Examples

List all non-archived notes:
```bash
curl http://localhost:8080/notes
```

List pinned notes:
```bash
curl "http://localhost:8080/notes?pinned=true"
```

Search for notes containing "grocery":
```bash
curl "http://localhost:8080/notes/search/query?q=grocery"
```

Get notes with a specific label:
```bash
curl "http://localhost:8080/notes?label=Work"
```

Get a single note:
```bash
curl http://localhost:8080/notes/<note_id>
```

List all labels:
```bash
curl http://localhost:8080/labels
```

## Response Shape

Each note object contains:
- `id` — unique note ID
- `title` — note title
- `text` — note body text
- `pinned` — boolean
- `archived` — boolean
- `trashed` — boolean
- `color` — color string (e.g. "white", "red")
- `labels` — array of label name strings
- `kind` — `"note"` or `"list"`
- `items` — array of `{text, checked}` objects (only present for list notes)

## Setup

Set these environment variables before starting the container:

```
GOOGLE_EMAIL=your@gmail.com
GOOGLE_MASTER_TOKEN=<master token from gpsoauth>
```

Start the service:
```bash
docker compose up -d
```
