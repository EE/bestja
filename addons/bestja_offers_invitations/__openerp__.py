# -*- coding: utf-8 -*-
{
    'name': "Bestja: Offers Invitations",
    'summary': "Invite specific users to specific job offers.",
    'description': """
BestJa Offers Invitations
===================
Adds an option for inviting users to the context menu in user views.
Invited users receive direct messages with links to specific offers.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_offers',
    ],
    'data': [
        'views/invitations_wizard.xml',
        'messages.xml',
    ],
}
