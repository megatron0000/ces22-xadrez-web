from os import environ

file = open(environ.get('GMAIL_CLIENT_SECRET_PATH'), 'w')
file.write(environ.get('GMAIL_CLIENT_DUMP'))
file.close()
