import json as _json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TYPE_INFO = {
    "game":     {"label": "BASE",     "icon": "🎮", "bg": "#dce8f8", "badge": "#0067c0"},
    "dlc":      {"label": "DLC",      "icon": "🧩", "bg": "#d4ecd4", "badge": "#107c10"},
    "update":   {"label": "UPDATE",   "icon": "⬆️", "bg": "#d4e8f8", "badge": "#0078d4"},
    "backport": {"label": "BACKPORT", "icon": "⏮️", "bg": "#f8e8d4", "badge": "#ca5010"},
}

DEFAULT_STATS = {
    "game": 0, "dlc": 0, "update": 0,
    "backport": 0, "total_size": "0 Go", "total_go": "0",
}

DEFAULT_SETTINGS = {
    "rawg_api_key":       "",
    "igdb_client_id":     "",
    "igdb_client_secret": "",
    "auto_fetch":         "1",
    "card_min_width":     "180",
    "language":           "fr",
    "cache_info":         "cache/covers/ · 0 fichiers",
}


def _normalize_pkg(pkg: dict) -> dict:
    pkg_type = pkg.get("type", "game")
    info     = TYPE_INFO.get(pkg_type, TYPE_INFO["game"])
    cover    = (pkg.get("cover_path") or "").replace("\\", "/")
    screenshots = [
        s.replace("\\", "/")
        for s in (pkg.get("screenshots") or [])
    ]
    return {
        **pkg,
        "type_label":  info["label"],
        "type_icon":   info["icon"],
        "type_bg":     info["bg"],
        "type_badge":  info["badge"],
        "cover_path":  cover,
        "screenshots": screenshots,
    }


def _base_context(
    active_page: str,
    stats: dict = None,
    status_msg: str = "Prêt",
    active_filter: str = "all",
    active_sort: str = "title",
    count_str: str = "0 fichiers",
    view_mode: str = "grid",
) -> dict:
    s = stats or DEFAULT_STATS
    return {
        "active_page":   active_page,
        "active_filter": active_filter,
        "active_sort":   active_sort,
        "count_str":     count_str,
        "status_msg":    status_msg,
        "view_mode":     view_mode,
        "stats": {
            "game":       s.get("game",       0),
            "dlc":        s.get("dlc",        0),
            "updates":    s.get("update",     0),
            "backport":   s.get("backport",   0),
            "total_size": s.get("total_size", "0 Go"),
            "total_go":   s.get("total_go",   "0"),
        },
    }


class TemplateEngine:

    def __init__(self):
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=False,
        )
        self._env.filters["tojson"] = lambda v: Markup(
            _json.dumps(v, ensure_ascii=False)
        )

    def _render(self, template_name: str, context: dict) -> str:
        return self._env.get_template(template_name).render(**context)

    def render_library(
        self,
        packages: list[dict],
        stats: dict = None,
        active_filter: str = "all",
        active_sort: str = "title",
        last_scan: str = "",
        active_folder: str = "",
        status_msg: str = "Prêt",
        count_str: str = "",
        view_mode: str = "grid",
        card_min_width: int = 180,
    ) -> str:
        s = stats or DEFAULT_STATS
        if not count_str:
            total     = len(packages)
            size      = s.get("total_size", "0 Go")
            count_str = f"{total} fichier{'s' if total > 1 else ''} · {size}"
        ctx = _base_context(
            "library", stats, status_msg,
            active_filter, active_sort, count_str,
            view_mode
        )
        ctx.update({
            "packages":       [_normalize_pkg(p) for p in packages],
            "last_scan":      last_scan,
            "active_folder":  active_folder,
            "view_mode":      view_mode,
            "card_min_width": card_min_width,
        })
        return self._render("library.html", ctx)

    def render_activity(
            self,
            stats: dict = None,
            status_msg: str = "Prêt",
    ) -> str:
        import json as _json
        from core.activity_log import activity, EVENT_SCAN, EVENT_API, EVENT_ERROR

        events = activity.get_events(limit=300)
        counts = activity.get_counts()

        counts_mapped = {
            "scan": counts.get(EVENT_SCAN, 0),
            "api": counts.get(EVENT_API, 0),
            "error": counts.get(EVENT_ERROR, 0),
        }

        ctx = _base_context("activity", stats, status_msg)
        ctx.update({
            "total": len(events),
            "count_scan": counts_mapped["scan"],
            "count_api": counts_mapped["api"],
            "count_error": counts_mapped["error"],
            "events_json": _json.dumps(events, ensure_ascii=False),
            "counts_json": _json.dumps(counts_mapped, ensure_ascii=False),
        })
        return self._render("activity.html", ctx)

    def render_detail(
        self,
        pkg_data: dict,
        related: list[dict] = None,
        stats: dict = None,
        status_msg: str = "Prêt",
    ) -> str:
        ctx = _base_context("detail", stats, status_msg)
        ctx.update({
            "pkg":     _normalize_pkg(pkg_data),
            "related": [_normalize_pkg(r) for r in (related or [])],
        })
        return self._render("detail.html", ctx)

    def render_folders(
        self,
        folders: list[dict],
        stats: dict = None,
        status_msg: str = "Prêt",
    ) -> str:
        ctx = _base_context("folders", stats, status_msg)
        ctx["folders"] = folders or []
        return self._render("folders.html", ctx)

    def render_settings(
        self,
        settings: dict = None,
        stats: dict = None,
        status_msg: str = "Prêt",
    ) -> str:
        ctx = _base_context("settings", stats, status_msg)
        ctx["settings"] = {**DEFAULT_SETTINGS, **(settings or {})}
        return self._render("settings.html", ctx)

    def render_credits(
        self,
        stats: dict = None,
        status_msg: str = "Prêt",
    ) -> str:
        ctx = _base_context("credits", stats, status_msg)
        return self._render("credits.html", ctx)