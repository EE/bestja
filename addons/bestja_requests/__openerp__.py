# -*- coding: utf-8 -*-
{
    'name': "Bestja: Project Requests",
    'summary': "Requests from child projects managers to parent project managers",
    'description': """
Bestja Project Requests
=========================
Allows managers of parent projects to define request templates, which child
project managers can use to send their requests.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
    'depends': [
        'base',
        'protected_fields',
        'bestja_base',
        'bestja_project_hierarchy',
    ],
    'data': [
        'views/request_template.xml',
        'views/request.xml',
        'views/request_item.xml',
        'views/project.xml',
        'menu.xml',
        'messages.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
}
