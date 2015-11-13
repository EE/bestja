# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions


class ChainImportWizard(models.TransientModel):
    _name = 'bestja.stores.state_wizard'

    STATES = [
        ('activated', "aktywowany"),
        ('chain', "wysłany do sieci"),
    ]

    def _default_stores(self):
        return self.env['bestja_stores.store_in_project'].browse(self.env.context.get('active_ids'))

    stores = fields.Many2many(
        'bestja_stores.store_in_project',
        string=u"Wybrane sklepy",
        required=True,
        default=_default_stores,
        relation='bestja_state_wizard_stores_rel',
    )
    state = fields.Selection(STATES, string=u"Docelowy status")

    @api.multi
    def change_state(self):

        for store in self.stores:
            if not self.user_has_groups('bestja_base.instance_admin'):
                raise exceptions.AccessError("Nie masz uprawnień do zmiany statusu!")

            if self.state == 'activated' and store.state not in ['chain', 'proposed']:
                raise exceptions.ValidationError(
                    u"""Można aktywować tylko sklepy proponowane lub wysłane do sieci.
                    Jednak sklep "{store}" ma status {state}.""".format(
                        store=store.store.name_get()[0][1],
                        state=store.display_state(),
                    )
                )
            elif self.state == 'chain' and store.state != 'proposed':
                raise exceptions.ValidationError(
                    u"""Można wysłać do sieci tylko proponowane sklepy.
                    Jednak sklep "{store}" ma status {state}.""".format(
                        store=store.store.name_get()[0][1],
                        state=store.display_state(),
                    )
                )
            elif self.state not in ['activated', 'chain']:
                raise exceptions.ValidationError("Wybrano nieprawidłowy status")

            store.sudo().state = self.state
