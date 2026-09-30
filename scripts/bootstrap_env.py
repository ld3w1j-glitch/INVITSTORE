"""Bootstrap de produção: cria o principal uma única vez, nunca redefine senha."""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.extensions import db
from app.models import User
from app.services import validation as v
from sqlalchemy import select

app = create_app()
with app.app_context():
    db.create_all()
    if not db.session.scalar(select(User.id).limit(1)):
        fields = ['ADMIN_NAME','ADMIN_EMAIL','ADMIN_WHATSAPP','ADMIN_PASSWORD']
        if any(not os.getenv(k) for k in fields):
            raise SystemExit('Primeira instalação: configure ADMIN_NAME, ADMIN_EMAIL, ADMIN_WHATSAPP e ADMIN_PASSWORD.')
        user = User(name=v.text(os.environ['ADMIN_NAME'], 'Nome', 90), email=v.email(os.environ['ADMIN_EMAIL']), whatsapp=v.phone(os.environ['ADMIN_WHATSAPP']), role='superadmin')
        user.set_password(v.password(os.environ['ADMIN_PASSWORD']))
        db.session.add(user); db.session.commit()
        print('Administrador principal criado.')
    print('Inicialização concluída.')
