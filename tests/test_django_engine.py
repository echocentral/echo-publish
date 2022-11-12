import os
from parameterized import parameterized
from unittest import TestCase
import filecmp
from merge.utils.engine_utils import get_engine, substituteVariablesPlainString, substituteVariablesPlain
from merge.models import ClientConfig
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merge.engine_settings")
application = get_wsgi_application()


class TestDjangoEngine(TestCase):
    
    def _test_get_engine(self):
        config = ClientConfig()
        config.tenant = ('.')
        engine = get_engine(config)
        print(engine)
        self.assertTrue(True)

    def _test_render_string(self):
        config = ClientConfig()
        config.tenant = ('.')
        engine = get_engine(config)
        print(engine)
        subs = {"version": "1a", "year": 2022}
        stringIn = "This is version {{ version }} written in {{ year }}"
        stringOut = substituteVariablesPlainString(config, stringIn, subs)
        expected = "This is version 1a written in 2022"
        self.assertEqual(stringOut, expected)

    def _test_render_string_2(self):
        config = ClientConfig()
        config.tenant = ('.')
        engine = get_engine(config)
        print(engine)
        subs = {"version": "1a", "year": 2022}
        stringIn = "This is version {{ version }} written in {{ year }}"
        stringOut = substituteVariablesPlainString(config, stringIn, subs)
        expected = "This is version 1a written in 2022"
        self.assertEqual(stringOut, expected)

    @parameterized.expand([
        ('./tests/fixtures/templates/SampleText01.txt', 'a',
            {'adj1': 'trivial', 'adj2': 'useful', "company": {"name": "ABC Inc."}}), 
        ('./tests/fixtures/templates/SampleText01.txt', 'b',
            {'adj1': 'trivial', 'adj2': 'useful', "company": {"name": "XYZ Inc."}}), 
        ('./tests/fixtures/templates/SampleText02.txt', 'a',
            {"versions": ["1a", "1b"], "company": {"name": "XYZ Inc."}}),
        ('./tests/fixtures/templates/SampleText03.txt', 'a',
            {"versions": ["1a", "1b"], "company": {"name": "XYZ Inc."}}),
        ('./tests/fixtures/templates/SampleText03.txt', 'b',
            {"versions": ["1a", "1b", "1c", "1d"], "company": {"name": "XYZ Inc."}}) 
    ])    
    def test_render_file(self, fixture, variant, subs):
        config = ClientConfig()
        config.tenant = ('.')
        filenameIn = fixture
        filenameOut = filenameIn.replace('templates', 'output').replace('.txt', f'.{variant}.txt')
        filenameExpected = filenameOut.replace('output', 'expected')
        fileOut = substituteVariablesPlain(config, filenameIn, filenameOut, subs)
        self.assertEqual(fileOut['file'], filenameOut)
        self.assertTrue(filecmp.cmp(filenameOut, filenameExpected))

