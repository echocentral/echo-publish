from unittest import TestCase
from merge.payloads.payload_manager import PayloadManager

class TestPayload(TestCase):
    
    def test_dict2subs(self):
        dict_in = {
            "a": 1, "b": 2
        }
        pm = PayloadManager.from_dict(dict_in)
        subs = pm.subs
        self.assertEqual(subs['a'], 1)
        self.assertEqual(subs['b'], 2)
        self.assertTrue(True)

    def test_json2subs(self):
        json_in = '{"a": 1, "b": 2}'
        pm = PayloadManager.from_json(json_in)
        subs = pm.subs
        self.assertEqual(subs['a'], 1)
        self.assertEqual(subs['b'], 2)
        self.assertTrue(True)

    def test_xml2subs(self):
        xml_in = '<payload><a>1</a><b>2</b></payload>'
        pm = PayloadManager.from_xml(xml_in)
        subs = pm.subs
        self.assertEqual(subs['a'], "1")
        self.assertEqual(subs['b'], "2")
        self.assertTrue(True)
