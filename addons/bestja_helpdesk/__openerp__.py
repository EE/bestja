# -*- coding: utf-8 -*-
{
    'name': "Bestja: Helpdesk",
    'summary': "Allows users to ask questions to the admins",
    'description': """
Bestja Helpdesk
=========================
Users can ask questions. Admins are able to abswear the questions and add them to FAQ.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_base',
        'protected_fields',
    ],
    'data': [
        'views/question.xml',
        'menu.xml',
        'messages.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
