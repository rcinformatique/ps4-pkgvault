from pathlib import Path
from core.pkg_reader import read_pkg


def scan_folder(
    folder_path: str | Path,
    db=None,
    progress_callback=None,
) -> tuple[list[dict], list[str]]:
    folder_path = Path(folder_path)
    packages    = []
    errors      = []

    if not folder_path.exists() or not folder_path.is_dir():
        return packages, errors

    pkg_files = sorted(folder_path.rglob("*.pkg"))
    total     = len(pkg_files)
    print(f"PKG trouvés sur disque : {total}")

    for i, pkg_file in enumerate(pkg_files):
        if progress_callback:
            progress_callback(i + 1, total)

        print(f"Lecture : {pkg_file.name}")
        result = read_pkg(pkg_file)

        if result is not None:
            print(f"  ✅ OK — type: {result.get('type')} | title: {result.get('title')}")
            packages.append(result)
            if db:
                db.upsert_game(result)
                _auto_link_relations(result, db)
        else:
            print(f"  ❌ ECHEC — fichier ignoré")
            errors.append(str(pkg_file))

    print(f"Total scanné : {len(packages)} OK, {len(errors)} erreurs")
    return packages, errors


def _auto_link_relations(pkg_data: dict, db):
    """
    Tente de lier automatiquement un DLC ou UPDATE
    à son jeu BASE via le Content-ID court (CUSAXXXXX).
    """
    pkg_type   = pkg_data.get("type", "game")
    content_id = pkg_data.get("content_id", "")

    if pkg_type not in ("dlc", "update", "backport"):
        return
    if not content_id or content_id == "UNKNOWN":
        return

    base = db.get_base_game(content_id)
    if base:
        db.add_relation(
            base["content_id"],
            content_id,
            pkg_type
        )


def count_by_type(packages: list[dict]) -> dict:
    """Retourne le nombre de PKG par type depuis une liste."""
    counts = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
    for pkg in packages:
        pkg_type = pkg.get("type", "game")
        if pkg_type in counts:
            counts[pkg_type] += 1
    return counts


def format_total_size(packages: list[dict]) -> str:
    """Retourne la taille totale formatée."""
    total = sum(p.get("size_bytes", 0) for p in packages)
    if total >= 1_073_741_824:
        return f"{total / 1_073_741_824:.1f} Go"
    if total >= 1_048_576:
        return f"{total / 1_048_576:.1f} Mo"
    return f"{total / 1024:.1f} Ko"