import os
import datetime
from unittest import TestCase
from merge.flow import Flow
from merge.models import ClientConfig
from merge.utils.docx_utils import docx_content
from django.core.wsgi import get_wsgi_application
from merge.flow import StepContext
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merge.engine_settings")
application = get_wsgi_application()

class TestMergeStep(TestCase):
    
    def test_merge_flow_docx(self):
        flow_spec = [{
            "name": "Merge docx",
            "step": "merge",
            "local_ext": ".docx"
        }]
        cwd = os.getcwd()
        config = ClientConfig()
        config.tenant = '.'
        uniq = 'abc123'
        localTemplateFileName = "Invoice.docx"
        template_folder = "../tests/fixtures/"
        template_subfolder = None
        localMergedFileName = "./tests/results/Invoice_abc123"
        filenameExpected = "./tests/expected/Invoice.out.docx"
        output_folder = '../tests/results/'
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
        step_context = StepContext(cwd, config, None, template_folder, template_subfolder, localTemplateFileName, uniq, output_folder, output_subfolder)

        mf = Flow(flow_spec, step_context)
        outcome = mf.process(subs)
        print(outcome)
        self.assertEqual(outcome['success'], True)
        self.assertEqual(outcome['messages'], [])
        self.assertEqual(outcome['link'], 'http://test.echo-publish.con/file/?name=Invoice_abc123.docx')
        expected = docx_content(filenameExpected)
        merged = docx_content(localMergedFileName+'.docx')
        self.assertEqual(expected, merged)
