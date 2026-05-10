import os

from webapp import app
from models import User, db


def bootstrap_database():
    with app.app_context():
        db.create_all()

        username = os.environ.get("SUPERADMIN_USERNAME", "superadmin")
        email = os.environ.get("SUPERADMIN_EMAIL", "superadmin@transport.local")
        password = os.environ.get("SUPERADMIN_PASSWORD", "SuperAdmin@123")

        superadmin = User.query.filter_by(username=username).first()
        if not superadmin:
            superadmin = User(
                username=username,
                email=email,
                full_name="System Superadmin",
                role="superadmin",
                is_active=True,
            )
            db.session.add(superadmin)
        else:
            superadmin.email = email
            superadmin.full_name = superadmin.full_name or "System Superadmin"
            superadmin.role = "superadmin"
            superadmin.is_active = True

        superadmin.tenant_id = None
        superadmin.set_password(password)
        db.session.commit()


if os.environ.get("BOOTSTRAP_DATABASE", "true").lower() == "true":
    bootstrap_database()

application = app

if __name__ == "__main__":
    app.run()
