from flask import Flask
from routes.auth_routes import auth_bp
from routes.content_routes import content_bp

app = Flask(__name__)

# Secret key for session management and flashing messages
app.secret_key = "super_secret_oldman_key_change_this"

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)

if __name__ == "__main__":
    app.run(debug=True)