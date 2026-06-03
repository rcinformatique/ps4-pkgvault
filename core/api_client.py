import re
import time
import requests
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from core.cover_loader import (
    save_cover, save_screenshot,
    get_cached_cover, get_cached_screenshot,
)

API_DELAY = 0.5


# ------------------------------------------------------------------ #
#  Utilitaires                                                         #
# ------------------------------------------------------------------ #

def _clean_search_title(title: str) -> str:
    title = re.sub(r'\bv\d+\.\d+\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\bPS[45]\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'—.*$', '', title)
    title = re.sub(r'-.*update.*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'™|®|©', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def _download_image(url: str, timeout: int = 10) -> bytes | None:
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200 and len(resp.content) > 1000:
            return resp.content
    except requests.RequestException:
        pass
    return None


# ------------------------------------------------------------------ #
#  IGDB                                                                #
# ------------------------------------------------------------------ #

def get_igdb_token(client_id: str, client_secret: str) -> str | None:
    """Obtient un token d'accès IGDB via Twitch OAuth."""
    try:
        resp = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id":     client_id,
                "client_secret": client_secret,
                "grant_type":    "client_credentials",
            },
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
    except requests.RequestException:
        pass
    return None


def fetch_igdb_data(
    title: str,
    client_id: str,
    access_token: str
) -> dict | None:
    if not client_id or not access_token or not title:
        return None

    clean = _clean_search_title(title)
    if not clean:
        return None

    headers = {
        "Client-ID":     client_id,
        "Authorization": f"Bearer {access_token}",
    }

    try:
        resp = requests.post(
            "https://api.igdb.com/v4/games",
            headers=headers,
            data=(
                f'search "{clean}"; '
                f'fields name,summary,first_release_date,'
                f'genres.name,'
                f'involved_companies.company.name,'
                f'involved_companies.developer,'
                f'involved_companies.publisher,'
                f'cover.url,'
                f'screenshots.url,'
                f'videos.video_id,'
                f'rating,'
                f'platforms.name; '
                f'limit 5;'
            ),
            timeout=10
        )
        if resp.status_code != 200 or not resp.json():
            return None

        results = resp.json()
        game    = None
        for r in results:
            platforms = [p.get("name", "") for p in r.get("platforms", [])]
            if any("PlayStation 4" in p for p in platforms):
                game = r
                break
        if not game:
            game = results[0]

        genres = [g["name"] for g in game.get("genres", [])]

        developer = ""
        publisher = ""
        for ic in game.get("involved_companies", []):
            company = ic.get("company", {})
            name    = company.get("name", "")
            if ic.get("developer") and not developer:
                developer = name
            if ic.get("publisher") and not publisher:
                publisher = name

        cover_url = ""
        if game.get("cover"):
            cover_url = "https:" + game["cover"]["url"].replace(
                "t_thumb", "t_cover_big"
            )

        screenshot_urls = []
        for s in game.get("screenshots", [])[:6]:
            url = "https:" + s["url"].replace("t_thumb", "t_screenshot_big")
            screenshot_urls.append(url)

        rating = round(game.get("rating", 0) / 20, 1)

        release_ts   = game.get("first_release_date", 0)
        release_date = ""
        if release_ts:
            from datetime import datetime
            release_date = datetime.fromtimestamp(release_ts).strftime("%Y-%m-%d")

        return {
            "title_api":       game.get("name", ""),
            "description":     game.get("summary", ""),
            "developer":       developer,
            "publisher":       publisher,
            "release_date":    release_date,
            "genres":          genres,
            "rating":          rating,
            "cover_url":       cover_url,
            "screenshot_urls": screenshot_urls,
            "source":          "IGDB",
        }

    except (requests.RequestException, KeyError, ValueError, IndexError):
        return None


# ------------------------------------------------------------------ #
#  Thread API asynchrone                                               #
# ------------------------------------------------------------------ #

class ApiWorkerThread(QThread):
    """
    Récupère les données IGDB pour les jeux BASE uniquement,
    puis propage les infos (description, genres, jaquette) aux DLC liés.

    Signaux :
        game_updated(content_id, api_data)
        cover_ready(content_id, cover_path)
        progress(current, total)
        finished_all()
        status_message(text)
    """

    game_updated   = pyqtSignal(str, dict)
    cover_ready    = pyqtSignal(str, str)
    progress       = pyqtSignal(int, int)
    finished_all   = pyqtSignal()
    status_message = pyqtSignal(str)

    def __init__(
        self,
        games: list[dict],
        igdb_client_id: str = "",
        igdb_client_secret: str = "",
        parent=None
    ):
        super().__init__(parent)
        self._games              = games
        self._igdb_client_id     = igdb_client_id
        self._igdb_client_secret = igdb_client_secret
        self._running            = True
        self._igdb_token         = None

    def run(self):
        # Obtient le token IGDB
        if self._igdb_client_id and self._igdb_client_secret:
            self._igdb_token = get_igdb_token(
                self._igdb_client_id,
                self._igdb_client_secret
            )

        if not self._igdb_token:
            self.status_message.emit("❌ Token IGDB invalide")
            self.finished_all.emit()
            return

        # Sépare les jeux BASE/BACKPORT des DLC/UPDATE
        base_games = [
            g for g in self._games
            if g.get("type") == "game"
        ]
        total = len(base_games)

        # Cache des données récupérées par content_id BASE
        # pour propager aux DLC après
        fetched_base: dict[str, dict] = {}

        for i, game in enumerate(base_games):
            if not self._running:
                break

            self.progress.emit(i + 1, total)

            content_id = game.get("content_id", "")
            title      = game.get("title_api") or game.get("title", "")

            if not content_id or content_id == "UNKNOWN":
                continue

            self.status_message.emit(f"IGDB : {title[:40]}…")

            api_data   = {}
            cover_path = None

            # 1. Cache jaquette existant
            cached = get_cached_cover(content_id)
            if cached:
                cover_path = str(cached.resolve())
                self.cover_ready.emit(content_id, cover_path)

            # 2. Appel IGDB
            igdb = fetch_igdb_data(
                title,
                self._igdb_client_id,
                self._igdb_token
            )

            if igdb:
                api_data = igdb

                # Télécharge la cover IGDB
                if not cover_path and igdb.get("cover_url"):
                    img_bytes = _download_image(igdb["cover_url"])
                    if img_bytes:
                        saved      = save_cover(content_id, img_bytes, ".jpg")
                        cover_path = str(saved.resolve())
                        self.cover_ready.emit(content_id, cover_path)

                # Télécharge les screenshots
                local_screens = []
                for j, url in enumerate(igdb.get("screenshot_urls", [])[:4]):
                    cached_s = get_cached_screenshot(content_id, j)
                    if cached_s:
                        local_screens.append(str(cached_s.resolve()))
                    else:
                        img = _download_image(url)
                        if img:
                            saved = save_screenshot(content_id, j, img)
                            local_screens.append(str(saved.resolve()))
                    time.sleep(0.2)

                api_data["screenshots"] = local_screens

            if api_data:
                self.game_updated.emit(content_id, api_data)
                fetched_base[content_id] = {
                    "api_data":   api_data,
                    "cover_path": cover_path,
                }

            time.sleep(API_DELAY)

        # ── Propagation aux DLC liés ─────────────────────────────
        if fetched_base and self._running:
            self._propagate_to_dlc(fetched_base)

        self.status_message.emit("✅ Données IGDB récupérées")
        self.finished_all.emit()

    def _propagate_to_dlc(self, fetched_base: dict):
        """
        Propage jaquette, description et genres du jeu BASE
        vers tous ses DLC liés qui n'ont pas encore de données API.

        Utilise le CUSA commun entre le content_id BASE et le DLC
        pour faire le lien sans accès à la base de données.
        """
        # Index CUSA → données BASE
        cusa_to_base: dict[str, dict] = {}
        for base_cid, data in fetched_base.items():
            cusa = self._extract_cusa(base_cid)
            if cusa:
                cusa_to_base[cusa] = {**data, "base_content_id": base_cid}

        if not cusa_to_base:
            return

        # DLC et updates dans la liste originale
        related_games = [
            g for g in self._games
            if g.get("type") == "dlc"
            and not g.get("api_fetched")
        ]

        propagated = 0
        for dlc in related_games:
            if not self._running:
                break

            dlc_cid = dlc.get("content_id", "")
            cusa    = self._extract_cusa(dlc_cid)
            if not cusa or cusa not in cusa_to_base:
                continue

            base_data  = cusa_to_base[cusa]
            api_data   = base_data["api_data"]
            cover_path = base_data["cover_path"]

            # Données héritées — on garde le titre du DLC
            inherited = {
                "title_api":    dlc.get("title_api") or dlc.get("title", ""),
                "description":  api_data.get("description", ""),
                "developer":    api_data.get("developer", ""),
                "publisher":    api_data.get("publisher", ""),
                "release_date": api_data.get("release_date", ""),
                "genres":       api_data.get("genres", []),
                "rating":       api_data.get("rating", 0),
                "screenshots":  [],   # pas de screenshots pour les DLC
                "video_url":    "",
                "source":       "inherited",
            }

            self.game_updated.emit(dlc_cid, inherited)

            # Partage la même jaquette que le jeu BASE
            if cover_path:
                self.cover_ready.emit(dlc_cid, cover_path)

            propagated += 1

        if propagated:
            self.status_message.emit(
                f"✅ {propagated} DLC/Update mis à jour depuis le jeu BASE"
            )

    @staticmethod
    def _extract_cusa(content_id: str) -> str:
        """Extrait le code CUSA depuis un content_id."""
        for part in content_id.replace("-", "_").split("_"):
            if part.startswith(("CUSA", "CUSE")):
                return part
        return ""

    def stop(self):
        self._running = False