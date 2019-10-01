# To update the fields in the database, edit classes and run
# `python manage.py makemigrations`
# `python manage.py migrate`

import json

from django.db import models


class Setting(models.Model):
    key = models.CharField(max_length=255)
    value = models.TextField()


class Rule(models.Model):
    TYPE_UPDATE = 1
    TYPE_REMARK = 2

    cql = models.CharField(max_length=255)  # match phrase
    actionCql = models.CharField(max_length=255)  # match token in phrase
    action = models.TextField()  # dict to update
    type = models.IntegerField()
    order = models.IntegerField()

    class Meta:
        pass  # order

    def getActionCqlDisplay(self):
        return self.actionCql.split('"')[1]

    getActionCqlDisplay.short_description = 'Token'

    def getActionDisplay(self):
        return '<br/>'.join('{}: {}'.format(k, v)
                         for k,v in json.loads(self.action).items())

    getActionDisplay.allow_tags = True
    getActionDisplay.short_description = 'Attributes'

class Format(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)  # Hex, e.g. #000000
    level = models.IntegerField(null=True)


class Token(models.Model):
    TYPE_UPDATE = 1
    TYPE_REMOVE = 2

    text = models.CharField(max_length=255)
    pos = models.CharField(max_length=255, null=True, blank=True)
    lemma = models.CharField(max_length=255, null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)
    meaning = models.TextField(null=True, blank=True)

    type = models.IntegerField(choices=(
        (TYPE_UPDATE, 'update'),
        (TYPE_REMOVE, 'remove')
    ))
