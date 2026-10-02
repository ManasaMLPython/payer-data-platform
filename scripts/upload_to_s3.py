"""Upload a local file or folder to a payer-platform landing bucket."""
import argparse
import sys
from pathlib import Path

import boto3

BUCKET_PREFIX = "mb-payer-landing"
VALID_ENVS = ("dev", "test", "prod")


def bucket_for(env: str) -> str:
    """Build the bucket name from the environment and this AWS account's ID."""
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    return f"{BUCKET_PREFIX}-{env}-{account_id}"


def files_to_upload(source: Path) -> list[Path]:
    """Return the single file, or every file inside the folder."""
    if source.is_file():
        return [source]
    if source.is_dir():
        return sorted(p for p in source.rglob("*") if p.is_file())
    sys.exit(f"Source not found: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", required=True, choices=VALID_ENVS)
    parser.add_argument("--source", required=True, type=Path, help="Local file or folder")
    parser.add_argument("--prefix", required=True, help="S3 prefix, e.g. sample/claims_professional/")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded, upload nothing")
    parser.add_argument("--confirm-prod", action="store_true", help="Required for --env prod")
    args = parser.parse_args()

    if args.env == "prod" and not args.confirm_prod:
        sys.exit("Refusing to upload to PROD without --confirm-prod")

    prefix = args.prefix.strip("/") + "/"
    bucket = bucket_for(args.env)
    files = files_to_upload(args.source)
    base = args.source if args.source.is_dir() else args.source.parent

    s3 = boto3.client("s3")
    total_bytes = 0
    for path in files:
        key = prefix + path.relative_to(base).as_posix()
        size = path.stat().st_size
        total_bytes += size
        label = "[dry-run] " if args.dry_run else ""
        print(f"{label}{path} -> s3://{bucket}/{key} ({size / 1024 / 1024:,.1f} MB)")
        if not args.dry_run:
            s3.upload_file(str(path), bucket, key)

    verb = "would be uploaded" if args.dry_run else "uploaded"
    print(f"\n{len(files)} file(s), {total_bytes / 1024 / 1024:,.1f} MB {verb} to s3://{bucket}/{prefix}")


if __name__ == "__main__":
    main()