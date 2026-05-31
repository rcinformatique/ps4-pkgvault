import re
import time
import requests
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from core.cover_loader import (
    save_cover, save_screenshot,
    get_cached_cover, get_cached_screenshot,
    COVERS_DIR, SCREENSHOTS_DIR
)


API_DELAY = 0.5  # secondes entre les requêtes


# ------------------------------------------------------------------ #
#  Utilitaires                                                        #
# ------------------------------------------------------------------ #

def _clean_search_title(title: str) -> str:
    """Nettoie le titre pour la recherche API."""
    title = re.sub(r'\bv\d+\.\d+\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\bPS[45]\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'—.*$', '', title)
    title = re.sub(r'-.*update.*$', '', title, flags=re.IGNORECASE)
    return title.strip()


def _strip_html(html: str) -> str:
    """Retire les balises HTML."""
    text = re.sub(r'<br\s*/?>', '\n', html)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;',  '&')
    text = text.replace('&lt;',   '<')
    text = text.replace('&gt;',   '>')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&#39;',  "'")
    text = text.replace('&quot;', '"')
    return text.strip()


def _download_image(url: str, timeout: int = 10) -> bytes | None:
    """Télécharge une image depuis une URL."""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200 and len(resp.content) > 1000:
            return resp.content
    except requests.RequestException:
        pass
    return None


# ------------------------------------------------------------------ #
#  RAWG.io                                                            #
# ------------------------------------------------------------------ #

def fetch_rawg_data(title: str, api_key: str) -> dict | None:
    """
    Cherche un jeu sur RAWG.io et retourne ses métadonnées.
    Retourne None si rien trouvé ou erreur.
    """
    if not api_key or not title:
        return None

    clean = _clean_search_title(title)
    if not clean:
        return None

    try:
        # Recherche
        resp = requests.get(
            "https://api.rawg.io/api/games",
            params={
                "key":       api_key,
                "search":    clean,
                "page_size": 5,
            },
            timeout=10
        )
        if resp.status_code != 200:
            return None

        results = resp.json().get("results", [])
        if not results:
            return None

        game    = results[0]
        game_id = game.get("id")

        time.sleep(API_DELAY)

        # Détail complet
        detail_resp = requests.get(
            f"https://api.rawg.io/api/games/{game_id}",
            params={"key": api_key},
            timeout=10
        )
        if detail_resp.status_code != 200:
            return None

        detail = detail_resp.json()

        # Genres
        genres = [g["name"] for g in detail.get("genres", [])]

        # Dev / Publisher
        developers = [d["name"] for d in detail.get("developers", [])]
        publishers = [p["name"] for p in detail.get("publishers", [])]

        # Description
        description = _strip_html(detail.get("description", ""))

        # Screenshots
        time.sleep(API_DELAY)
        screens_resp = requests.get(
            f"https://api.rawg.io/api/games/{game_id}/screenshots",
            params={"key": api_key},
            timeout=10
        )
        screenshot_urls = []
        if screens_resp.status_code == 200:
            screenshot_urls = [
                s["image"]
                for s in screens_resp.json().get("results", [])[:6]
            ]

        # Cover URL
        cover_url = detail.get("background_image", "")

        # Video
        clip = detail.get("clip", {})
        video_url = clip.get("clip", "") if clip else ""

        return {
            "title_api":    detail.get("name", ""),
            "description":  description,
            "developer":    ", ".join(developers),
            "publisher":    ", ".join(publishers),
            "release_date": detail.get("released", ""),
            "genres":       genres,
            "rating":       detail.get("rating", 0),
            "cover_url":    cover_url,
            "screenshot_urls": screenshot_urls,
            "video_url":    video_url,
        }

    except (requests.RequestException, KeyError, ValueError):
        return None


# ------------------------------------------------------------------ #
#  IGDB (Twitch)                                                      #
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
    """
    Cherche un jeu sur IGDB et retourne ses métadonnées.
    """
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
            data=f'search "{clean}"; fields name,summary,first_release_date,genres.name,involved_companies.company.name,involved_companies.developer,involved_companies.publisher,cover.url,screenshots.url,videos.video_id,rating; limit 5;',
            timeout=10
        )
        if resp.status_code != 200 or not resp.json():
            return None

        game = resp.json()[0]

        # Genres
        genres = [g["name"] for g in game.get("genres", [])]

        # Dev / Publisher
        developer = ""
        publisher = ""
        for ic in game.get("involved_companies", []):
            company = ic.get("company", {})
            name    = company.get("name", "")
            if ic.get("developer") and not developer:
                developer = name
            if ic.get("publisher") and not publisher:
                publisher = name

        # Cover
        cover_url = ""
        if game.get("cover"):
            cover_url = "https:" + game["cover"]["url"].replace(
                "t_thumb", "t_cover_big"
            )

        # Screenshots
        screenshot_urls = []
        for s in game.get("screenshots", [])[:6]:
            url = "https:" + s["url"].replace("t_thumb", "t_screenshot_big")
            screenshot_urls.append(url)

        # Video YouTube
        video_url = ""
        if game.get("videos"):
            vid_id    = game["videos"][0].get("video_id", "")
            video_url = f"https://www.youtube.com/watch?v={vid_id}" if vid_id else ""

        # Rating IGDB (sur 100 → sur 5)
        rating = round(game.get("rating", 0) / 20, 1)

        # Date
        release_ts = game.get("first_release_date", 0)
        release_date = ""
        if release_ts:
            from datetime import datetime
            release_date = datetime.fromtimestamp(release_ts).strftime("%d %B %Y")

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
            "video_url":       video_url,
        }

    except (requests.RequestException, KeyError, ValueError, IndexError):
        return None


# ------------------------------------------------------------------ #
#  Thread API asynchrone                                              #
# ------------------------------------------------------------------ #

class ApiWorkerThread(QThread):
    """
    Récupère les données API pour les jeux non encore traités.

    Signaux :
        game_updated(content_id, api_data)  → données API reçues
        cover_ready(content_id, cover_path) → jaquette téléchargée
        progress(current, total)            → avancement
        finished_all()                      → tout terminé
        status_message(text)                → message de statut
    """

    game_updated   = pyqtSignal(str, dict)
    cover_ready    = pyqtSignal(str, str)
    progress       = pyqtSignal(int, int)
    finished_all   = pyqtSignal()
    status_message = pyqtSignal(str)

    def __init__(
        self,
        games: list[dict],
        rawg_api_key: str = "",
        igdb_client_id: str = "",
        igdb_client_secret: str = "",
        parent=None
    ):
        super().__init__(parent)
        self._games              = games
        self._rawg_key           = rawg_api_key
        self._igdb_client_id     = igdb_client_id
        self._igdb_client_secret = igdb_client_secret
        self._running            = True
        self._igdb_token         = None

    def run(self):
        # Obtient le token IGDB si configuré
        if self._igdb_client_id and self._igdb_client_secret:
            self._igdb_token = get_igdb_token(
                self._igdb_client_id,
                self._igdb_client_secret
            )

        total = len(self._games)

        for i, game in enumerate(self._games):
            if not self._running:
                break

            self.progress.emit(i + 1, total)

            content_id = game.get("content_id", "")
            title      = game.get("title_api") or game.get("title", "")
            pkg_type   = game.get("type", "game")

            if not content_id or content_id == "UNKNOWN":
                continue

            # Uniquement les jeux BASE pour l'API
            if pkg_type not in ("game", "backport"):
                continue

            self.status_message.emit(
                f"API : {title[:40]}…"
            )

            api_data   = {}
            cover_path = None

            # 1. Cache jaquette existant
            cached = get_cached_cover(content_id)
            if cached:
                cover_path = str(cached)
                self.cover_ready.emit(content_id, cover_path)

            # 2. Essaie RAWG
            if self._rawg_key:
                rawg = fetch_rawg_data(title, self._rawg_key)
                if rawg:
                    api_data = rawg

                    # Télécharge la jaquette RAWG
                    if not cover_path and rawg.get("cover_url"):
                        img_bytes = _download_image(rawg["cover_url"])
                        if img_bytes:
                            saved      = save_cover(content_id, img_bytes, ".jpg")
                            cover_path = str(saved)
                            self.cover_ready.emit(content_id, cover_path)

                    # Télécharge les screenshots
                    local_screens = []
                    for j, url in enumerate(rawg.get("screenshot_urls", [])[:4]):
                        cached_s = get_cached_screenshot(content_id, j)
                        if cached_s:
                            local_screens.append(str(cached_s))
                        else:
                            img = _download_image(url)
                            if img:
                                saved = save_screenshot(content_id, j, img)
                                local_screens.append(str(saved))
                        time.sleep(0.2)

                    api_data["screenshots"] = local_screens

                time.sleep(API_DELAY)

            # 3. Fallback IGDB si RAWG n'a rien donné
            if not api_data and self._igdb_token:
                igdb = fetch_igdb_data(
                    title,
                    self._igdb_client_id,
                    self._igdb_token
                )
                if igdb:
                    api_data = igdb

                    if not cover_path and igdb.get("cover_url"):
                        img_bytes = _download_image(igdb["cover_url"])
                        if img_bytes:
                            saved      = save_cover(content_id, img_bytes, ".jpg")
                            cover_path = str(saved)
                            self.cover_ready.emit(content_id, cover_path)

                    local_screens = []
                    for j, url in enumerate(igdb.get("screenshot_urls", [])[:4]):
                        cached_s = get_cached_screenshot(content_id, j)
                        if cached_s:
                            local_screens.append(str(cached_s))
                        else:
                            img = _download_image(url)
                            if img:
                                saved = save_screenshot(content_id, j, img)
                                local_screens.append(str(saved))
                        time.sleep(0.2)

                    api_data["screenshots"] = local_screens

                time.sleep(API_DELAY)

            if api_data:
                self.game_updated.emit(content_id, api_data)

        self.status_message.emit("Données API récupérées")
        self.finished_all.emit()

    def stop(self):
        self._running = False