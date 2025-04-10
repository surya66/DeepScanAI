from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Analyst

app = create_app()
cli = FlaskGroup(create_app=lambda: app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Database tables created")

@cli.command("seed_db")
def seed_db():
    # Create admin user
    admin = User(
        username="admin",
        email="admin@deepscan.ai",
        password="admin123",
        role="admin"
    )
    db.session.add(admin)
    
    # Create test client user
    client = User(
        username="testclient",
        email="client@example.com",
        password="client123",
        role="client"
    )
    db.session.add(client)
    
    # Create test analyst user
    analyst_user = User(
        username="testanalyst",
        email="analyst@example.com",
        password="analyst123",
        role="analyst"
    )
    db.session.add(analyst_user)
    db.session.commit()
    
    # Create analyst profile
    analyst = Analyst(
        user_id=analyst_user.id,
        expertise="web,api",
        availability=True,
        rating=4.5
    )
    db.session.add(analyst)
    db.session.commit()
    
    print("Database seeded with test data")

if __name__ == "__main__":
    cli()
