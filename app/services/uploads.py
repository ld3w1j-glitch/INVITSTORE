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

def profile_image_path(user_id):
    folder = Path(current_app.config['UPLOAD_FOLDER']) / 'profiles'
    return folder / f'{int(user_id)}.webp'

def profile_image_exists(user_id):
    return profile_image_path(user_id).is_file()

def save_profile_image(file, user_id):
    if not file or not file.filename:
        raise ValueError('Escolha uma foto para o perfil.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            im = Image.open(file.stream)
            if im.format not in {'JPEG', 'PNG', 'WEBP'}:
                raise ValueError('Use uma foto JPG, PNG ou WebP.')
            if im.width * im.height > 20000000:
                raise ValueError('A foto deve ter no máximo 20 megapixels.')
            im.load()
            im = ImageOps.exif_transpose(im).convert('RGB')
            im = ImageOps.fit(im, (640, 640), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            target = profile_image_path(user_id)
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(f'.{target.stem}-{uuid4().hex}.tmp.webp')
            try:
                im.save(temporary, 'WEBP', quality=90, method=4)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
            return target
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise ValueError('Não foi possível ler essa foto. Use JPG, PNG ou WebP de até 8 MB.')

def remove_profile_image(user_id):
    profile_image_path(user_id).unlink(missing_ok=True)

