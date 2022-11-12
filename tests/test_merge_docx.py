import os
import datetime
from parameterized import parameterized
from unittest import TestCase
import filecmp
from merge.utils.docx_utils import substituteVariablesDocx_direct, docx_content
from merge.models import ClientConfig
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merge.engine_settings")
application = get_wsgi_application()


class TestMergeUtils(TestCase):
    
    @parameterized.expand([
        ('./tests/fixtures/templates/Invoice.docx', 'a', 
            {
                'number': 'INV342', 
                'date': datetime.date(2022,10,1), 
                "company": {
                    "name": "ECV Inc.",
                    "address1": "15 Oddrow"
                },
                "customer": {
                    "name": "Jeremy Fisher",
                    "address1": "6b Fullbrook Lane"
                },
                "items":[
                    {
                        "description": "Subscription",
                        "price": 123.45
                    },
                    {
                        "description": "Upgrade",
                        "price": 6.55
                    }
                ],
                "total": 130.00
            }), 
    ])    
    def test_merge_docx(self, fixture, variant, subs):
        config = ClientConfig()
        config.tenant = ('.')
        filenameIn = fixture
        filenameOut = filenameIn.replace('templates', 'output').replace('.docx', f'.{variant}.docx')
        filenameExpected = filenameOut.replace('output', 'expected')
        try:
            os.remove(filenameOut)
        except OSError:
            pass
        fileOut = substituteVariablesDocx_direct(config, filenameIn, filenameOut, subs)
        self.assertEqual(fileOut['file'], filenameOut)
        expected = docx_content(filenameExpected)
        merged = docx_content(fileOut['file'])
        self.assertEqual(expected, merged)
