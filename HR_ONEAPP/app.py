from flask import Flask, redirect, url_for
from models import db
from routes import auth_bp, dashboard_bp, meeting_bp, attendance_bp, payroll_bp, task_bp, employee_bp, leave_bp
from scheduler import start_meeting_scheduler
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']                     = 'hr-oneapp-secret-2024'
    app.config['SQLALCHEMY_DATABASE_URI']         = 'sqlite:///hr_oneapp.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']  = False

    db.init_app(app)

    for bp in [auth_bp, dashboard_bp, meeting_bp, attendance_bp, payroll_bp, task_bp, employee_bp, leave_bp]:
        app.register_blueprint(bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()
        print("All tables ready.")

    # Flask's debug-mode reloader runs this factory in two processes (a
    # watcher + the actual worker). WERKZEUG_RUN_MAIN is only set in the
    # real worker, so this guard stops the scheduler thread from being
    # started twice under `flask run --debug` / `app.run(debug=True)`.
    # Outside debug mode (e.g. a production WSGI server) the var is unset,
    # so the scheduler still starts normally exactly once.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        start_meeting_scheduler(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
