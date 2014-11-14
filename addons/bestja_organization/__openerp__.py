# -*- coding: utf-8 -*-
{
    'name': "Bestja: Organization",
    'summary': "Managing Organizations",
    'description': """
BestJa Organization Profile
===========================
This module allow users to add new organizations
(which need to be accepted by the BestJa Instance Admin).""",
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
        'menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
}
