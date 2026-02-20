from app import create_app, db
from app.models import User
import bcrypt
import os

app = create_app()

def create_admin():
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(username='admin', email='admin@ortiflex.com', password=hashed_pw, role='Admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin / admin123")

if __name__ == '__main__':
    create_admin()
    # Para despliegue en la nube
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
