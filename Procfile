% prepara el repositorio para su despliegue. 
release: sh -c 'cd decide && heroku pg:reset d7d5ko7df39q6p && python manage.py makemigrations && python manage.py migrate  && python manage.py loaddata data.json'
% especifica el comando para lanzar Decide
web: sh -c 'cd decide &&  python manage.py makemessages -l es && python manage.py makemessages -l ca  && python manage.py compilemessages && gunicorn decide.wsgi --log-file -'
