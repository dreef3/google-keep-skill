---
name: google-keep
description: Read, create, edit, archive, and share notes and lists in Google Keep via a local REST API. Deletes are not supported.
allowed-tools: Bash
---

# Google Keep

Use this skill to read and manage the user's Google Keep notes and lists. Notes can be created, edited, archived, and shared with collaborators, but not deleted.

The API runs at `http://google-keep-api:8080` (docker-compose service name) or `http://localhost:8080` when running locally.

## Available Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notes` | List all notes |
| GET | `/notes/{id}` | Get a single note by ID |
| GET | `/notes/search/query?q=<text>` | Search notes by text |
| POST | `/notes` | Create a new note or list |
| PATCH | `/notes/{id}` | Edit an existing note |
| POST | `/notes/{id}/archive` | Archive a note |
| POST | `/notes/{id}/collaborators` | Add a collaborator by email |
| DELETE | `/notes/{id}/collaborators/{email}` | Remove a collaborator |
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

Create a note:
```bash
curl -X POST http://localhost:8080/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "My Note", "text": "Some content", "pinned": false}'
```

Create a list note:
```bash
curl -X POST http://localhost:8080/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Shopping", "kind": "list"}'
```

Edit a note (only provided fields are updated):
```bash
curl -X PATCH http://localhost:8080/notes/<note_id> \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "pinned": true}'
```

Archive a note:
```bash
curl -X POST http://localhost:8080/notes/<note_id>/archive
```

Share a note with a collaborator:
```bash
curl -X POST http://localhost:8080/notes/<note_id>/collaborators \
  -H "Content-Type: application/json" \
  -d '{"email": "friend@example.com"}'
```

Remove a collaborator:
```bash
curl -X DELETE http://localhost:8080/notes/<note_id>/collaborators/friend@example.com
```

List all labels:
```bash
curl http://localhost:8080/labels
```

## Request Body for `POST /notes`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `""` | Note title |
| `text` | string | `""` | Note body text |
| `pinned` | boolean | `false` | Pin the note |
| `color` | string | `null` | Color (e.g. `"white"`, `"red"`, `"yellow"`, `"green"`, `"blue"`) |
| `labels` | array of strings | `[]` | Label names to apply (must already exist) |
| `kind` | string | `"note"` | `"note"` or `"list"` |

## Request Body for `PATCH /notes/{id}`

All fields are optional; only provided fields are updated.

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | New title |
| `text` | string | New body text |
| `pinned` | boolean | Pin or unpin |
| `archived` | boolean | Archive or unarchive |
| `color` | string | New color |
| `labels` | array of strings | Replace label set (must already exist) |

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
- `collaborators` — array of collaborator email strings
- `kind` — `"note"` or `"list"`
- `items` — array of `{text, checked}` objects (only present for list notes)
