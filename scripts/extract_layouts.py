"""Write each in-scope CMS file's column layout to docs/contracts/source_layouts/
and check that all beneficiary years share the same columns."""
import csv
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
SOURCE = REPO_DIR.parent / "cms_raw_source"
OUT = REPO_DIR / "docs" / "contracts" / "source_layouts"

FILES = {
    "claims_professional": "ffs_claims/carrier.csv",
    "claims_inpatient": "ffs_claims/inpatient.csv",
    "claims_outpatient": "ffs_claims/outpatient.csv",
    "pharmacy": "pde/pde.csv",
    "eligibility": "beneficiary/beneficiary_2025.csv",
}


def read_header_and_first_row(path: Path):
    """Return (delimiter, column names, first data row) without reading the whole file."""
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        header_line = f.readline()
        first_line = f.readline()
    delim = "|" if header_line.count("|") > header_line.count(",") else ","
    columns = next(csv.reader([header_line], delimiter=delim))
    first_row = next(csv.reader([first_line], delimiter=delim), [])
    return delim, columns, first_row


def write_layouts() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for feed, rel in FILES.items():
        delim, columns, row = read_header_and_first_row(SOURCE / rel)
        lines = [f"# {feed} <- {rel}",
                 f"# delimiter: '{delim}'   columns: {len(columns)}",
                 "",
                 "pos | column | sample value (first row)"]
        for i, col in enumerate(columns):
            value = row[i] if i < len(row) else ""
            lines.append(f"{i + 1:>3} | {col} | {value}")
        (OUT / f"{feed}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{feed:<20} {len(columns):>4} columns  delimiter '{delim}'")


def compare_beneficiary_years() -> None:
    files = sorted((SOURCE / "beneficiary").glob("beneficiary_*.csv"))
    _, baseline, _ = read_header_and_first_row(files[0])
    print(f"\nBeneficiary header check (baseline {files[0].name}, {len(baseline)} columns):")
    for path in files[1:]:
        _, cols, _ = read_header_and_first_row(path)
        added = [c for c in cols if c not in baseline]
        removed = [c for c in baseline if c not in cols]
        status = "same" if cols == baseline else f"DIFFERENT  added={added} removed={removed}"
        print(f"  {path.name}: {status}")


if __name__ == "__main__":
    write_layouts()
    compare_beneficiary_years()