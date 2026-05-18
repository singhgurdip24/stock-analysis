from apscheduler.schedulers.background import BackgroundScheduler
from services.evaluate_prediction import evaluate_all_predictions

scheduler = BackgroundScheduler()

scheduler.add_job(
    evaluate_all_predictions,
    'interval',
    hours=24
)
