# Webchess

## Package dependencies

They are all listed on `requirements.txt` and expect `python 3.5.6`.

Instal with `pip install -U -r requirements.txt`

## Database dependencies

As `django` persistent storage, `webxadrez/settings.py` expects a `PostgreSQL` database. Default settings are on localhost, but environment variables can be created to direct to an external installation.

For `django-channels` channel-layers backend, it expects a `Redis` installation (default on localhost, but may be configured).

## Dependencies at deployment time

The intended deployment host is *heroku* (`Procfile` file serves this purpose)

When deploying to *heroku*, `config/nginx.conf.erb` configures an `nginx` server to route `static/**` urls to an external server configured with env variable `STATIC_URL` and route other urls to local server running `django-channels`

Currently, `STATIC_URL` points to an instance of google's `firebase` service.

## Local development

Provided all dependencies listed have been met, running `python manage.py runserver` activates a local server on port 8000.

It does NOT make use of `firebase`, instead serving local files directly with the django server. Also, it does not make use of an `nginx` server, instead using purely `django-channels` dev server.

Database and package dependencies still hold, though.