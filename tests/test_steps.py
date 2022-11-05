from unittest import TestCase
from merge import steps

class TestSteps(TestCase):
    
    def test_step_classes(self):
        step_classes = steps.step.Step.step_classes()
        self.assertTrue("<class 'merge.steps.merge_step.MergeStep'>" in str(step_classes))

    def test_step_dict(self):
        step_dict = steps.step.Step.step_dict()
        self.assertTrue("<class 'merge.steps.merge_step.MergeStep'>" in str(step_dict))
