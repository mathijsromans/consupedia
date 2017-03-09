python -m venv env
CALL env\Scripts\activate.bat
python -m pip install -U pip
pip install -r requirements.txt
python create_local_settings.py
python manage.py migrate
