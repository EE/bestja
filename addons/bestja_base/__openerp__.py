# -*- coding: utf-8 -*-
{
    'name': "BestJa: Base",
    'summary': "Common definitions for the BestJa project",
    'description': """
BestJa Project Base
===================
This module is not very useful all by itself, but it contains common
definitions used by other BestJa modules.

It includes (among other things) the BestJa menu and CSS definitions. """,
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'auth_signup',
        'mail',
        'message_template',
        'website',
        'email_confirmation'
    ],
    'data': [
        'menu.xml',
        'config.xml',
        'views/assets.xml',
        'security/security.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [
        'demo.xml',
    ],
}
