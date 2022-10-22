from unittest import TestCase
import os
from merge.utils.engine_utils import get_engine, substituteVariablesPlainString
from merge.models import ClientConfig
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merge.engine_settings")
application = get_wsgi_application()


class TestDjangoEngine(TestCase):
    
    def test_get_engine(self):
        config = ClientConfig()
        config.tenant = ('.')
        engine = get_engine(config)
        print(engine)
        self.assertTrue(True)

    def test_render_string(self):
        config = ClientConfig()
        config.tenant = ('.')
        engine = get_engine(config)
        print(engine)
        subs = {"version": "1a", "year": 2022}
        stringIn = "This is version {{ version }} written in {{ year }}"
        stringOut = substituteVariablesPlainString(config, stringIn, subs)
        expected = "This is version 1a written in 2022"
        self.assertEqual(stringOut, expected)
