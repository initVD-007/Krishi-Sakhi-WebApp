from flask import Flask
from config import Config
from .utils import init_db, populate_schedules, load_model, check_for_reminders
from apscheduler.schedulers.background import BackgroundScheduler
import logging

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    
    # Logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize DB (and create tables if needed)
    with app.app_context():
        init_db()
        populate_schedules()
        load_model() # Preload model

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    # Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_for_reminders, 'cron', hour=8)
    scheduler.start()
    
    return app
