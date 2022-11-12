import json
import xmltodict


class PayloadManager(object):

    def __init__(self, subs_dict):
        self.subs = subs_dict

    @classmethod
    def from_dict(cls, dict):
        pm = cls(dict)
        return pm

    @classmethod
    def from_json(cls, json_dict):
        pm = cls(json.loads(json_dict))
        return pm

    @classmethod
    def from_xml(cls, xml_dict):
        payload = xmltodict.parse(xml_dict)
        print(payload.values())
        pm = cls(list(payload.values())[0])
        print(pm.subs)
        return pm

