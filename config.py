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
                "task-every-10-seconds": {
                    "task": "application.tasks.askLogin",
                    "schedule": crontab(minute=20, hour=20),
                },
                "task-every-10-10-seconds": {
                    "task": "application.tasks.send_monthly_report",
                    "schedule": 60,
                }
            },
    }
}