Backend database integration

1) Environment variables (see .env.example)
- DATABASE_URL: SQLAlchemy URL (e.g., sqlite:///./app.db, postgresql+psycopg2://user:pass@host:5432/dbname)
- SQL_ECHO: true|false to echo SQL statements
- SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM: JWT config
- BACKEND_CORS_ORIGINS: CORS origins (comma-separated)

2) Local development with SQLite
- Put DATABASE_URL=sqlite:///./app.db in .env
- First run will auto-create tables (Base.metadata.create_all)

3) Alembic migrations (optional now)
- alembic.ini and alembic/env.py included
- To initialize first migration (when ready):
  - pip install -r requirements.txt
  - alembic revision --autogenerate -m "init"
  - alembic upgrade head

4) Usage in routes
- Use: from src.core.database import get_db
- Inject: def endpoint(db: Session = Depends(get_db)): ...
- ORM models under src/models, schemas under src/schemas

5) Security helpers
- Password: hash via get_password_hash, verify with verify_password
- JWT: create_access_token(subject=...)
