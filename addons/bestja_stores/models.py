# -*- coding: utf-8 -*-
import re

from openerp import models, fields, api, exceptions


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
    def _default_responsible(self):
        return self.env['organization'].search([
            ('level', '=', 1),
            '|',  # noqa
                ('coordinator', '=', self.env.uid),
                ('children.coordinator', '=', self.env.uid),
        ])

    @api.model
    def _default_default_partner(self):
        return self.env['organization'].search([
            ('level', '>=', 1),
            ('coordinator', '=', self.env.uid),
        ])

    name = fields.Char(required=True, string="Nazwa")
    state = fields.Selection(STATES, default='pending', required=True, string="Status")
    chain = fields.Many2one('bestja_stores.chain', string="Sieć Handlowa")
    chain_id = fields.Char(
        groups='bestja_project_hierarchy.managers_level0',
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
        default=_default_responsible,
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
        default=_default_default_partner,  # default ;)
        required=True,
        string="Domyślny partner",
    )
    user_can_moderate = fields.Boolean(compute="_compute_user_can_moderate")
    in_projects = fields.One2many('bestja_stores.store_in_project', inverse_name='store')

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
    @api.constrains('responsible')
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

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # Adds a `__free_for_project__` domain operator. Yeah - adding a domain operator
        # to a single model to support a particular case seems like an act of complete
        # desperation. That's because it is an act of complete desperation.
        #
        # The problem is it seems there is no way to create an Odoo domain that
        # would select objects that are NOT in many2many relation with a particular
        # object.
        #
        # Example usage of the new operator:
        # [('store', '__free_for_project__', project)]
        #
        # It will select stores that are free to use with the `project` (are not
        # already reserved).
        for i, arg in enumerate(args):
            if isinstance(arg, (tuple, list)) and len(arg) == 3 and arg[1] == '__free_for_project__':
                left, _, right = arg
                project = self.env['bestja.project'].browse([right])
                reserved_inprojects = self.env['bestja_stores.store_in_project'].search([
                    ('top_project', '=', project.top_parent.id),
                    ('state', 'not in', ['rejected', 'deactivated']),
                ])
                reserved_stores = {record.store.id for record in reserved_inprojects}
                args[i] = (left, 'not in', list(reserved_stores))

        return super(Store, self)._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )

    @api.one
    def name_get(self):
        name_string = ", ".join([self.name, self.address, self.city])
        return (self.id, name_string)


class StoreInProject(models.Model):
    _name = 'bestja_stores.store_in_project'

    STATES = [
        ('waiting_bank', "oczekuje na bank"),
        ('waiting_partner', "oczekuje na partnera"),
        ('rejected', "odrzucony"),
        ('activated', "aktywowany"),
        ('deactivated', "dezaktywowany"),
    ]

    def _default_project(self):
        if self.env.context.get('active_model') == 'bestja.project':
            return self.env.context.get('active_id')
        return self.env.context.get('default_project')

    store = fields.Many2one(
        'bestja_stores.store',
        required=True,
        domain='''[
            ('state', '=', 'accepted'),
            ('default_partner', '=', organization),
            ('id', '__free_for_project__', project),
        ]''',  # a custom operator defined in Store's _search method
        string="Sklep",
    )
    show_all_stores = fields.Boolean(
        string="pokazuj wszystkie sklepy",
        compute='_compute_show_all_stores',
        inverse='_inverse_show_all_stores',
    )
    project = fields.Many2one(
        'bestja.project',
        required=True,
        default=_default_project,
        # TODO: Is this a zbiórkowy project?
        domain='''[
            ('organization', '=', organization),
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
    organization = fields.Many2one(
        'organization',
        compute='_compute_organization',
        inverse='_inverse_organization',
        required=True,
        domain='''[
            ('level', '>=', 1),
            '|',
                ('coordinator', '=', uid),
            '|',
                ('projects.manager', '=', uid),
            '|',
                ('parent.coordinator', '=', uid),
                ('parent.projects.manager', '=', uid),
        ]''',
        string="Organizacja",
    )
    activated_by = fields.Many2one('organization', string="Organizacja aktywująca")
    top_project = fields.Many2one(
        'bestja.project',
        related='project.top_parent',
        store=True,
    )
    date_start = fields.Date(related='project.top_parent.date_start', readonly=True)
    date_stop = fields.Date(related='project.top_parent.date_stop', readonly=True)
    days = fields.One2many('bestja_stores.day', inverse_name='store')
    state = fields.Selection(STATES, default='waiting_bank', required=True, string="Status")
    name = fields.Char(related='store.name', readonly=True)
    address = fields.Char(related='store.address', readonly=True)
    city = fields.Char(related='store.city', readonly=True)

    @api.one
    @api.depends('project.organization')
    def _compute_organization(self):
        self.organization = self.project.organization

    @api.one
    def _compute_show_all_stores(self):
        self.show_all_stores = False

    @api.one
    def _inverse_show_all_stores(self):
        # The field is used for temporary purposes,
        # no need to store its value
        pass

    @api.one
    def _inverse_organization(self):
        # Changing organization should only have client side consequences.
        # (it is used in project field's domain).
        pass

    @api.onchange('organization')
    def _onchange_organization(self):
        """
        Change project to a one from the same project hierarchy,
        but from the right organization.
        """
        if isinstance(self.project.id, models.NewId):
            # self.project is in draft mode, which unfortunately means
            # we can't access its id (and we need it!).
            # Fortunately it also means that its the currently opened
            # project and we can get its id from context :)
            current_project = self.env.context.get('default_project')
            project = self.env['bestja.project'].browse([current_project])
        else:
            project = self.project

        if project:
            organization_project = self.env['bestja.project'].search([
                ('organization', '=', self.organization.id),
                ('top_parent', '=', project.top_parent.id),
            ])
            self.project = organization_project.id

    @api.onchange('show_all_stores')
    def _onchange_show_all_stores(self):
        if self.show_all_stores:
            store_domain = """[
                ('state', '=', 'accepted'),
                ('id', '__free_for_project__', project),
                '|',
                    ('responsible', '=', organization),
                    ('responsible.children', '=', organization),
            ]"""
        else:
            store_domain = self._fields['store'].domain

        return {
            'domain': {
                'store': store_domain,
            }
        }


class DayInStore(models.Model):
    _name = 'bestja_stores.day'
    _order = 'date'

    store = fields.Many2one(
        'bestja_stores.store_in_project',
        required=True,
        ondelete='cascade',
        string="Sklep",
    )
    date = fields.Date(
        required=True,
        string="Dzień zbiórki",
    )
    time_from = fields.Char(
        string="Start"
    )
    time_to = fields.Char(
        string="Koniec",
    )
    # Computed versions of the above fields, to be able to
    # provide store specific defaults
    time_from_default = fields.Char(
        required=True,
        compute='_compute_time_from',
        inverse='_inverse_time_from',
        string="Start"
    )
    time_to_default = fields.Char(
        required=True,
        compute='_compute_time_to',
        inverse='_inverse_time_to',
        string="Koniec",
    )
    previous_day = fields.Many2one(
        'bestja_stores.day',
        compute='_compute_previous_day',
    )

    _sql_constraints = [
        ('date_uniq', 'unique(date, store)', 'Można podać tylko jedną datę zbiórki dla danego sklepu!')
    ]

    @api.one
    @api.depends('store.store')
    def _compute_previous_day(self):
        """
        Previously accepted day in the same store,
        needed for default hours
        """
        previous_day = self.env['bestja_stores.day'].search(
            [
                ('store.store', '=', self.store.store.id),
                ('store.state', '=', 'activated'),
            ],
            order='store desc, date',
            limit=1,
        )
        self.previous_day = previous_day.id

    @api.one
    @api.depends('time_from', 'previous_day', 'store')
    def _compute_time_from(self):
        """
        If time_from is set just present it.
        If not present a default value - the previous time
        from the same store in the most recent project.
        """
        if self.time_from:
            self.time_from_default = self.time_from
        else:
            self.time_from_default = self.previous_day.time_from

    @api.one
    @api.depends('time_to', 'previous_day', 'store')
    def _compute_time_to(self):
        """
        If time_to is set just present it.
        If not present a default value - the previous time
        from the same store in the most recent project.
        """
        if self.time_to:
            self.time_to_default = self.time_to
        else:
            self.time_to_default = self.previous_day.time_to

    @api.one
    def _inverse_time_from(self):
        self.time_from = self.time_from_default

    @api.one
    def _inverse_time_to(self):
        self.time_to = self.time_to_default

    @api.one
    @api.constrains('time_from_default', 'time_to_default')
    def _check_hours(self):
        time_pattern = re.compile(r"^([0-1][0-9]|2[0-4]):[0-5][0-9]$")
        if not time_pattern.match(self.time_to_default) or not time_pattern.match(self.time_from_default):
            raise exceptions.ValidationError("Godzina musi być podana w formacie hh:mm!")

    @api.one
    @api.constrains('date')
    def _check_date_in_project(self):
        if not self.store.top_project.date_start <= self.date <= self.store.top_project.date_stop:
            raise exceptions.ValidationError("Wybrano dzień poza czasem trwania projektu!")


class ProjectWithStores(models.Model):
    _inherit = 'bestja.project'

    stores = fields.One2many('bestja_stores.store_in_project', inverse_name='project')
