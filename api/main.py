import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import gkeepapi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Google Keep API", version="2.0.0")

keep = gkeepapi.Keep()
_authenticated = False


def get_keep() -> gkeepapi.Keep:
    global _authenticated
    if not _authenticated:
        email = os.environ.get("GOOGLE_EMAIL")
        master_token = os.environ.get("GOOGLE_MASTER_TOKEN")
        if not email or not master_token:
            raise HTTPException(
                status_code=503,
                detail="Google credentials not configured. Set GOOGLE_EMAIL and GOOGLE_MASTER_TOKEN.",
            )
        try:
            keep.authenticate(email, master_token)
            keep.sync()
            _authenticated = True
            logger.info("Authenticated with Google Keep")
        except Exception as e:
            logger.error("Authentication failed: %s", e)
            raise HTTPException(status_code=503, detail=f"Google Keep authentication failed: {e}")
    return keep


class ListItemOut(BaseModel):
    text: str
    checked: bool


class NoteCreate(BaseModel):
    title: str = ""
    text: str = ""
    pinned: bool = False
    color: Optional[str] = None
    labels: list[str] = []
    kind: str = "note"  # "note" or "list"


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None
    color: Optional[str] = None
    labels: Optional[list[str]] = None


class NoteOut(BaseModel):
    id: str
    title: str
    text: str
    pinned: bool
    archived: bool
    trashed: bool
    color: str
    labels: list[str]
    items: Optional[list[ListItemOut]] = None  # only for list notes
    kind: str  # "note" or "list"


def _apply_color(note, color: str):
    try:
        note.color = gkeepapi.node.ColorValue(color)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid color: {color!r}")


def _apply_labels(keep_inst, note, label_names: list[str]):
    note.labels.clear()
    for name in label_names:
        label = next((lb for lb in keep_inst.labels() if lb.name == name), None)
        if label is None:
            raise HTTPException(status_code=400, detail=f"Label not found: {name!r}")
        note.labels.add(label)


def _serialize_note(note) -> dict:
    labels = [label.name for label in note.labels.all()]
    kind = "list" if isinstance(note, gkeepapi.node.List) else "note"
    items = None
    if kind == "list":
        items = [{"text": item.text, "checked": item.checked} for item in note.items]
    return {
        "id": note.id,
        "title": note.title,
        "text": note.text,
        "pinned": note.pinned,
        "archived": note.archived,
        "trashed": note.trashed,
        "color": note.color.value if note.color else "white",
        "labels": labels,
        "items": items,
        "kind": kind,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes", response_model=list[NoteOut])
def list_notes(
    pinned: Optional[bool] = Query(None, description="Filter by pinned status"),
    archived: Optional[bool] = Query(None, description="Filter by archived status"),
    trashed: Optional[bool] = Query(False, description="Include trashed notes"),
    label: Optional[str] = Query(None, description="Filter by label name"),
):
    """Return all notes, with optional filters."""
    k = get_keep()
    notes = k.all()

    results = []
    for note in notes:
        if trashed is False and note.trashed:
            continue
        if pinned is not None and note.pinned != pinned:
            continue
        if archived is not None and note.archived != archived:
            continue
        if label is not None:
            note_labels = [lb.name for lb in note.labels.all()]
            if label not in note_labels:
                continue
        results.append(_serialize_note(note))

    return results


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: str):
    """Return a single note by ID."""
    k = get_keep()
    note = k.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return _serialize_note(note)


@app.get("/notes/search/query", response_model=list[NoteOut])
def search_notes(
    q: str = Query(..., description="Text to search for in title and body"),
    trashed: Optional[bool] = Query(False, description="Include trashed notes"),
):
    """Search notes by text (title or body)."""
    k = get_keep()
    q_lower = q.lower()
    results = []
    for note in k.all():
        if trashed is False and note.trashed:
            continue
        if q_lower in note.title.lower() or q_lower in note.text.lower():
            results.append(_serialize_note(note))
    return results


@app.post("/notes", response_model=NoteOut, status_code=201)
def create_note(body: NoteCreate):
    """Create a new note or list."""
    k = get_keep()
    if body.kind == "list":
        note = k.createList(body.title, [])
        if body.text:
            note.text = body.text
    else:
        note = k.createNote(body.title, body.text)
    note.pinned = body.pinned
    if body.color is not None:
        _apply_color(note, body.color)
    if body.labels:
        _apply_labels(k, note, body.labels)
    k.sync()
    return _serialize_note(note)


@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: str, body: NoteUpdate):
    """Edit an existing note. Only provided fields are updated."""
    k = get_keep()
    note = k.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if body.title is not None:
        note.title = body.title
    if body.text is not None:
        note.text = body.text
    if body.pinned is not None:
        note.pinned = body.pinned
    if body.archived is not None:
        note.archived = body.archived
    if body.color is not None:
        _apply_color(note, body.color)
    if body.labels is not None:
        _apply_labels(k, note, body.labels)
    k.sync()
    return _serialize_note(note)


@app.post("/notes/{note_id}/archive", response_model=NoteOut)
def archive_note(note_id: str):
    """Archive a note."""
    k = get_keep()
    note = k.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    note.archived = True
    k.sync()
    return _serialize_note(note)


@app.get("/labels")
def list_labels():
    """Return all label names."""
    k = get_keep()
    return [{"name": label.name} for label in k.labels()]


@app.post("/sync")
def sync():
    """Force a sync with Google Keep servers."""
    k = get_keep()
    try:
        k.sync()
        return {"status": "synced"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {e}")
