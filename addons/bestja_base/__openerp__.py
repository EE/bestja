# -*- coding: utf-8 -*-
{
    'name': "BestJa: Base",

    'summary': """Common definitions for the BestJa project""",

    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'menu.xml',
        'config.xml',
        'views/assets.xml',
        'security/security.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ]
}
