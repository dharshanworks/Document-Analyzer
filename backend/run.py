import os

# Set Tesseract path for Render (Linux) before any imports
if os.path.exists('/usr/bin/tesseract'):
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

from app import create_app

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Create all database tables."""
    with app.app_context():
        from app.extensions import db
        db.create_all()
        print("Database tables created successfully.")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
