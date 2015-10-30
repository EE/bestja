# -*- coding: utf-8 -*-
{
    'name': "Bestja: Import of store chain permissions",
    'summary': "Option to import permissions from store chains to use their stores durring a collection",
    'description': """
BestJa Import of store chain permissions
========================================
Option to import (from a CSV file) permissions from store chains to use their stores durring a collection.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'depends': [
        'bestja_stores',
    ],
    'data': [
        'views/chain_import_wizard.xml',
        'messages.xml',
    ],
}
