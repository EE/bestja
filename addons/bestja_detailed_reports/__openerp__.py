# -*- coding: utf-8 -*-
{
    'name': "BestJa: Detailed reports",
    'summary': "Adding detailed reports of products",
    'description': """
BestJa: Detailed reports
========================
Module containing reports of products obtained during projects.
    """,
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'bestja_base',
        'bestja_project',
        'bestja_project_hierarchy',
    ],
    'data': [
        'views/project.xml',
        'views/detailed_reports.xml',
        'views/detailed_reports_summary.xml',
        'menu.xml',
        'data/commodities.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'messages.xml',
    ],
}
