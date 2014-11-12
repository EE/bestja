# -*- coding: utf-8 -*-
{
    'name': "BestJa: Volunteer",

    'summary': """
        Volunteer Profile""",

    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'bestja_base',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/volunteer.xml',
        'data/occupation.xml',
        'data/skills.xml',
        'data/drivers_license.xml',
        'data/wishes.xml',
        'menu.xml',
        'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'installable': True,
    'application': True,
}
