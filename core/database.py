import sqlite3
import json
from pathlib import Path
from datetime import datetime


DB_PATH = Path("ps4pkgvault.db")


class Database:
    """
    Gère la persistance SQLite de PS4 PKGVault.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._conn   = None
        self._connect()
        self._migrate()

    # ------------------------------------------------------------------ #
    #  Connexion                                                           #
    # ------------------------------------------------------------------ #

    def _connect(self):
        self._conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

    def _migrate(self):
        """Crée ou met à jour les tables."""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS games (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id      TEXT UNIQUE NOT NULL,
                title           TEXT,
                title_api       TEXT,
                type            TEXT,
                category        TEXT,
                app_ver         TEXT,
                version         TEXT,
                firmware        TEXT,
                size_bytes      INTEGER DEFAULT 0,
                size_str        TEXT,
                filepath        TEXT,
                filename        TEXT,
                region          TEXT,
                languages       TEXT DEFAULT '[]',
                description     TEXT,
                developer       TEXT,
                publisher       TEXT,
                release_date    TEXT,
                genres          TEXT DEFAULT '[]',
                rating          REAL DEFAULT 0,
                cover_path      TEXT,
                screenshots     TEXT DEFAULT '[]',
                video_url       TEXT,
                api_fetched     INTEGER DEFAULT 0,
                date_added      TEXT,
                last_scanned    TEXT
            );

            CREATE TABLE IF NOT EXISTS game_relations (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                base_content_id TEXT NOT NULL,
                related_id      TEXT NOT NULL,
                relation_type   TEXT NOT NULL,
                UNIQUE(base_content_id, related_id)
            );

            CREATE TABLE IF NOT EXISTS folders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                path        TEXT UNIQUE NOT NULL,
                date_added  TEXT,
                enabled     INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS settings (
                key     TEXT PRIMARY KEY,
                value   TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_games_content_id
                ON games(content_id);
            CREATE INDEX IF NOT EXISTS idx_games_type
                ON games(type);
            CREATE INDEX IF NOT EXISTS idx_relations_base
                ON game_relations(base_content_id);
        """)
        self._conn.commit()

    # ------------------------------------------------------------------ #
    #  Games — écriture                                                    #
    # ------------------------------------------------------------------ #

    def upsert_game(self, pkg_data: dict) -> int:
        """Insère ou met à jour un jeu. Retourne l'id."""
        now = datetime.now().isoformat()

        languages   = json.dumps(pkg_data.get("languages",   []), ensure_ascii=False)
        genres      = json.dumps(pkg_data.get("genres",      []), ensure_ascii=False)
        screenshots = json.dumps(pkg_data.get("screenshots", []), ensure_ascii=False)

        cur = self._conn.execute("""
            INSERT INTO games (
                content_id, title, type, category,
                app_ver, version, firmware,
                size_bytes, size_str, filepath, filename,
                region, languages, genres, screenshots,
                date_added, last_scanned
            ) VALUES (
                :content_id, :title, :type, :category,
                :app_ver, :version, :firmware,
                :size_bytes, :size_str, :filepath, :filename,
                :region, :languages, :genres, :screenshots,
                :date_added, :last_scanned
            )
            ON CONFLICT(content_id) DO UPDATE SET
                title        = COALESCE(NULLIF(excluded.title, ''), games.title),
                type         = excluded.type,
                category     = excluded.category,
                app_ver      = excluded.app_ver,
                version      = excluded.version,
                firmware     = excluded.firmware,
                size_bytes   = excluded.size_bytes,
                size_str     = excluded.size_str,
                filepath     = excluded.filepath,
                filename     = excluded.filename,
                region       = excluded.region,
                languages    = excluded.languages,
                last_scanned = excluded.last_scanned
        """, {
            "content_id":  pkg_data.get("content_id", "UNKNOWN"),
            "title":       pkg_data.get("title", ""),
            "type":        pkg_data.get("type", "game"),
            "category":    pkg_data.get("category", ""),
            "app_ver":     pkg_data.get("app_ver", ""),
            "version":     pkg_data.get("version", ""),
            "firmware":    pkg_data.get("firmware", ""),
            "size_bytes":  pkg_data.get("size_bytes", 0),
            "size_str":    pkg_data.get("size_str", ""),
            "filepath":    pkg_data.get("filepath", ""),
            "filename":    pkg_data.get("filename", ""),
            "region":      pkg_data.get("region", ""),
            "languages":   languages,
            "genres":      genres,
            "screenshots": screenshots,
            "date_added":  now,
            "last_scanned": now,
        })
        self._conn.commit()
        return cur.lastrowid

    def update_api_data(self, content_id: str, api_data: dict):
        """Met à jour les infos récupérées via API."""
        genres      = json.dumps(api_data.get("genres",      []), ensure_ascii=False)
        screenshots = json.dumps(api_data.get("screenshots", []), ensure_ascii=False)

        self._conn.execute("""
            UPDATE games SET
                title_api    = :title_api,
                description  = :description,
                developer    = :developer,
                publisher    = :publisher,
                release_date = :release_date,
                genres       = :genres,
                rating       = :rating,
                screenshots  = :screenshots,
                video_url    = :video_url,
                api_fetched  = 1
            WHERE content_id = :content_id
        """, {
            "content_id":   content_id,
            "title_api":    api_data.get("title_api", ""),
            "description":  api_data.get("description", ""),
            "developer":    api_data.get("developer", ""),
            "publisher":    api_data.get("publisher", ""),
            "release_date": api_data.get("release_date", ""),
            "genres":       genres,
            "rating":       api_data.get("rating", 0),
            "screenshots":  screenshots,
            "video_url":    api_data.get("video_url", ""),
        })
        self._conn.commit()

    def update_cover(self, content_id: str, cover_path: str):
        """Met à jour le chemin de la jaquette."""
        self._conn.execute(
            "UPDATE games SET cover_path = ? WHERE content_id = ?",
            (cover_path, content_id)
        )
        self._conn.commit()

    def delete_game(self, content_id: str):
        """Supprime un jeu et ses relations."""
        self._conn.execute(
            "DELETE FROM game_relations WHERE base_content_id = ? OR related_id = ?",
            (content_id, content_id)
        )
        self._conn.execute(
            "DELETE FROM games WHERE content_id = ?",
            (content_id,)
        )
        self._conn.commit()

    def delete_by_filepath(self, filepath: str):
        """Supprime un jeu par son chemin de fichier."""
        cur = self._conn.execute(
            "SELECT content_id FROM games WHERE filepath = ?",
            (filepath,)
        )
        row = cur.fetchone()
        if row:
            self.delete_game(row["content_id"])

    # ------------------------------------------------------------------ #
    #  Games — lecture                                                     #
    # ------------------------------------------------------------------ #

    def get_all_games(self) -> list[dict]:
        """Retourne tous les jeux triés par titre."""
        cur = self._conn.execute(
            "SELECT * FROM games ORDER BY COALESCE(title_api, title)"
        )
        return [self._row_to_dict(r) for r in cur.fetchall()]

    def get_game(self, content_id: str) -> dict | None:
        """Retourne un jeu par son Content-ID."""
        cur = self._conn.execute(
            "SELECT * FROM games WHERE content_id = ?",
            (content_id,)
        )
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def get_game_by_filepath(self, filepath: str) -> dict | None:
        """Retourne un jeu par son chemin de fichier."""
        cur = self._conn.execute(
            "SELECT * FROM games WHERE filepath = ?",
            (filepath,)
        )
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def get_by_type(self, pkg_type: str) -> list[dict]:
        """Retourne les jeux filtrés par type."""
        cur = self._conn.execute(
            "SELECT * FROM games WHERE type = ? ORDER BY COALESCE(title_api, title)",
            (pkg_type,)
        )
        return [self._row_to_dict(r) for r in cur.fetchall()]

    def search(self, query: str) -> list[dict]:
        """Recherche dans le titre et le Content-ID."""
        pattern = f"%{query}%"
        cur = self._conn.execute("""
            SELECT * FROM games
            WHERE title      LIKE :q
               OR title_api  LIKE :q
               OR content_id LIKE :q
            ORDER BY COALESCE(title_api, title)
        """, {"q": pattern})
        return [self._row_to_dict(r) for r in cur.fetchall()]

    def get_unfetched(self) -> list[dict]:
        """Retourne les jeux dont l'API n'a pas encore été appelée."""
        cur = self._conn.execute(
            "SELECT * FROM games WHERE api_fetched = 0 AND type = 'game' ORDER BY date_added"
        )
        return [self._row_to_dict(r) for r in cur.fetchall()]

    def count_by_type(self) -> dict:
        """Retourne le nombre de jeux par type."""
        cur = self._conn.execute("""
            SELECT type, COUNT(*) as cnt
            FROM games GROUP BY type
        """)
        counts = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
        for row in cur.fetchall():
            if row["type"] in counts:
                counts[row["type"]] = row["cnt"]
        return counts

    def get_total_size(self) -> int:
        """Retourne la taille totale en bytes."""
        cur = self._conn.execute(
            "SELECT SUM(size_bytes) as total FROM games"
        )
        row = cur.fetchone()
        return row["total"] or 0

    # ------------------------------------------------------------------ #
    #  Relations                                                           #
    # ------------------------------------------------------------------ #

    def add_relation(
        self,
        base_content_id: str,
        related_id: str,
        relation_type: str
    ):
        """Crée un lien entre un jeu BASE et son DLC/UPDATE."""
        try:
            self._conn.execute("""
                INSERT OR IGNORE INTO game_relations
                    (base_content_id, related_id, relation_type)
                VALUES (?, ?, ?)
            """, (base_content_id, related_id, relation_type))
            self._conn.commit()
        except sqlite3.Error:
            pass

    def get_related(self, base_content_id: str) -> list[dict]:
        """Retourne les DLC et UPDATES liés à un jeu BASE."""
        cur = self._conn.execute("""
            SELECT g.*, r.relation_type
            FROM games g
            JOIN game_relations r ON g.content_id = r.related_id
            WHERE r.base_content_id = ?
            ORDER BY r.relation_type, COALESCE(g.title_api, g.title)
        """, (base_content_id,))
        return [self._row_to_dict(r) for r in cur.fetchall()]

    def get_base_game(self, content_id: str) -> dict | None:
        """
        Trouve le jeu BASE associé à un DLC ou UPDATE
        en comparant le CUSA extrait du content_id.
        """
        cusa = ""
        for part in content_id.replace("-", "_").split("_"):
            if part.startswith("CUSA") or part.startswith("CUSE"):
                cusa = part
                break

        if not cusa:
            return None

        cur = self._conn.execute("""
            SELECT * FROM games
            WHERE type = 'game'
              AND content_id LIKE ?
            LIMIT 1
        """, (f"%{cusa}%",))
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    # ------------------------------------------------------------------ #
    #  Dossiers                                                            #
    # ------------------------------------------------------------------ #

    def add_folder(self, path: str) -> bool:
        """Ajoute un dossier. Retourne False si déjà présent."""
        try:
            self._conn.execute("""
                INSERT INTO folders (path, date_added)
                VALUES (?, ?)
            """, (str(Path(path).resolve()), datetime.now().isoformat()))
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_folder(self, path: str):
        """Supprime un dossier."""
        self._conn.execute(
            "DELETE FROM folders WHERE path = ?",
            (str(Path(path).resolve()),)
        )
        self._conn.commit()

    def get_folders(self) -> list[str]:
        """Retourne la liste des dossiers actifs qui existent."""
        cur = self._conn.execute(
            "SELECT path FROM folders WHERE enabled = 1 ORDER BY date_added"
        )
        return [
            row["path"] for row in cur.fetchall()
            if Path(row["path"]).exists()
        ]

    def get_folders_full(self) -> list[dict]:
        """Retourne les dossiers avec leurs stats."""
        folders = self.get_folders()
        result  = []
        for path in folders:
            cur = self._conn.execute(
                "SELECT date_added FROM folders WHERE path = ?", (path,)
            )
            row        = cur.fetchone()
            date_added = row["date_added"] if row else ""

            counts = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
            total_bytes = 0
            cur2 = self._conn.execute(
                "SELECT type, size_bytes FROM games WHERE filepath LIKE ?",
                (f"{path}%",)
            )
            for r in cur2.fetchall():
                t = r["type"]
                if t in counts:
                    counts[t] += 1
                total_bytes += r["size_bytes"] or 0

            total = sum(counts.values())
            if total_bytes >= 1_073_741_824:
                size_str = f"{total_bytes / 1_073_741_824:.1f} Go"
            else:
                size_str = f"{total_bytes / 1_048_576:.0f} Mo"

            result.append({
                "path":       path,
                "total":      total,
                "game":       counts["game"],
                "dlc":        counts["dlc"],
                "update":     counts["update"],
                "backport":   counts["backport"],
                "size_str":   size_str,
                "date_added": date_added[:10] if date_added else "",
            })

        return result

    # ------------------------------------------------------------------ #
    #  Paramètres                                                          #
    # ------------------------------------------------------------------ #

    def get_setting(self, key: str, default: str = "") -> str:
        """Récupère un paramètre."""
        cur = self._conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        row = cur.fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        """Enregistre un paramètre."""
        self._conn.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        self._conn.commit()

    def get_all_settings(self) -> dict:
        """Retourne tous les paramètres."""
        cur = self._conn.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cur.fetchall()}

    # ------------------------------------------------------------------ #
    #  Utilitaires                                                         #
    # ------------------------------------------------------------------ #

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """Convertit une Row SQLite en dict avec JSON décodé."""
        if row is None:
            return {}
        d = dict(row)
        for key in ("languages", "genres", "screenshots"):
            if key in d and isinstance(d[key], str):
                try:
                    d[key] = json.loads(d[key])
                except (json.JSONDecodeError, TypeError):
                    d[key] = []
        return d

    def close(self):
        if self._conn:
            self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()