import inspect
import re

import collectd_haproxy.plugin
import collectd_haproxy.connection
import collectd_haproxy.metrics
import collectd_haproxy.compat


modules_to_test = (
    collectd_haproxy.plugin,
    collectd_haproxy.connection,
    collectd_haproxy.metrics,
    collectd_haproxy.compat,
)


def test_docstrings():
    for module in modules_to_test:
        for path, thing in get_module_things(module):
            yield create_docstring_assert(path, thing)


def get_module_things(module):
    module_name = module.__name__

    for func_name, func in get_module_functions(module):
        if inspect.getmodule(func) != module:
            continue
        yield (module_name + "." + func_name, func)

    for class_name, klass in get_module_classes(module):
        if inspect.getmodule(klass) != module:
            continue
        yield (module_name + "." + class_name, klass)

        for method_name, method in get_class_methods(klass):
            if method_name not in klass.__dict__:
                continue
            yield (module_name + "." + class_name + ":" + method_name, method)


def get_module_classes(module):
    for name, klass in inspect.getmembers(module, predicate=inspect.isclass):
        yield (name, klass)


def get_module_functions(module):
    for name, func in inspect.getmembers(module, predicate=inspect.isfunction):
        yield (name, func)


def get_class_methods(klass):
    for name, method in inspect.getmembers(klass, predicate=inspect.ismethod):
        yield (name, method)


def create_docstring_assert(path, thing):

    def test_function():
        assert_docstring_present(thing, path)
        assert_docstring_includes_param_metadata(thing, path)

    test_name = "test_docstring__%s" % de_camelcase(path)
    test_function.__name__ = test_name
    test_function.description = test_name

    return test_function


def assert_docstring_present(thing, path):
    docstring = inspect.getdoc(thing)
    if not docstring or not docstring.strip():
        raise AssertionError("No docstring present for %s" % path)


def assert_docstring_includes_param_metadata(thing, path):
    if inspect.isclass(thing):
        return

    docstring = inspect.getdoc(thing)
    if not docstring:
        return

    for arg_name in inspect.getargspec(thing).args:
        if arg_name in ("self", "cls"):
            continue

        if ":param %s:" % arg_name not in docstring:
            raise AssertionError(
                "Missing :param: for arg %s of %s" % (arg_name, path)
            )
        if ":type %s:" % arg_name not in docstring:
            raise AssertionError(
                "Missing :type: for arg %s of %s" % (arg_name, path)
            )


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def de_camelcase(name):
    return all_cap_re.sub(
        r'\1_\2',
        first_cap_re.sub(r'\1_\2', name)
    ).lower()
