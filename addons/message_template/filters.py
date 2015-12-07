from bleach import clean, ALLOWED_TAGS, ALLOWED_ATTRIBUTES


ALLOWED_TAGS += [
    'span',
    'div',
    'br',
    'p',
]
ALLOWED_ATTRIBUTES = ALLOWED_ATTRIBUTES.copy()
ALLOWED_ATTRIBUTES['*'] = ['style']
ALLOWED_STYLES = [
    'font-style',
    'font-weight',
    'text-decoration',
    'margin', 'margin-left', 'margin-right', 'margin-top', 'margin-bottom',
    'padding', 'padding-left', 'padding-right', 'padding-top', 'padding-bottom',
]


def bleach(text):
    return clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES, strip=True)
