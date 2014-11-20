# encoding: utf-8

from __future__ import unicode_literals
import collections
import glob
import os
import re
import sys

from openerp.tests.common import HttpCase


TestType = collections.namedtuple(
    'TestType',
    ['test_function', 'file_extension'],
)


PHANTOMJS_LIBRARY = """
function assert(value) {
    if (value) {
        console.log("ok");
    }
    else {
        console.log("error");
    }
}
"""


def phantomjs_run(self, filepath):
    with open(filepath, 'r') as f:
        script_contents = f.read()

    # Extracting kwargs from comments.
    # For example, the line
    # // PhantomArg: foo = bar
    # would give us key “foo” and value “bar”.
    #
    # It is mandatory to specify url_path.
    # For other possible parameters, refer to the definition of function phantom_js
    # in the HttpCase class.
    kwargs = dict(re.findall(r'^\s*//\s*PhantomArg:\s*(\w*)\s*=\s*([^\s]*)\s*', script_contents))
    url_path = kwargs.pop('url_path')

    return self.phantom_js(url_path, code=PHANTOMJS_LIBRARY + script_contents, **kwargs)


class ExternalTestsMetaclass(type):
    """
    A metaclass which generates test methods based on files located in the same folder.
    """

    test_types = [
        TestType(test_function=phantomjs_run, file_extension='js'),
    ]

    def __new__(cls, name, bases, attrs):
        ExternalTestCase = super(ExternalTestsMetaclass, cls).__new__(cls, name, bases, attrs)
        for test_type in cls.test_types:
            test_folder_path = os.path.dirname(sys.modules[ExternalTestCase.__module__].__file__)
            for test_filepath in glob.glob('{}/*.{}'.format(test_folder_path, test_type.file_extension)):
                method_name = 'test_{}'.format(os.path.basename(test_filepath).split(".")[0])
                test_method = lambda self, test_type=test_type, test_filepath=test_filepath: test_type.test_function(self, test_filepath)
                setattr(ExternalTestCase, method_name, test_method)
        return ExternalTestCase


class ExternalTestCase(HttpCase):
    """
    A test case which generates test methods based on files located in the same folder.
    """

    __metaclass__ = ExternalTestsMetaclass
    post_install = True
