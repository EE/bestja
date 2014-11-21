# -*- coding: utf-8 -*-
{
    'name': "Bestja: Project files",
    'summary': "Per-project file repositories",

    'description': """
Project Files
=========================
Adds an ability to add files to projects and to
later browse all project files in one place.
    """,
    'author': 'Laboratorium EE',
    'website': 'http://www.laboratorium.ee',
    'version': '0.1',
    'depends': [
        'bestja_project',
        'bestja_files'
    ],
    'data': [
        'views/file.xml',
        'views/project.xml',
        'menu.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'auto_install': True,
}
