# -*- coding: utf-8 -*-
{
    'name': 'Quizzes',
    'description': 'Interactive quiz snippet for Website Builder',
    'description': """
Quizzes
=========================
This snippet Website Builder snippet lets you to add interactive quizzes
to the website.""",
    'author': 'Laboratorium EE',
    'website': 'http://www.laboratorium.ee',
    'depends': [
        'base',
        'website'
    ],
    'js': ['static/src/js/index.js'],
    'data': [
        'views/survey.xml',
    ],
    'installable': True,
    'application': True,
}
