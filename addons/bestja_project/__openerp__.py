# -*- coding: utf-8 -*-
{
    'name': "Bestja: Projects",
    'summary': "Project management in BestJa",
    'description': """
BestJa Project management
=========================
Define projects and assign users to tasks.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_base',
        'base',
        'bestja_organization',
    ],

    'data': [
        'security/security.xml',
        'views/task.xml',
        'views/project.xml',
        'messages.xml',
        'menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo.xml',
    ],
    'application': True,
}
