# -*- coding: utf-8 -*-
{
    'name': "BestJa: Account Deletion",
    'summary': "Module for special account deletion.",
    'description': """
BestJa Account Deletion
=======================
Bestja Instance Admin can deactivate user and remove her personal data.""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_base',
        'bestja_volunteer',
    ],
    'data': [
        'views/account_deletion_wizard.xml',
        'views/report_account_deletion_wizard.xml',
        'messages.xml',
    ],
}
