import os
import datetime
from unittest import TestCase
from merge.steps.merge_step import MergeStep
from merge.models import ClientConfig
from merge.utils.docx_utils import docx_content
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merge.engine_settings")
application = get_wsgi_application()

class TestMergeStep(TestCase):
    
    def test_merge_step(self):

        spec = {
            "local_ext": ".docx"
        }
        ms = MergeStep(spec)
        cwd = os.getcwd()
        config = ClientConfig()
        config.tenant = ('.')
        uniq = 'abc123'
        localTemplateFileName = "./tests/fixtures/Invoice"
        template_subfolder = '.'
        localMergedFileName = "./tests/results/Invoice.out"
        filenameExpected = "./tests/expected/Invoice.out.docx"
        localMergedFileNameOnly = "Invoice.out.docx'"
        output_subfolder = 'osf'

        subs = {
                'site': 'test.echo-publish.con',
                'number': 'INV342', 
                'date': datetime.date(2022, 10, 1), 
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
            }
        try:
            os.remove(localMergedFileName+'.docx')
        except OSError:
            pass
        ms.process(
            cwd, config, uniq, localTemplateFileName, template_subfolder, 
            localMergedFileName, localMergedFileNameOnly, 
            output_subfolder, 
            subs)
        expected = docx_content(filenameExpected)
        merged = docx_content(localMergedFileName+'.docx')
        self.assertEqual(expected, merged)
