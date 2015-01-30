# -*- coding: utf-8 -*-
{
    'name': "Bestja: FBŻ",
    'summary': "Installation configuration for FPBŻ",
    'description': "Installation configuration for Federacja Polskich Banków Żywności",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'category': 'Specific Industry Applications',
    'depends': [
        'base',
        'bestja_base',
        'bestja_volunteer',
        'bestja_volunteer_notes',
        'bestja_account_deletion',
        'bestja_organization',
        'bestja_organization_hierarchy',
        'bestja_project',
        'bestja_project_hierarchy',
        'bestja_requests',
        'bestja_offers',
        'bestja_offers_by_org',
        'bestja_files',
        'quizzes',
        'bestja_organization_warehouse'
    ],
    'data': [
        'data.xml',
    ],
    'application': True,
}
