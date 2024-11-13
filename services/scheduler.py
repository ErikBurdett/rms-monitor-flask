from apscheduler.schedulers.background import BackgroundScheduler
from services.domain_checker import perform_monitoring

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=perform_monitoring, trigger="interval", hours=1, id='background_monitoring')
    scheduler.start()
    return scheduler
