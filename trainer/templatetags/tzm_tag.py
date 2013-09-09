# -*- coding:utf-8 -*-
from django import template

register=template.Library()

@register.filter
def by_key(_dict, key):
    return _dict.get(key)
