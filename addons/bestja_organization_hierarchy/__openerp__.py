# -*- coding: utf-8 -*-
{
    'name': "Bestja: Hierarhical Organizations",
    'summary': "Organizations hierarchy for Bestja Organizations",
    'description': """
Bestja Hierarhical Organizations
================================
Adds parent-child relationship to organizations from the `bestja_organization`
module. Parent organizations have administrative rights to their children.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_organization',
    ],
    'data': [
        'views/organization.xml',
        'menu.xml',
        'security/security.xml',
    ],
    'demo': [
        'demo.xml',
    ],
}
