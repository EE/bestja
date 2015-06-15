# -*- coding: utf-8 -*-
{
    'name': "Embedded objects",
    'summary': "Embeding videos etc. and listing it on the website",
    'description': """
        A module for embeding videos and other media and listing them.
    """,
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'templates.xml',
        'views/embedded_object.xml',
        'menu.xml',
    ],
}
