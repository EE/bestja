# -*- coding: utf-8 -*-
{
    'name': "Bestja: Projects",
    'summary': "Project management in BestJa",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_base',
        'base',
        'bestja_organization',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/project.xml',
        'menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
