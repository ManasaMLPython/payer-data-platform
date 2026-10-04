"""Gzip the in-scope CMS source files into one folder per feed, ready for upload."""
import gzip
import shutil
from pathlib import Path

# scripts/ -> payer-data-platform/ -> dbt-snowflake-end-to-end-project/
PROJECT_DIR = Path(__file__).resolve().parents[2]
SOURCE = PROJECT_DIR / "cms_raw_source"
TARGET = PROJECT_DIR / "cms_sample_gz"

# feed name -> source files (relative to SOURCE)
FEEDS = {
    "claims_professional": ["ffs_claims/carrier.csv"],
    "claims_inpatient": ["ffs_claims/inpatient.csv"],
    "claims_outpatient": ["ffs_claims/outpatient.csv"],
    "pharmacy": ["pde/pde.csv"],
    "eligibility": [f"beneficiary/beneficiary_{year}.csv" for year in range(2015, 2026)],
}


def compress(src: Path, dst: Path) -> None:
    """Write a gzip copy of src to dst, reading in chunks so big files don't fill memory."""
    with src.open("rb") as fin, gzip.open(dst, "wb", compresslevel=6) as fout:
        shutil.copyfileobj(fin, fout, length=16 * 1024 * 1024)


def main() -> None:
    for feed, files in FEEDS.items():
        out_dir = TARGET / feed
        out_dir.mkdir(parents=True, exist_ok=True)
        for rel in files:
            src = SOURCE / rel
            dst = out_dir / (src.name + ".gz")
            if not src.exists():
                print(f"MISSING  {src}")
                continue
            if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                print(f"SKIP     {dst.name} (already compressed)")
                continue
            compress(src, dst)
            before = src.stat().st_size / 1024 / 1024
            after = dst.stat().st_size / 1024 / 1024
            print(f"OK       {feed}/{dst.name}: {before:,.1f} MB -> {after:,.1f} MB ({before / after:.1f}x)")


if __name__ == "__main__":
    main()