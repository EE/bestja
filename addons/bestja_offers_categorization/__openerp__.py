# -*- coding: utf-8 -*-
{
    'name': "Bestja: Offers categorization",
    'summary': "Adds categories to offers",
    'description': """
BestJa Job Offers Categorization
================================
Adds categories to offers and allows users to browse offers by category.""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'depends': [
        'bestja_offers'
    ],
    'data': [
        'templates.xml',
        'data.xml',
        'views/offer.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo.xml',
    ],
}
