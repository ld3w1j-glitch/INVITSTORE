import warnings
from pathlib import Path
from uuid import uuid4
from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError

def save_image(file):
    if not file or not file.filename: return None
    # Decode and re-encode rather than trusting extension/MIME or preserving payloads.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            im = Image.open(file.stream)
            if im.format not in {'JPEG', 'PNG', 'WEBP'}: raise ValueError('Use imagens JPG, PNG ou WebP.')
            if im.width * im.height > 20000000: raise ValueError('A imagem deve ter no máximo 20 megapixels.')
            im.load()
            im = ImageOps.exif_transpose(im)
            im.thumbnail((1800, 1800))
            im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
            filename = uuid4().hex + '.webp'
            folder = Path(current_app.config['UPLOAD_FOLDER'])
            folder.mkdir(parents=True, exist_ok=True)
            im.save(folder / filename, 'WEBP', quality=88, method=4)
            return filename
    except (UnidentifiedImageError, OSError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise ValueError('Não foi possível ler essa imagem. Use JPG, PNG ou WebP de até 8 MB.')

def remove_image(filename):
    if filename and Path(filename).name == filename:
        (Path(current_app.config['UPLOAD_FOLDER']) / filename).unlink(missing_ok=True)
