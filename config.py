from celery.schedules import crontab
config_object = {
    "DEBUG": True,         
    "CACHE_TYPE": "RedisCache", 
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_REDIS_HOST": "127.0.0.1",
    "CACHE_REDIS_PORT": 6379,
    "IMAGE_FOLDER":"..//image",
    "AUDIO_FOLDER":"..//audio",
    "SQLALCHEMY_DATABASE_URI":"sqlite:///proj.sqlite3",
    "JWT_ACCESS_TOKEN_EXPIRES": 84200,
    "CELERY": {
        "broker_url":"redis://localhost",
        "result_backend":"redis://localhost",
        "task_ignore_result":True,
         "beat_schedule": {
                "task-check_login": {
                    "task": "application.tasks.check_login",
                    "schedule": crontab(minute=5, hour=19),
                },
                "task-send_monthly_report": {
                    "task": "application.tasks.send_monthly_report",
                    "schedule": crontab(minute=57, hour=8, day_of_month='28'),
                }
            },
    }
}
