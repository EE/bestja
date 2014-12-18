# -*- coding: utf-8 -*-
{
    'name': "BestJa: Offers Moderation",
    'summary': "Offers are published only after being approved.",
    'description': """
BestJa Offers Moderation
========================
This module changes the BestJa Offers module, so only people in
BestJa Offers Moderator and BestJa Instance Admin groups are
able to publish offers directly.
Other people can publish their offers by sending them to moderators,
who need to accept them first.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': ['base', 'bestja_offers'],
    'data': [
        'security/security.xml',
        'views/offer.xml',
        'menu.xml',
        'security/ir.model.access.csv',
        'messages.xml',
    ],
    'demo': [
        'demo.xml',
    ],
}
