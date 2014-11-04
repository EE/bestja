# -*- coding: utf-8 -*-
{
    'name': "Bestja: Projects",
    'summary': "Project management in BestJa",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_base',  # This dependency is redundant, but we need to load it first because of monkeypatches.
        'base',
        'project',
        'bestja_organization'
    ],

    'data': [
        'views/project.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
