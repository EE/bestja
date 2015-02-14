{
    # Theme information
    'name': "FPBŻ Theme",
    'summary': "Html5 Responsive Bootstrap Theme for Odoo CMS",
    'description': """
    This is a custom theme made for Federacja Polskich Banków Żywności
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
        'templates/pages/footer.xml',
        'templates/pages/become_partner.xml',
        
    # snippets
        'templates/snippets/main_top_white_text.xml',
        'templates/snippets/why_act_with_us.xml',
        'templates/snippets/map_of_poland.xml',
        'templates/snippets/quote_div.xml',
        'templates/snippets/volunteers_newsletter.xml',
        'templates/snippets/meet_our_volunteers.xml',
        'templates/snippets/get_knowledge.xml',
    ],
    'application': True,
    # About information
    'author': "Laboratorium EE, Kamil Woźniak",
    'website': "http://laboratorium.ee",
}
