from flask import Flask, render_template
from config import SECRET_KEY, DEBUG
from routes.utils import generate_csrf_token, validate_csrf_token, is_safe_url
from routes import main_bp, auth_bp, booking_bp, admin_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.jinja_env.globals['csrf_token'] = generate_csrf_token

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)


@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


if __name__ == '__main__':
    app.run(debug=DEBUG)