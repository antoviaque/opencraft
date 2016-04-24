from astroid import MANAGER
from astroid import scoped_nodes
from astroid.as_string import dump

def register(linter):
    pass

def is_available():
    return True

def transform(method):
    if method.is_method() and \
            'instance.models.utils.ResourceStateDescriptor.only_for.wrap' in method.decoratornames():
        print(dump(method), method.decoratornames())

        #is_available = MANAGER.ast_from_module_name('opencraft.pylint').lookup('is_available')[0]
        #print(is_available)

        is_available = scoped_nodes.Function('is_available', None)
        is_available.parent = method
        #is_available.file = 'bla'
        method.instance_attrs['is_available'] = is_available

MANAGER.register_transform(scoped_nodes.Function, transform)
