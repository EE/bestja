# -*- coding: utf-8 -*-
{
    'name': "Collage Photo",
    'summary': """Module for the photo collage""",
    'description': """
        Module for the photo collage, allows adding pictures and 
        showing them as a list.
    """,
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'templates.xml',
        'views/collage_photo.xml',
        'menu.xml',
    ],
}
