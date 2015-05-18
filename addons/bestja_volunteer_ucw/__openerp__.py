# -*- coding: utf-8 -*-
{
    'name': "BestJa: Volunteer (UCW)",
    'summary': "Volunteer Profile (UCW)",
    'description': """
Volunteer Profile modification for UCW
=========================
Hides a couple of fields, and adds a new "UW status" field.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'depends': [
        'bestja_volunteer',
        'bestja_offers',
    ],
    'data': [
        'data/wishes.xml',
        'data/uw_status.xml',
        'views/volunteer.xml',
        'views/offer.xml',
        'security/ir.model.access.csv',
    ],
}
