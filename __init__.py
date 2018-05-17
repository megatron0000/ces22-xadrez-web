from os import write, environ

write(environ.get('GMAIL_CLIENT_SECRET_PATH', 'client_secret.json'),
      environ.get('GMAIL_CLIENT_DUMP'))
