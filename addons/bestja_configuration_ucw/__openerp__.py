# -*- coding: utf-8 -*-
{
    'name': "Bestja: UCW",
    'summary': "Installation configuration for UCW",
    'description': "Installation configuration for Uniwersyteckie Centrum Wolontariatu",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'category': 'Specific Industry Applications',
    'depends': [
        'base',
        'bestja_base',
        'bestja_volunteer',
        'bestja_volunteer_notes',
        'bestja_organization',
        'bestja_project',
        'bestja_offers',
        'bestja_offers_moderation',
        'bestja_offers_invitations',
        'bestja_files',
        'bestja_application_moderation',
    ],
    'data': [
        'data.xml',
    ],
    'application': True,
}
