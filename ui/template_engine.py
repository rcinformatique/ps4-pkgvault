import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TYPE_INFO = {
    "game":     {"label": "BASE",     "icon": "🎮", "bg": "#dce8f8", "badge": "#0067c0"},
    "dlc":      {"label": "DLC",      "icon": "🧩", "bg": "#d4ecd4", "badge": "#107c10"},
    "update":   {"label": "UPDATE",   "icon": "⬆️", "bg": "#d4e8f8", "badge": "#0078d4"},
    "backport": {"label": "BACKPORT", "icon": "⏮️", "bg": "#f8e8d4", "badge": "#ca5010"},
}


class TemplateEngine:
    """
    Moteur Jinja2 pour générer le HTML des pages riches.
    """

    def __init__(self):
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html"]),
        )

    def render_detail(
        self,
        pkg_data: dict,
        related: list[dict] = None
    ) -> str:
        """
        Génère le HTML de la page de détail.
        pkg_data : dictionnaire du PKG
        related  : liste des PKG associés (DLC, UPDATE, BACKPORT)
        """
        template  = self._env.get_template("detail.html")
        pkg_type  = pkg_data.get("type", "game")
        type_info = TYPE_INFO.get(pkg_type, TYPE_INFO["game"])

        # Prépare les related avec leurs infos de type
        related_data = []
        for rel in (related or []):
            rel_type = rel.get("type", "game")
            rel_info = TYPE_INFO.get(rel_type, TYPE_INFO["game"])
            related_data.append({
                **rel,
                "type_label": rel_info["label"],
                "type_icon":  rel_info["icon"],
                "type_bg":    rel_info["bg"],
                "type_badge": rel_info["badge"],
            })

        # Normalise les chemins Windows pour les URLs file:///
        cover_path = pkg_data.get("cover_path", "")
        if cover_path:
            cover_path = cover_path.replace("\\", "/")

        screenshots = []
        for s in pkg_data.get("screenshots", []):
            screenshots.append(s.replace("\\", "/"))

        pkg_normalized = {
            **pkg_data,
            "cover_path":  cover_path,
            "screenshots": screenshots,
        }

        return template.render(
            pkg=pkg_normalized,
            type_label=type_info["label"],
            type_icon=type_info["icon"],
            type_bg=type_info["bg"],
            type_badge=type_info["badge"],
            related=related_data,
        )