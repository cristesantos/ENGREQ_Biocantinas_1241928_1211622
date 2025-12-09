"""
Script para criar utilizadores de teste
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from biocantinas.backend.app.db.session import SessionLocal, init_db
from biocantinas.backend.app.db.models import UserORM
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_utilizadores():
    init_db()
    session = SessionLocal()
    
    try:
        # Verificar utilizadores existentes
        existing = {u.username for u in session.query(UserORM).all()}
        print(f"\nUtilizadores existentes: {existing}")
        
        # Utilizadores de teste
        users = [
            ("gestor", "gestor123", "GESTOR"),
            ("produtor", "produtor123", "PRODUTOR"),
            ("gestor_cantina", "gestor123", "GESTOR_CANTINA"),
            ("dietista", "dietista123", "DIETISTA"),
        ]
        
        created = 0
        for username, password, role in users:
            if username not in existing:
                hashed = pwd_context.hash(password)
                user = UserORM(username=username, hashed_password=hashed, role=role)
                session.add(user)
                print(f"✓ Criado: {username} ({role})")
                created += 1
            else:
                print(f"✗ Já existe: {username}")
        
        if created > 0:
            session.commit()
            print(f"\n{created} utilizador(es) criado(s) com sucesso!")
        else:
            print("\nNenhum utilizador novo criado.")
            
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    criar_utilizadores()
