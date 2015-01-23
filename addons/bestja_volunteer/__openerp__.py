# -*- coding: utf-8 -*-
{
    'name': "BestJa: Volunteer",
    'summary': "Volunteer Profile",
    'description': """
BestJa Volunteer Profile
=========================
Adds additional fields to user profiles, allowing users to
specify their experiences, interests etc.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': [
        'bestja_base',
        'auth_crypt',
    ],
    'demo': [
        'demo.xml',
    ],
    'js': ['static/src/js/*.js'],
    'data': [
        'views/volunteer.xml',
        'views/partner.xml',
        'views/assets.xml',
        'data/occupation.xml',
        'data/skills.xml',
        'data/languages.xml',
        'data/daypart.xml',
        'data/drivers_license.xml',
        'data/wishes.xml',
        'data/voivodeship.xml',
        'menu.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
