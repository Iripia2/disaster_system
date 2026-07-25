import sqlite3
from pathlib import Path
path = Path('db.sqlite3')
print('exists', path.exists())
if not path.exists():
    raise SystemExit(1)
conn = sqlite3.connect(path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print('tables:', sorted([row[0] for row in c.fetchall()]))
c.execute("SELECT app, name FROM django_migrations ORDER BY app, name;")
rows = c.fetchall()
print('migrations:')
for app, name in rows:
    print(app, name)
conn.close()
