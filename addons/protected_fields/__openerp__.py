# -*- coding: utf-8 -*-
{
    'name': "Protected Fields Mixin",
    'summary': """Provides a mixin that allows model creators to specify
        a list of protected fields in their models.""",
    'description': """
Protected Fields Mixin
======================
Provides a mixin that allows model creators to specify
a list of protected fields in their models.

Protected fields can be read by everyone with read
permissions to the object, but can be modified
only by specified users and groups.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': ['base'],
}
