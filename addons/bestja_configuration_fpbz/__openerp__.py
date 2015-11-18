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
        'bestja_volunteer_fpbz',
        'bestja_volunteer_notes',
        'bestja_account_deletion',
        'bestja_organization',
        'bestja_organization_hierarchy',
        'bestja_project',
        'bestja_project_hierarchy',
        'bestja_stores',
        'bestja_stores_chain_import',
        'bestja_requests',
        'bestja_detailed_reports',
        'bestja_estimation_reports',
        'bestja_offers',
        'bestja_offers_by_org',
        'bestja_files',
        'quizzes',
        'bestja_organization_warehouse',
        'bestja_age_verification',
        'bestja_frontend_fpbz',
        'bestja_page_fixtures_fpbz',
        'bestja_intro',
        'bestja_helpdesk',
    ],
    'data': [
        'data.xml',
    ],
    'application': True,
}
