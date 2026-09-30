import os
import secrets
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def settings():
    data = Path(os.getenv('DATA_DIR', str(BASE_DIR / 'instance'))).resolve()
    data.mkdir(parents=True, exist_ok=True)
    production = os.getenv('APP_ENV') == 'production'
    secret = os.getenv('SECRET_KEY', '').strip()
    if production and len(secret) < 32:
        raise RuntimeError('Defina SECRET_KEY com pelo menos 32 caracteres no ambiente de produção.')
    if not secret:
        secret_file = data / 'secret.key'
        if not secret_file.exists():
            try:
                with secret_file.open('x') as f:
                    f.write(secrets.token_hex(32))
                secret_file.chmod(0o600)
            except FileExistsError:
                pass
        secret = secret_file.read_text().strip()
    return dict(
        SECRET_KEY=secret,
        SQLALCHEMY_DATABASE_URI='sqlite:///' + str(data / 'invitstore.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'timeout': 20}},
        DATA_DIR=data,
        UPLOAD_FOLDER=data / 'uploads',
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=production,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        WTF_CSRF_TIME_LIMIT=12 * 60 * 60,
        PUBLIC_BASE_URL=os.getenv('PUBLIC_BASE_URL', '').rstrip('/'),
        TRUSTED_HOSTS=[v.strip() for v in os.getenv('TRUSTED_HOSTS', '').split(',') if v.strip()] or None,
    )
