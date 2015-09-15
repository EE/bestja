# -*- coding: utf-8 -*-
{
    'name': "BestJa: API User group",
    'summary': "User group for importing users via API",
    'description': """
BestJa API User group
=============================
User group for importing users via API.
Has read-only access to all users in the system.""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_volunteer',
        'bestja_organization',
    ],
    'data': [
        'security/security.xml',
    ],
}
