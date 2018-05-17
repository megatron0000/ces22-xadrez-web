from django.db import models
from django.contrib.postgres.fields import ArrayField


class UserToken(models.Model):
    token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.TextField()
    client_id = models.TextField()
    client_secret = models.TextField()
    scopes = ArrayField(models.TextField())
