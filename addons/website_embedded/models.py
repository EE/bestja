# -*- coding: utf-8 -*-

from openerp import models, fields, api

from pyembed.core import PyEmbed, consumer as oembed_consumer
from requests.exceptions import RequestException


class EmbeddedObject(models.Model):
    _name = 'embedded_object'
    _order = 'sequence, create_date'

    KINDS = [
        ('elearning', "e-learning (dla wolontariuszy)"),
        ('elearning_partners', "e-learning (dla partnerów)"),
        ('biuletyn', "biuletyn wolontariuszy"),
    ]

    name = fields.Char(string=u"Tytuł", required=True)
    kind = fields.Selection(
        KINDS,
        required=True,
        string=u"Typ",
    )
    resource_url = fields.Char(
        string=u"Adres zasobu",
        required=True,
        help="np. adres filmu na YouTube lub numeru na issuu.com",
    )
    embed_code = fields.Text(string="Kod osadzenia", required=True)
    thumbnail_url = fields.Char(string=u"Adres miniaturki", required=True)
    description = fields.Html(sanitize=False, string=u"Opis")
    sequence = fields.Integer(default=1)

    @api.onchange('resource_url')
    def resource_change(self):
        error_message = None
        if self.resource_url:
            # Discover embed code using oEmbed
            oembed = PyEmbed()
            embed_code = None
            thumbnail_url = None
            try:
                oembed_urls = oembed.discoverer.get_oembed_urls(self.resource_url)
                if oembed_urls:
                    oembed_response = oembed_consumer.get_first_oembed_response(
                        oembed_urls,
                        max_width=800,
                        max_height=600
                    )
                    embed_code = oembed.renderer.render(self.resource_url, oembed_response)
                    thumbnail_url = getattr(oembed_response, 'thumbnail_url', '')

                if embed_code and thumbnail_url:
                    self.embed_code = embed_code
                    self.thumbnail_url = thumbnail_url
                else:
                    error_message = u'''Nie udało się pobrać kodu osadzenia (embed code) tego zasobu!'''

            except RequestException:
                error_message = u'''Wystąpił problem podczas łączenia z adresem "%s".
                            Sprawdź czy jest on poprawny.''' % self.resource_url

            if error_message:
                self.resource_url = ''
                self.embed_code = ''
                self.thumbnail_url = ''
                return {
                    'warning': {
                        'title': u'Problem z pobraniem informacji o zasobie!',
                        'message': error_message,
                    }
                }
