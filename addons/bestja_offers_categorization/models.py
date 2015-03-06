# -*- coding: utf-8 -*-
import logging

from psycopg2 import IntegrityError

from openerp import models, fields

_logger = logging.getLogger(__name__)


class OfferCategory(models.Model):
    _name = 'bestja.offer_category'

    name = fields.Char(string=u"nazwa", required=True)
    slug = fields.Char(string=u"identyfikator", required=True, index=True)

    _sql_constraints = [
        ('uffer_category_slug_uniq', 'unique("slug")', 'Identyfikator kategorii musi być unikalny!')
    ]


class Offer(models.Model):
    _inherit = 'offer'

    category = fields.Many2one('bestja.offer_category', required=True, index=True, string=u"kategoria")

    def _auto_init(self, cr, context=None):
        # Temporary disable `required` on the category field
        # to suppress setting it NOT NULL, which might
        # blow up if there are already existing offer objects.
        # (for example from demo data)
        self._columns['category'].required = False
        super(Offer, self)._auto_init(cr, context)
        self._columns['category'].required = True

        # Only now try adding the NOT NULL constraint
        try:
            cr.execute('ALTER TABLE offer ALTER COLUMN category SET NOT NULL', log_exceptions=False)
        except IntegrityError:
            # Adding constraint failed due to preexisting data.
            # Can't really do anything about it. Oh well...
            _logger.warning(
                "Table offer: unable to set a NOT NULL constraint on column 'category' due to preexisting data!)"
            )
        finally:
            cr.commit()
