# -*- coding: utf-8 -*-
{
    'name': "BestJa: Application Moderation",
    'summary': "Two stage recruitment process",
    'description': """
BestJa Application Moderation
=============================
Split recruitment process into two separate stages.

The first ("preliminary") stage is handled by offer moderators.

The second stage is handled by the recruiting organization itself.""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'bestja_offers_moderation',
    ],
    'data': [
        'views/offer.xml',
        'menu.xml',
        'security/security.xml',
    ],
}
