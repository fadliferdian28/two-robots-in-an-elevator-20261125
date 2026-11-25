import hashlib
import os
import shutil
import sys
from pathlib import Path

EXPECTED_SHA256 = "2fd95d5c02a39e255536189bac27de15db1e81f7565d3a8daccb8dbe3f21575d"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def main():
    source = Path(__file__).resolve().parent / "entry.txt"
    if not source.is_file():
        return fail(f"missing entry file: {source}")

    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        return fail(
            f"sha256 mismatch for {source}: expected {EXPECTED_SHA256}, got {digest}"
        )

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail(f"entry.txt is not valid UTF-8: {exc}")

    if not text.strip():
        return fail("entry.txt is whitespace-only")

    char_count = len(text)
    if not 1 <= char_count <= 200:
        return fail(f"entry.txt must be 1-200 characters, got {char_count}")

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail(f"could not create output directory {output_dir}: {exc}")

    if not os.access(output_dir, os.W_OK):
        return fail(f"output directory is not writable: {output_dir}")

    destination = output_dir / "entry.txt"

    if source.resolve() == destination.resolve():
        return fail("source and destination are the same file; refusing to copy")

    try:
        shutil.copyfile(source, destination)
    except shutil.SameFileError:
        return fail("source and destination are the same file; refusing to copy")
    except OSError as exc:
        return fail(f"could not copy entry.txt to {destination}: {exc}")

    print(f"characters: {char_count}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
