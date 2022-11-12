import os
import datetime
from unittest import TestCase
from merge.steps.merge_step import MergeStep
from merge.models import ClientConfig
from merge.utils.docx_utils import docx_content
from django.core.wsgi import get_wsgi_application
from merge.flow import StepContext
from merge.resources.resource_manager import LocalResourceManager
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merge.engine_settings")
application = get_wsgi_application()


class TestMergeStep(TestCase):
    
    def test_merge_step_docx(self):
        spec = {
            "local_ext": ".docx"
        }
        config = ClientConfig()
        config.tenant = '.'
        uniq = 'abc123'
        localTemplateFileName = "Invoice.docx"
        template_subfolder = None
        localMergedFileName = "./tests/fixtures/output/Invoice_abc123"
        filenameExpected = "./tests/fixtures/expected/Invoice.out.docx"
        output_subfolder = None

        subs = {
                'site': 'http://test.echo-publish.con/',
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
        remote_resources = None
        local_resources = LocalResourceManager(local_root='tests\\fixtures')
        step_context = StepContext(config, remote_resources, local_resources, template_subfolder, localTemplateFileName, output_subfolder, uniq)
        ms = MergeStep(spec)
        outcome = ms.process(step_context, subs)
        expected = docx_content(filenameExpected)
        merged = docx_content(localMergedFileName+'.docx')
        self.assertEqual(expected, merged)
        expected_outcome = {
            'file': 'C:/Users/Andrew/Documents/GitHub/echo-publish/tests/fixtures/output//Invoice_abc123.docx',
            'link': 'http://test.echo-publish.con/file/?name=Invoice_abc123.docx'
        }
        self.assertEqual(outcome, expected_outcome)
