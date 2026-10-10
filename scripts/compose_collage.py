"""Compose a photo and generated artwork without redrawing the photo."""
import argparse
from pathlib import Path
import shutil

from PIL import Image, ImageOps


PAPER = (239, 230, 207)


def compose(artwork, output, original=None, mode="paired"):
    art_path, out_path = Path(artwork), Path(output)
    if mode not in {"paired", "artwork-only"}:
        raise ValueError("Unknown mode")
    if out_path.exists():
        raise FileExistsError(f"Output already exists: {out_path}")
    sources = [art_path] + ([Path(original)] if original is not None else [])
    if any(out_path.resolve() == source.resolve() for source in sources):
        raise ValueError("Output must not replace an input")
    if not art_path.is_file():
        raise FileNotFoundError(art_path)
    if mode == "artwork-only":
        if out_path.suffix.lower() != art_path.suffix.lower():
            raise ValueError("Artwork-only output extension must match the source")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("xb") as dest, art_path.open("rb") as source:
            shutil.copyfileobj(source, dest)
        return
    if original is None:
        raise ValueError("Paired mode needs --original")
    if out_path.suffix.lower() != ".png":
        raise ValueError("Paired output must be lossless PNG")
    with Image.open(original) as source:
        photo = ImageOps.exif_transpose(source).convert("RGB")
        profile = source.info.get("icc_profile")
    with Image.open(art_path) as source:
        art = ImageOps.exif_transpose(source).convert("RGBA")
    width, height = photo.size
    fitted = ImageOps.contain(art, (width, height), Image.Resampling.LANCZOS)
    result = Image.new("RGB", (width, height * 2), PAPER)
    result.paste(photo, (0, 0))
    result.paste(fitted, ((width - fitted.width) // 2,
                          height + (height - fitted.height) // 2), fitted)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("xb") as dest:
        result.save(dest, format="PNG", icc_profile=profile)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["paired", "artwork-only"], default="paired")
    parser.add_argument("--original", type=Path)
    parser.add_argument("--artwork", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        compose(args.artwork, args.output, args.original, args.mode)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
