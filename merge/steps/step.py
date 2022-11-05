
class Step(object):

    keyword = 'generic'

    def __init__(self, step):
        self.step_spec = step

    @classmethod
    def step_classes(klass):
        subclasses = set()
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    @classmethod
    def step_dict(klass):
        subclasses = klass.step_classes()
        class_dict = {}
        for subclass in subclasses:
            class_dict[subclass.keyword] = subclass
        return class_dict






