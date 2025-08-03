from app import create_app
from app.config.database import db
from app.models import User, Job, Note
import os
app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database initialized!")

@app.cli.command("create-migration")
def create_migration():
    """Create a new migration."""
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", "Auto-generated migration"])

@app.cli.command("run-migrations")
def run_migrations():
    """Run database migrations."""
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"])

if __name__ == '__main__':
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=os.getenv('PORT', 8000)) 