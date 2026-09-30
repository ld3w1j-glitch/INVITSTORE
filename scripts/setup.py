"""Criação inicial interativa. Não recria senhas nem altera contas existentes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.extensions import db
from app.models import User
from sqlalchemy import select

app = create_app()
with app.app_context():
    db.create_all()
    first = db.session.scalar(select(User.id).limit(1))
if not first:
    # Invoke the same interactive command used by Flask, with a real app context.
    from flask.cli import ScriptInfo
    try:
        app.cli.main(args=['criar-admin'], prog_name='InvitStore', obj=ScriptInfo(create_app=lambda: app), standalone_mode=False)
    except Exception as exc:
        print(f'Não foi possível configurar: {exc}')
        sys.exit(1)
print('InvitStore pronta. Painel: http://127.0.0.1:5000/login')
