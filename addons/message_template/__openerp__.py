# -*- coding: utf-8 -*-
{
    'name': "Message Templates",
    'summary': "Sending template based notifications",
    'description': """
Message Templates
=================
A utility module providing other modules with an option to
keep notification templates in XML and send them out using
simple API.""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'mail',
        'email_template',
    ],
    'data': [
        'data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
