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
    'depends': [
        'base',
        'bestja_base',
        'bestja_volunteer',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/organization.xml',
        'menu.xml'
    ],
    'demo': [
        'demo.xml',
    ],
    'application': True,
}
