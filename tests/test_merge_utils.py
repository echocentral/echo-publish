from unittest import TestCase
from merge.utils.merge_utils import replaceParams
from parameterized import parameterized


class TestMergeUtils(TestCase):
    
    @parameterized.expand([
        ('This is a ${adj1} test of a ${adj2} function', 
            {'adj1': 'trivial', 'adj2': 'useful'}, 
            'This is a trivial test of a useful function'),
        ('This is a ${adj1}, ${adj1} test of a ${adj2} function', 
            {'adj1': 'trivial', 'adj2': 'useful'}, 
            'This is a trivial, trivial test of a useful function'),
        ('This is a ${adj1} test of a ${adj2} function', 
            {'adj1': 'trivial', 'adjx': 'useful'}, 
            'This is a trivial test of a ${adj2} function'),
    ])    
    def test_replace_params(self, template, subs, expected):
        rendered = replaceParams(template, subs)
        self.assertEqual(rendered, expected)
