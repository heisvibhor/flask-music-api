### Backend

At the top level files are organized as main, config and instances. These serve as configuration and instantiation of utilities.
Then comes the application which has a directory api_resources that contains all the resources for flask restful. These are called in api.py
Controllers contain user login time management using Redis, and endpoint for audio and image access
Delete File include function to delete files when mutated and Email include function for sending OTP email.
Login contains controllers for login requests, similarly signup provides controllers for OTP generation which can be used to verify in User Resource.
Tasks contains methods for celery and report generation.


### .env at the top
JWT_SECRET_KEY
EMAIL
PASSWORD
DOMAIN
SECRET_KEY


### Demo Video
https://drive.google.com/file/d/1e9ijzaoeh0FrYUm5xVkzOZ8kWig98Taw/view?usp=sharing

### Frontend 
https://github.com/heisvibhor/vibhorify

### Folders Required
audio -> containing audios required
image -> containing images required
intances contain sqlite database

### Technologies Used

Flask and Flask-RESTful for backend API
Vue-CLI for frontend development
Bootstrap and Bootstrap-Vue CSS
Flask-JWT for authentication
Vue-router, VueX for routing and state management
Celery and Redis for batch jobs
Python SMTP to send mails
Flask-Caching and Redis for caching
Pandas and Matplotlib to generate graphs
SQLalchemy as database engine
SQLite as database


### To run celery schedule and worker
```
celery -A main.celery_app beat
celery -A main.celery_app worker
```

### Config
Can be found in config.py file

### To run app
After install requirements in the env
```
python main.py
```