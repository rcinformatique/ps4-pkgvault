import json
import threading
from datetime import datetime
from pathlib import Path

# Fichier de persistance
ACTIVITY_FILE = Path(__file__).parent.parent / "data" / "activity.json"
MAX_EVENTS    = 500  # Limite pour ne pas grossir indéfiniment


# ------------------------------------------------------------------ #
#  Types d'événements                                                  #
# ------------------------------------------------------------------ #

EVENT_SCAN  = "scan"
EVENT_API   = "api"
EVENT_ERROR = "error"

EVENT_META = {
    EVENT_SCAN:  {"icon": "📦", "color": "#4ade80", "label": "Scan"},
    EVENT_API:   {"icon": "🌐", "color": "#60a5fa", "label": "API"},
    EVENT_ERROR: {"icon": "❌", "color": "#f87171", "label": "Erreur"},
}


# ------------------------------------------------------------------ #
#  Singleton ActivityLogger                                            #
# ------------------------------------------------------------------ #

class ActivityLogger:
    _instance = None
    _lock     = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._events   = []
                    cls._instance._listeners = []
                    cls._instance._load()
        return cls._instance

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def log_scan(self, pkg_data: dict):
        """PKG scanné avec succès."""
        title    = pkg_data.get("title_api") or pkg_data.get("title") or "Inconnu"
        title_id = pkg_data.get("title_id", "")
        pkg_type = pkg_data.get("type", "game")
        size_str = pkg_data.get("size_str", "")
        filename = pkg_data.get("filename", "")

        type_labels = {
            "game":     "Jeu",
            "update":   "Mise à jour",
            "dlc":      "DLC",
            "backport": "Backport",
        }

        self._add(
            event_type = EVENT_SCAN,
            message    = f"{title}",
            detail     = f"{type_labels.get(pkg_type, pkg_type)} · {title_id} · {size_str}",
            filename   = filename,
            extra      = {
                "title_id": title_id,
                "pkg_type": pkg_type,
                "filepath": pkg_data.get("filepath", ""),
            }
        )

    def log_api(self, title: str, source: str = "", content_id: str = ""):
        """Données API récupérées pour un jeu."""
        self._add(
            event_type = EVENT_API,
            message    = title,
            detail     = f"Source : {source}" if source else "",
            filename   = content_id,
            extra      = {"content_id": content_id, "source": source}
        )

    def log_error(self, filepath: str, reason: str = ""):
        """PKG ignoré ou erreur."""
        filename = Path(filepath).name if filepath else "Inconnu"
        self._add(
            event_type = EVENT_ERROR,
            message    = filename,
            detail     = reason or "Fichier ignoré",
            filename   = filename,
            extra      = {"filepath": filepath}
        )

    def get_events(
        self,
        event_type: str | None = None,
        limit: int = 200
    ) -> list[dict]:
        """Retourne les événements, du plus récent au plus ancien."""
        events = self._events[::-1]  # plus récent en premier
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[:limit]

    def get_counts(self) -> dict:
        counts = {EVENT_SCAN: 0, EVENT_API: 0, EVENT_ERROR: 0}
        for e in self._events:
            t = e.get("type")
            if t in counts:
                counts[t] += 1
        return counts

    def clear(self):
        self._events = []
        self._save()
        self._notify()

    def add_listener(self, callback):
        """Enregistre un callback appelé à chaque nouvel événement."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback):
        self._listeners = [l for l in self._listeners if l != callback]

    # ------------------------------------------------------------------ #
    #  Interne                                                             #
    # ------------------------------------------------------------------ #

    def _add(
        self,
        event_type: str,
        message: str,
        detail: str = "",
        filename: str = "",
        extra: dict | None = None,
    ):
        event = {
            "type":      event_type,
            "message":   message,
            "detail":    detail,
            "filename":  filename,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "extra":     extra or {},
        }
        with self._lock:
            self._events.append(event)
            # Limite la taille
            if len(self._events) > MAX_EVENTS:
                self._events = self._events[-MAX_EVENTS:]
        self._save()
        self._notify(event)

    def _notify(self, event: dict | None = None):
        for cb in list(self._listeners):
            try:
                cb(event)
            except Exception:
                pass

    def _save(self):
        try:
            ACTIVITY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ACTIVITY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._events, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def _load(self):
        try:
            if ACTIVITY_FILE.exists():
                with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
                    self._events = json.load(f)
        except (OSError, json.JSONDecodeError):
            self._events = []

    def reset(self):
        """Vide les événements et supprime le fichier JSON."""
        with self._lock:
            self._events = []
        try:
            if ACTIVITY_FILE.exists():
                ACTIVITY_FILE.unlink()
        except OSError:
            pass
        self._notify()

# Accès global
activity = ActivityLogger()