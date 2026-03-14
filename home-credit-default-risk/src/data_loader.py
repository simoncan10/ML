"""
Portable data loader for Home Credit Default Risk notebooks.

Works identically whether running:
  - Locally on Windows/Mac/Linux
  - On Binder
  - On Google Colab

Data is downloaded automatically from Kaggle if not already present.
Kaggle credentials must be available via one of:
  - Environment variables: KAGGLE_USERNAME and KAGGLE_KEY
  - A kaggle.json file at ~/.kaggle/kaggle.json
"""

from pathlib import Path


def get_repo_root() -> Path:
    """Walk up from cwd until we find .git or _quarto.yml."""
    for path in [Path.cwd(), *Path.cwd().parents]:
        if (path / ".git").exists() or (path / "_quarto.yml").exists():
            return path
    # Fallback: this file lives at <root>/home-credit-default-risk/src/data_loader.py
    return Path(__file__).resolve().parent.parent.parent


REPO_ROOT     = get_repo_root()
PROJECT_DIR   = REPO_ROOT / "home-credit-default-risk"
RAW_DIR       = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

COMPETITION = "home-credit-default-risk"


def ensure_data() -> None:
    """Download competition data from Kaggle if the raw CSVs are missing."""
    if RAW_DIR.exists() and any(RAW_DIR.glob("*.csv")):
        print(f"Data found at: {RAW_DIR}")
        return

    print("Data not found locally — downloading from Kaggle...")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import kaggle
        kaggle.api.authenticate()
        kaggle.api.competition_download_files(
            COMPETITION, path=RAW_DIR, quiet=False
        )
    except Exception as exc:
        raise RuntimeError(
            f"Kaggle download failed: {exc}\n\n"
            "To fix this, provide your Kaggle credentials in one of two ways:\n"
            "  Option 1 — Environment variables:\n"
            "    KAGGLE_USERNAME=<your_username>\n"
            "    KAGGLE_KEY=<your_api_key>\n"
            "  Option 2 — Place kaggle.json in ~/.kaggle/\n\n"
            "Get your API key at: https://www.kaggle.com/settings (Account → API)"
        ) from exc

    import zipfile
    for zf in RAW_DIR.glob("*.zip"):
        print(f"Extracting {zf.name}...")
        with zipfile.ZipFile(zf) as z:
            z.extractall(RAW_DIR)
        zf.unlink()

    print("Download complete.")
