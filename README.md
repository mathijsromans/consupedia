# Consupedia 

Consupedia is based on a django project template at https://github.com/bartromgens/django-project-template.

These instrutions provide you with a working system where you can test consupedia yourself.

Requires Python 3.4+ and Django 1.10+

## Installation

### Linux
Get the code and enter the project directory,
```
$ git clone https://github.com/mathijsromans/consupedia.git
$ cd consupedia
```
Install dependencies that you will need
```
$ apt-get install virtualenv
```
or
```
$ pip install virtualenv
```
Run the install script (creates a Python 3 virtualenv with dependencies, a local_settings.py file, and a sqlite database),
```
$ ./install.sh
```

Activate the virtualenv (always do this before working on the project),
```
$ source env/bin/activate
```

### Windows

Install [git](https://git-scm.com/download/win) and [Python 3](https://www.python.org/downloads/windows/). 

Get the code and enter the project directory,
```
> git clone https://github.com/mathijsromans/consupedia.git
> cd consupedia
```
Run the install script (creates a Python 3 virtualenv with dependencies, a local_settings.py file, and a sqlite database),
```
> install.bat
```

Activate the virtualenv (always do this before working on the project),
```
> env\Scripts\activate.bat
```

### Create a superuser (optional)
This allows you to login at the website as superuser and view the admin page,
```
(env)$ python manage.py createsuperuser
```

### Run a developement webserver
Run the Django dev web server in the virtualenv (don't forget to active the virtualenv),
```
(env)$ python manage.py runserver
```

The website is now available at http://127.0.0.1:8000 and admin http://127.0.0.1:8000/admin.

## Configuration (optional)

### local_settings.py

The local settings are defined in `website/local_settings.py`. 
These are not under version control and you are free change these for your personal needs.
This is also the place for secret settings. An example, on which this file is based, is found in `website/local_settings_example.py`.

### Daily backups (cronjob)
This project has a django-cronjob that makes daily backups of the raw database (includes everything), and a json dump of the data.
These are defined in `website/cron.py`. The location of the backup files is defined in `website/local_settings.py`. 
Create the following cronjob (Linux) to kickstart the `django-cron` jobs,
```
$ crontab -e
*/5 * * * * source /home/<username>/.bashrc && source /home/<path-to-project>/env/bin/activate && python /home/<path-to-project>/website/manage.py runcrons > /home/<path-to-project>/log/cronjob.log
```

## Commands

Create recipes from an [AllerHande](https://www.ah.nl/allerhande/) recipe overview page url (example: https://www.ah.nl/allerhande/recepten-zoeken?Ntt=pasta),
```
$ python manage.py create_recipes_from_url <allerhande url>
```

## Development

### Testing

Run all tests,
```
$ python manage.py test
```

Run specific tests (example),
```
$ python manage.py test website.test.TestCaseAdminLogin
```

### Import/export demo data

Create a json database dump,
 ```
$ python manage.py dumpdata --all --natural-foreign --indent 2 product auth.User auth.Group > demo_data.json
```
Note: this includes user data.

Import a json dump,
```
$ python manage.py loaddata demo_data.json
```

### Logging
There are 3 log files (`debug.log`, `error.log`, `django.log`) available, with different log levels and for different applications.
The log files are found in the `log` directory of the project.
The log statements contain the time, log level, file, class, function name and line. 

The log something, create a logger at the top of you python file,
```python
import logging
logger = logging.getLogger(__name__)
```
then create a log statement,
```python
logger.debug('an info log message')
logger.info('an info log message')
logger.warning('a warning log message')
logger.error('an error log message')
logger.exception(exception_object)
```
