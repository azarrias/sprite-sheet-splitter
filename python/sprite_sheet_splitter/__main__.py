"""Desktop entry point; imports the GUI only when actually launching it."""

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sprite sheet slicing and animation preview")
    parser.add_argument("image", nargs="?", help="PNG/TGA to open instead of the startup chooser")
    args = parser.parse_args(argv)
    from .app import run

    try:
        return run(args.image)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Sprite Sheet Splitter: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())