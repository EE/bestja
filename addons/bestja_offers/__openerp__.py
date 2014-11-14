# -*- coding: utf-8 -*-
{
    'name': "Bestja: Job Offers",
    'summary': "Adding and displaying job offers",
    'description': """
BestJa Job Offers
===================
This module deals with creating job offers, publishing them on the website,
receiving and managing user applications.""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'js': ['static/src/js/*.js'],
    'qweb': ['static/src/xml/*.xml'],
    'css': ['static/src/css/*.css'],

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'website',
        'bestja_volunteer',
        'bestja_base',
        'bestja_project'
    ],

    # always loaded
    'data': [
        'config.xml',
        'views/application.xml',
        'views/offer.xml',
        'views/assets.xml',
        'data/daypart.xml',
        'data/helpee_group.xml',
        'data/weekday.xml',
        'data/rejected_reasons.xml',
        'templates.xml',
        'menu.xml',
        'workflows.xml',
        'security/ir.model.access.csv',
        'security/security.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
    'installable': True,
    'application': True,
}
