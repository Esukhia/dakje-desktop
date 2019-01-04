#!/usr/bin/env python
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


class Format(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)  # Hex, e.g. #000000


class Token(models.Model):
    content = models.CharField(max_length=255)
    format = models.ForeignKey(Format, on_delete=models.CASCADE)


class Dict(models.Model):
    ACTION_ADD = 1
    ACTION_DELETE = 2

    content = models.CharField(max_length=255)
    pos = models.CharField(max_length=255)
    action = models.IntegerField()
