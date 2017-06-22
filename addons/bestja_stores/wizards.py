# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions


class StoreStateWizard(models.TransientModel):
    _name = 'bestja.stores.state_wizard'

    STATES = [
        ('activated', u"aktywowany"),
        ('chain', u"wysłany do sieci"),
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

class StoreDeactivateWizard(models.TransientModel):
    _name = 'bestja.stores.deactivate_wizard'

    def _default_stores(self):
        return self.env['bestja_stores.store_in_project'].browse(self.env.context.get('active_ids'))

    stores = fields.Many2many(
        'bestja_stores.store_in_project',
        string=u"Wybrane sklepy",
        required=True,
        default=_default_stores,
        relation='bestja_deactivate_wizard_stores_rel',
    )

    @api.multi
    def deactivate(self):
        for store in self.stores:
            if store.state not in ['chain', 'proposed', 'activated']:
                raise exceptions.ValidationError(
                    u"""Można dezaktywować tylko sklepy zaakceptowane, proponowane lub wysłane do sieci.
                    Jednak sklep "{store}" ma status {state}.""".format(
                        store=store.store.name_get()[0][1],
                        state=store.display_state(),
                    )
                )
            if not store.user_can_moderate:
                raise exceptions.AccessError(
                    u"Nie masz uprawnień do deazktywacji sklepu \"{}\"!".format(store.store.name_get()[0][1])
                )
            store.sudo().state = 'deactivated'

class StoreToProjectWizard(models.TransientModel):
    _name = 'bestja.stores.to_project_wizard'

    def _default_stores(self):
        return self.env['bestja_stores.store'].browse(self.env.context.get('active_ids'))

    @api.one
    @api.depends('project', 'stores')
    def _compute_ignore_stores(self):
        stores = self.env['bestja_stores.store'].search([
            ('id', 'in', self.stores.ids),
            '|',
            ('state', '!=', 'accepted'),
            '!',
                ('id', '__free_for_project__', self.project.id),
        ])
        self.ignore_stores = [(6, 0, stores.ids)]

    stores = fields.Many2many(
        'bestja_stores.store',
        string=u"Wybrane sklepy",
        required=True,
        default=_default_stores,
        relation='bestja_to_project_wizard_stores_rel',
    )

    ignore_stores = fields.Many2many(
        'bestja_stores.store',
        string=u"Pominięte sklepy",
        help=u"Te sklepy są już dodane do projektu lub nie zostały jeszcze zaakceptowane i zostaną pominięte.",
        compute=_compute_ignore_stores
    )

    project = fields.Many2one(
        'bestja.project',
        required=True,
        string="Projekt",
        domain='''[
            ('use_stores', '=', True),
            ('date_stop', '>=', current_date),
            '|',
                ('organization.coordinator', '=', uid),
            '|',
                ('manager', '=', uid),
            '|',
                ('parent.organization.coordinator', '=', uid),
                ('parent.manager', '=', uid),
        ]''',
    )

    @api.multi
    def add_in_project(self):
        stores = self.env['bestja_stores.store'].search([
            ('id', 'in', self.stores.ids),
            ('state', '=', 'accepted'),
            ('id', '__free_for_project__', self.project.id),
        ])
        for store in stores:
            store_in_project = self.env['bestja_stores.store_in_project'].create({
                'store': store.id,
                'project': self.project.id,
            })
            store_in_project.add_days();
