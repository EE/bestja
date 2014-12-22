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
    'data': [
        'views/volunteer.xml',
        'data/occupation.xml',
        'data/skills.xml',
        'data/languages.xml',
        'data/daypart.xml',
        'data/drivers_license.xml',
        'data/wishes.xml',
        'menu.xml',
        'security/ir.model.access.csv'
    ],
}
