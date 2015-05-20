# -*- coding: utf-8 -*-
{
    'name': "BestJa: Volunteer (FPBZ)",
    'summary': "Volunteer Profile (FPBZ)",
    'description': """
Volunteer Profile modification for FPBZ
=========================
Adds qualifications secion.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'depends': [
        'bestja_volunteer',
        'bestja_offers',
    ],
    'data': [
        'data/wishes.xml',
        'data/drivers_license.xml',
        'views/volunteer.xml',
        'views/offer.xml',
        'views/application.xml',
        'security/ir.model.access.csv',
        'templates.xml',
    ],
}
