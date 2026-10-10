import importlib.util
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('compose', ROOT / 'scripts' / 'compose_collage.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CompositionTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / 'assets/examples/original.png').exists(), 'Local photo fixture only')
    def test_real_photo_pixels_and_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'paired.png'
            src = ROOT / 'assets/examples/original.png'
            module.compose(ROOT / 'assets/examples/artwork.png', dest, src)
            with Image.open(src) as photo, Image.open(dest) as result:
                expected = ImageOps.exif_transpose(photo).convert('RGB')
                self.assertEqual(result.size, (expected.width, expected.height * 2))
                self.assertEqual(result.crop((0, 0, expected.width, expected.height)).tobytes(), expected.tobytes())

    @unittest.skipUnless((ROOT / 'assets/examples/artwork.png').exists(), 'Local artwork fixture only')
    def test_artwork_only_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = ROOT / 'assets/examples/artwork.png'
            dest = Path(tmp) / 'ai-only.png'
            module.compose(src, dest, mode='artwork-only')
            self.assertEqual(dest.read_bytes(), src.read_bytes())

    def test_aspect_ratio_mismatch_complete_artwork(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            photo, art, dest = (folder / name for name in ['photo.png', 'art.png', 'paired.png'])
            Image.new('RGB', (100, 60), 'blue').save(photo)
            Image.new('RGB', (20, 60), 'red').save(art)
            module.compose(art, dest, photo)
            with Image.open(dest) as result:
                self.assertEqual(result.getpixel((39, 90)), module.PAPER)
                self.assertEqual(result.getpixel((40, 60)), (255, 0, 0))
                self.assertEqual(result.getpixel((59, 119)), (255, 0, 0))
                self.assertEqual(result.getpixel((60, 90)), module.PAPER)

    def test_exif_orientation_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            photo, art, dest = (folder / name for name in ['photo.jpg', 'art.png', 'paired.png'])
            source = Image.new('RGB', (20, 10), 'green')
            exif = source.getexif(); exif[274] = 6
            source.save(photo, exif=exif)
            Image.new('RGB', (10, 20), 'red').save(art)
            module.compose(art, dest, photo)
            with Image.open(photo) as original, Image.open(dest) as result:
                expected = ImageOps.exif_transpose(original).convert('RGB')
                self.assertEqual(result.size, (10, 40))
                self.assertEqual(result.crop((0, 0, 10, 20)).tobytes(), expected.tobytes())

    def test_existing_output_and_wrong_extension_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            src = folder / 'artwork.png'
            Image.new('RGB', (20, 20), 'red').save(src)
            dest = folder / 'existing.png'
            dest.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):
                module.compose(src, dest, mode='artwork-only')
            self.assertEqual(dest.read_bytes(), b'keep')
            with self.assertRaises(ValueError):
                module.compose(src, folder / 'wrong.jpg', mode='artwork-only')
            self.assertFalse((folder / 'wrong.jpg').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
