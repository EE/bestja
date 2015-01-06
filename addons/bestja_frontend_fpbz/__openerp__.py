{
    # Theme information
    'name': "FPBŻ frontend",
    'description': """
    This is a custom theme made for Federacja Polskich Banków Żywności
    """,
    'category': 'Theme',
    'version': '1.0',
    'css': ['static/src/css/custom.css'],
    'depends': ['website'],

    # templates, pages, and snippets
    'data': [
        'views/config.xml',

    # pages
        'templates/pages/header.xml',
        'templates/pages/home_page.xml',
        'templates/pages/footer.xml',
    ],
    'application': True,
    # Your information
    'author': "Laboratorium EE, Kamil Woźniak",
    'website': "http://laboratorium.ee",
}
