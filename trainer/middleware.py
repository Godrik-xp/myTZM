# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.sessions.middleware import SessionMiddleware

class TZMSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None) or request.GET.get('sid')
        request.session = engine.SessionStore(session_key)
