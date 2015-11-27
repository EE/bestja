# -*- coding: utf-8 -*-
{
    'name': "BestJa: Offers Hierarchy",
    'summary': "Support of project hierarchy fot the offers module",
    'description': """
BestJa Offers Hierarchy
=========================
Coordinators and managers of parent project can access offers.
Some statistics.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'bestja_offers',
        'bestja_project_hierarchy',
    ],
    'data': [
        'views/offer.xml',
        'menu.xml',
        'security/security.xml',
    ],
}
