# -*- coding: utf-8 -*-
{
    'name': "BestJa: Project Hierarchy",
    'summary': "Parent-children relationships for projects",
    'description': """
BestJa Project Hierarchy
=========================
Allows organizations to invite their child organizations to
projects.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'protected_fields',
        'bestja_project',
        'bestja_organization_hierarchy',
    ],
    'data': [
        'views/invitation.xml',
        'views/project.xml',
        'menu.xml',
        'messages.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
