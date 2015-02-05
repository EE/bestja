# -*- coding: utf-8 -*-
{
    'name': "Bestja Messages",
    'summary': "Messages customization for the Bestja Project",
    'description': """
Bestja Messages
===============
Various customizations of messages widgets for the BestJa project""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'bestja_base',
        'message_template',
    ],
    'data': [
        'security/security.xml',
    ],
    'qweb': [
        'static/src/xml/mail.xml',
    ],
    'auto_install': True,
}
