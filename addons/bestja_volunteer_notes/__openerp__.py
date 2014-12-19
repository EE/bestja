# -*- coding: utf-8 -*-
{
    'name': "BestJa: Volunteer Notes",
    'summary': "Adding notes about volunteers",
    'description': """
BestJa Volunteer Notes
=========================
Administrators and organization coordinators are able to
add notes to volunteer profiles.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_organization',
        'bestja_volunteer',
    ],
    'data': [
        'views/volunteer.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
