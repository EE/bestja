# -*- coding: utf-8 -*-
from itertools import product

from openerp import models, fields, api


class Wizard(models.TransientModel):
    _name = 'bestja.invitation_wizard'

    def _default_users(self):
        return self.env['res.users'].browse(self.env.context.get('active_ids'))

    users = fields.Many2many(
        'res.users',
        string=u"Wybrani użytkownicy",
        required=True,
        default=_default_users,
    )
    offers = fields.Many2many(
        'offer',
        required=True,
        string=u"Wybrane oferty",
        domain=[('state', '=', 'published')],
    )

    @api.one
    def send_invites(self):
        for offer, user in product(self.offers, self.users):
            offer.send(
                template='bestja_offers_invitations.msg_offer_invitation',
                recipients=user,
            )
