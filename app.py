from flask import Flask, redirect, session, url_for
import atexit

# Import logging configuration first
import config.logging_config

from blueprints.auth import auth_bp
from blueprints.monitor import monitor_bp
from services.scheduler import start_scheduler

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Secure this for production

@app.route('/')
def home():
    # If the user is authenticated, redirect to the monitor index page
    if session.get('authenticated'):
        return redirect(url_for('monitor.index'))
    # Otherwise, redirect to the login page
    return redirect(url_for('auth.login'))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(monitor_bp, url_prefix='/monitor')

# Start the scheduler
scheduler = start_scheduler()

# Optionally, perform an initial domain monitoring run on app start
# Uncomment the following lines if you want an initial run
# def initial_run():
#     perform_monitoring()
# initial_thread = threading.Thread(target=initial_run)
# initial_thread.start()

# Ensure the scheduler is stopped on shutdown
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)
