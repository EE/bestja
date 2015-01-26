# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from openerp.addons.website.models.website import slug

from .search import OffersIndex


class Offer(models.Model):
    _inherit = 'offer'

    def init(self, cr):
        # (Re)index after install / update
        ids = self.pool['offer'].search(
            cr, SUPERUSER_ID, [('state', '=', 'published')],
        )
        self.pool['offer'].whoosh_reindex(cr, SUPERUSER_ID, ids)

    @api.multi
    def whoosh_reindex(self):
        """
        Update/Add offers to the whoosh index.
        """
        # utility function for creating lists of names of objects
        # in a record set
        list_names = lambda rset: [r[1] for r in rset.name_get()]

        index = OffersIndex(dbname=self.env.cr.dbname)
        writer = index.get_writer()
        for offer in self.sudo():
            pk = unicode(offer.id)
            if offer.state == 'published':
                writer.update_document(
                    pk=pk,
                    slug=slug(self),
                    name=offer.name,
                    wishes=list_names(offer.wishes),
                    target_group=list_names(offer.target_group),
                    organization=offer.organization.name,
                )
            else:
                # Should not be public. Flag as removed from index.
                # Even if it wasn't there - no harm, no foul.
                writer.delete_by_term('pk', pk)
        writer.commit()

    @api.model
    def create(self, vals):
        record = super(Offer, self).create(vals)
        record.whoosh_reindex()
        return record

    @api.multi
    def write(self, vals):
        val = super(Offer, self).write(vals)
        self.whoosh_reindex()
        return val

    @api.multi
    def unlink(self):
        val = super(Offer, self).unlink()
        index = OffersIndex(dbname=self.env.cr.dbname)
        writer = index.get_writer()
        for offer in self:
            writer.delete_by_term('pk', unicode(offer.id))
        writer.commit()
        return val
