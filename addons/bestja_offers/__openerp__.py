# -*- coding: utf-8 -*-
{
    'name': "Bestja: Job Offers",
    'summary': """Adding and displaying job offers""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr_recruitment',
        'project',
        'bestja_volunteer',
        'bestja_styles'
    ],

    # always loaded
    'data': [
        'views/job.xml',
        'views/config.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
}
