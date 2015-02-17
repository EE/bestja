# -*- coding: utf-8 -*-
{
    'name': "BestJa: Estimation reports",
    'summary': "Reports of estimations of products",
    'description': """
BestJa: Estimation reports
==========================
Module containing reports of estimated number of products
per shops in towns/cities obtained during projects.
    """,
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'css': ['static/src/css/*.css'],
    'depends': [
        'bestja_base',
        'bestja_project',
        'bestja_project_hierarchy',
        'bestja_stores',
    ],
    'data': [
        'views/project.xml',
        'views/assets.xml',
        'views/estimation_reports.xml',
        'views/estimation_reports_summary.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'menu.xml',
    ],
}
