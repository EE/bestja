{
    # Theme information
    'name': "UCW Theme",
    'summary': "Html5 Responsive Bootstrap Theme for Odoo CMS",
    'description': """
    This is a custom theme made for Uniwersyteckie Centrum Wolontariatu
    """,
    'category': 'Theme',
    'version': '1.0',
    'css': ['static/src/css/custom.css'],
    'depends': ['website'],

    # assets
    'data': [
        'views/assets.xml',
        
    # pages
        'templates/pages/title.xml',
        'templates/pages/home_page.xml',
        'templates/pages/contactus.xml',
        'templates/pages/footer.xml',
        'templates/pages/about_us.xml',
        'templates/pages/for_organizations.xml',
        'templates/pages/become_volunteer.xml',
        'templates/pages/wolontariat_badawczy.xml',
        'templates/pages/regulations.xml',
        'templates/pages/privacy_policy.xml',
        'templates/pages/team.xml',
        'templates/pages/for_volunteers.xml',
        
    # snippets
        
    ],
    'application': True,
    # About information
    'author': "Laboratorium EE, Kamil Woźniak",
    'website': "http://laboratorium.ee",
}