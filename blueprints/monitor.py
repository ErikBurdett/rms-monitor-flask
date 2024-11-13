from flask import Blueprint, json, render_template, session, redirect, url_for, flash, Response
from services.domain_checker import perform_monitoring, sse_monitor_domains, domain_statuses
import threading
from config.logging_config import logger
from queue import Empty

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('auth.login'))

    if domain_statuses:
        last_update = max(
            (status['last_checked'] for status in domain_statuses.values()),
            default=None
        )
    else:
        last_update = None

    return render_template('index.html', domains=domain_statuses, last_update=last_update)

@monitor_bp.route('/run_monitor', methods=['POST'])
def run_monitor():
    def run_monitoring():
        try:
            perform_monitoring()
            logger.info("Manual domain monitoring executed successfully.")
        except Exception as e:
            logger.error(f"Error during manual monitoring: {e}")

    # Start the monitoring in a separate thread
    monitoring_thread = threading.Thread(target=run_monitoring)
    monitoring_thread.start()

    flash('Domain monitoring has been started in the background.', 'success')
    return redirect(url_for('monitor.index'))

@monitor_bp.route('/domain_status_stream')
def domain_status_stream():
    # This endpoint streams the existing domain_statuses without initiating monitoring
    return Response(sse_monitor_domains(), mimetype='text/event-stream')
