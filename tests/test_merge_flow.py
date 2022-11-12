import os
import json
import datetime
from unittest import TestCase
from merge.flow import Flow
from merge.models import ClientConfig
from merge.utils.docx_utils import docx_content
from django.core.wsgi import get_wsgi_application
from merge.flow import StepContext
from merge.resources.resource_manager import LocalResourceManager
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "merge.engine_settings")
application = get_wsgi_application()


class TestMergeFlow(TestCase):
    
    def test_merge_flow_docx(self):
        flow_spec = [{
            "name": "Merge docx",
            "step": "merge",
            "local_ext": ".docx"
        }]

        config = ClientConfig()
        config.tenant = '.'

        template_subfolder = None
        localTemplateFileName = "Invoice.docx"
        uniq = 'abc123'

        output_subfolder = None

        localMergedFileName = "./tests/fixtures/output/Invoice_abc123"
        filenameExpected = "./tests/fixtures/expected/Invoice.out.docx"

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
        mf = Flow(flow_spec, step_context, config)
        outcome = mf.process(subs)

        self.assertEqual(outcome['success'], True)
        self.assertEqual(outcome['messages'], [])
        self.assertEqual(outcome['link'], 'http://test.echo-publish.con/file/?name=Invoice_abc123.docx')

        expected = docx_content(filenameExpected)
        merged = docx_content(localMergedFileName+'.docx')
        self.assertEqual(expected, merged)

    def test_flow_from_file(self):
        config = ClientConfig()
        config.tenant = '.'
        local_resources = LocalResourceManager(local_root='tests\\fixtures')
        flow_str = local_resources.get_local_txt_content(config, 'flows', 'merge.flo')
        flow_from_file = json.loads(flow_str)
        expected_flow = [{
            "name": "Merge docx",
            "step": "merge",
            "local_ext": ".docx"
        }]
        self.assertEqual(expected_flow, flow_from_file)

    def test_flow_from_file_2(self):
        config = ClientConfig()
        config.tenant = '.'
        local_resources = LocalResourceManager(local_root='tests\\fixtures')
        flow_from_file = local_resources.get_flow_spec(config, 'merge.flo')
        expected_flow = [{
            "name": "Merge docx",
            "step": "merge",
            "local_ext": ".docx"
        }]
        self.assertEqual(expected_flow, flow_from_file)
