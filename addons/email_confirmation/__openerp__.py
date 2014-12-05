# -*- coding: utf-8 -*-
{
    'name': "Email Confirmation",

    'summary': """
        Module for email confirmation after user signup.
    """,
    'description': """
Email confirmation
=========================
Module for email confirmation after signup.
When user clicks on the confirmation link his account becomes active.
    """,

    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',

    'depends': [
        'base',
        'auth_signup',
        'mail',
    ],

    'data': [
        'email_confirmation_data.xml',
        'views/email_confirmation_signup.xml',
    ],
}
