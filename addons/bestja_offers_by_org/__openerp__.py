# -*- coding: utf-8 -*-
{
    'name': "Bestja: Offers by Organization",
    'summary': "Browse offers by organization",
    'description': """
BestJa Job Offers by Organization
========================
Adds browsing by hierarchical organizations to the website.""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'depends': [
        'bestja_offers',
        'bestja_organization_hierarchy',
    ],
    'data': [
        'templates.xml',
    ],
}
