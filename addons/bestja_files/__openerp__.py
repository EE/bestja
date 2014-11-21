# -*- coding: utf-8 -*-
{
    'name': "Bestia: File repository",
    'summary': "A place for keeping files, with support for categories.",
    'description': """
File repository
===============
You can keep files there, and it even supports categories.
More importantly, it's less confusing than what's in Odoo.

Cool, huh?""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'bestja_base',
    ],
    'data': [
        'views/file.xml',
        'menu.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
}
