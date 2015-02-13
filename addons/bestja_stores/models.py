# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
import re


class RetailChain(models.Model):
    _name = 'bestja_stores.chain'
    name = fields.Char(required=True)


class Store(models.Model):
    _name = 'bestja_stores.store'

    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
        'message_template.mixin',
    ]
    _protected_fields = ['state']

    STATES = [
        ('pending', "oczekujący"),
        ('accepted', "zaakceptowany"),
        ('rejected', "odrzucony"),
    ]

    @api.model
    def default_responsible(self):
        return self.env['organization'].search([
            ('level', '=', 1),
            '|',  # noqa
                ('coordinator', '=', self.env.uid),
                ('children.coordinator', '=', self.env.uid),
        ])

    @api.model
    def default_default_partner(self):
        return self.env['organization'].search([
            ('level', '>=', 1),
            ('coordinator', '=', self.env.uid),
        ])

    name = fields.Char(required=True, string="Nazwa")
    state = fields.Selection(STATES, default='pending', required=True, string="Status")
    chain = fields.Many2one('bestja_stores.chain', string="Sieć Handlowa")
    chain_id = fields.Char(
        groups='bestja_base.instance_admin',
        string="ID sklepu",
    )
    address = fields.Char(required=True, string="Ulica i numer")
    city = fields.Char(required=True, string="Miasto")
    voivodeship = fields.Many2one('volunteer.voivodeship', required=True, string="Województwo")
    responsible = fields.Many2one(
        'organization',
        domain='''[
            ('level', '=', 1),
            '|',
                ('coordinator', '=', uid),
            '|',
                ('parent.coordinator', '=', uid),
                ('children.coordinator', '=', uid),
        ]''',
        required=True,
        default=default_responsible,
        string="BŻ odpowiedzialny",
    )
    default_partner = fields.Many2one(
        'organization',
        domain='''[
            ('level', '>=', 1),
            '|',
                ('coordinator', '=', uid),
            '|',
                ('parent.coordinator', '=', uid),
                ('parent.parent.coordinator', '=', uid),
        ]''',
        default=default_default_partner,  # default ;)
        required=True,
        string="Domyślny partner",
    )
    user_can_moderate = fields.Boolean(compute="_compute_user_can_moderate")

    @api.one
    def set_accepted(self):
        self.state = 'accepted'
        self.send(
            template='bestja_stores.msg_store_accepted',
            recipients=self.default_partner.coordinator,
        )

    @api.one
    def set_rejected(self):
        self.state = 'rejected'
        self.send(
            template='bestja_stores.msg_store_rejected',
            recipients=self.default_partner.coordinator,
        )

    @api.one
    @api.constrains('default_partner', 'responsible')
    def _check_default_partner(self):
        if self.default_partner.parent != self.responsible and self.default_partner != self.responsible:
            raise exceptions.ValidationError("Domyślny partner musi podlegać wybranemu Bankowi Żywności!")

    @api.one
    @api.constrains('responsible', 'responsible.level')
    def _check_responsible_level(self):
        if self.responsible.level != 1:
            raise exceptions.ValidationError("Organizacja odpowiedzialna musi być Bankiem!")

    @api.one
    @api.depends('responsible', 'responsible.coordinator')
    def _compute_user_can_moderate(self):
        """
        Is current user authorized to moderate (accept/reject) the store?
        """
        self.user_can_moderate = (
            self.responsible.coordinator.id == self.env.uid or
            self.responsible.parent.coordinator.id == self.env.uid
        ) and self.responsible != self.default_partner

    @api.multi
    def _is_permitted(self):
        """
        Allow authorized users to modify protected fields
        """
        permitted = super(Store, self)._is_permitted()
        return permitted or self.user_can_moderate

    @api.model
    def _needaction_domain_get(self):
        """
        Show pending count in menu.
        """
        return [
            ('state', '=', 'pending'),
            ('responsible.coordinator', '=', self.env.uid),
        ]

    @api.model
    def create(self, vals):
        record = super(Store, self).create(vals)
        if record.responsible.coordinator.id == self.env.uid:
            record.sudo().state = 'accepted'
        else:
            record.send(
                template='bestja_stores.msg_store_from_partner',
                recipients=record.responsible.coordinator,
            )
        return record


class StoreInProject(models.Model):
    _name = 'bestja_stores.store_in_project'

    STATES = [
        ('waiting_bank', "oczekuje na bank"),
        ('waiting_partner', "oczekuje na partnera"),
        ('rejected', "odrzucony"),
        ('activated', "aktywowany"),
        ('deactivated', "dezaktywowany"),
    ]

    store = fields.Many2one('bestja_stores.store', required=True)
    project = fields.Many2one('bestja.project', required=True)
    top_project = fields.Many2one(
        'bestja.project',
        related='project.top_parent',
        store=True,
    )
    state = fields.Selection(STATES, default='waiting_bank', required=True)


class DayInStore(models.Model):
    _name = 'bestja_stores.day'

    store = fields.Many2one('bestja_stores.store_in_project', required=True)
    date = fields.Date(required=True)
    time_from = fields.Char(required=True)
    time_to = fields.Char(required=True)

    @api.one
    @api.constrains('time_from', 'time_to')
    def _check_hours(self):
        time_pattern = re.compile(r"^([0-1][0-9]|2[0-4]):[0-5][0-9]$")
        if not time_pattern.match(self.time_to) or not time_pattern.match(self.time_from):
            raise exceptions.ValidationError("Godzina musi być podana w formacie hh:mm!")
