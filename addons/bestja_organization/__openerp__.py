# -*- coding: utf-8 -*-
{
    'name': "Bestja: Organization",
    'summary': """ Managing Organizations""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'bestja_base'
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/organization.xml',
        'views/login.xml',
        'menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    #    'demo.xml',
    ],
    'installable': True,
    'application': True,
}
