# -*- coding: utf-8 -*-
{
    'name': "Bestja: Hierarchical Project files",
    'summary': "Permissions for hierarchical per-project file repositories",
    'description': """
Hierarchical Project files
==========================
Allows managers of child projects to view files
associated with parent repositories.
    """,
    'author': 'Laboratorium EE',
    'website': 'http://www.laboratorium.ee',
    'version': '0.1',
    'depends': [
        'bestja_project_hierarchy',
        'bestja_project_files',
    ],
    'data': [
        'security/security.xml',
        'messages.xml',
    ],
    'auto_install': True,
}
