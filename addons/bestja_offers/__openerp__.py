# -*- coding: utf-8 -*-
{
    'name': "Bestja: Job Offers",
    'summary': """Adding and displaying job offers""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'version': '0.1',
	'js': ['static/src/js/*.js'],
	'qweb': ['static/src/xml/*.xml'],
	'css': ['static/src/css/*.css'],

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
        'views/duration.xml',
        'views/config.xml',
        'data/daypart.xml',
        'data/target_group.xml',
        'data/weekday.xml',
		'templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
}
