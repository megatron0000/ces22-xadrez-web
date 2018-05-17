from os import write, environ

write(environ.get('GMAIL_CLIENT_SECRET_PATH'),
      environ.get('GMAIL_CLIENT_DUMP'))
