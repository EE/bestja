# -*- coding: utf-8 -*-
import re
import datetime
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
    _permitted_groups = ['bestja_base.instance_admin']

    STATES = [
        ('pending', u"oczekujący"),
        ('accepted', u"zaakceptowany"),
        ('rejected', u"odrzucony"),
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

    name = fields.Char(required=True, string=u"Nazwa")
    state = fields.Selection(STATES, default='pending', required=True, string=u"Status")
    chain = fields.Many2one('bestja_stores.chain', string=u"Sieć Handlowa")
    chain_id = fields.Char(
        groups='bestja_project_hierarchy.managers_level0',
        string=u"ID sklepu",
    )
    address = fields.Char(required=True, string=u"Ulica i numer")
    city = fields.Char(required=True, string=u"Miasto")
    postal_code = fields.Char(size=6, required=True, string=u"Kod pocztowy")
    voivodeship = fields.Many2one('volunteer.voivodeship', required=True, string=u"Województwo")
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
        string=u"BŻ odpowiedzialny",
    )
    default_partner = fields.Many2one(
        'organization',
        domain='''[
            ('level', '>=', 1),
            '|',
                ('id', '=', responsible),
                ('parent', '=', responsible),
            '|',
                ('coordinator', '=', uid),
            '|',
                ('parent.coordinator', '=', uid),
                ('parent.parent.coordinator', '=', uid),
        ]''',
        default=_default_default_partner,  # default ;)
        required=True,
        string=u"Domyślny partner",
    )
    user_is_responsible = fields.Boolean(compute="_compute_user_is_responsible")
    user_is_federation = fields.Boolean(compute="_compute_user_is_federation")
    user_is_partner = fields.Boolean(compute="_compute_user_is_partner")
    in_projects = fields.One2many('bestja_stores.store_in_project', inverse_name='store')
    active = fields.Boolean(default=True)

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
            sender=self.env.user,
        )

    @api.one
    def archive(self):
        if not self.user_is_responsible and not self.user_is_federation and not self.user_is_partner:
            raise exceptions.AccessError("Nie masz uprawnień żeby archiwizować ten sklep!")
        self.sudo().active = False

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
    def _compute_user_is_responsible(self):
        """
        Is current user coordinator of a Bank responsible for this store.
        """
        self.user_is_responsible = (self.responsible.coordinator.id == self.env.uid)

    @api.one
    @api.depends('responsible', 'responsible.parent')
    def _compute_user_is_federation(self):
        self.user_is_federation = (
            self.responsible.parent.coordinator.id == self.env.uid and self.responsible.parent.level == 0
        )

    @api.one
    @api.depends('default_partner', 'default_partner.coordinator')
    def _compute_user_is_partner(self):
        self.user_is_partner = (self.default_partner.coordinator.id == self.env.uid)

    @api.model
    def _needaction_domain_get(self):
        """
        Show pending count in menu.
        """
        if not self.user_has_groups('bestja_base.instance_admin'):
            return False
        return [
            ('state', '=', 'pending'),
        ]

    @api.model
    def create(self, vals):
        record = super(Store, self).create(vals)
        record.send_group(
            template='bestja_stores.msg_new_store',
            group='bestja_base.instance_admin',
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
    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
        'message_template.mixin',
    ]
    _protected_fields = ['state', 'proposed_by', 'time_deactivated']
    _order = 'state'

    STATES = [
        ('waiting_bank', u"oczekuje na bank"),
        ('waiting_partner', u"oczekuje na partnera"),
        ('rejected', u"odrzucony"),
        ('activated', u"aktywowany"),
        ('deactivated', u"dezaktywowany"),
        ('proposed', u"proponowany"),
        ('chain', u"wysłany do sieci"),
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
        string=u"Sklep",
    )
    show_all_stores = fields.Boolean(
        string=u"pokaż wszystkie sklepy Banku",
        compute='_compute_show_all_stores',
        inverse='_inverse_show_stores',
    )
    hide_used_stores = fields.Boolean(
        string=u"ukryj wykorzystane w tej zbiórce",
        compute='_compute_hide_used_stores',
        inverse='_inverse_show_stores',
    )
    project = fields.Many2one(
        'bestja.project',
        required=True,
        default=_default_project,
        string="Projekt",
        domain='''[
            ('use_stores', '=', True),
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
            ('projects.top_parent', '=?', top_project),
            '|',
                ('coordinator', '=', uid),
            '|',
                ('projects.manager', '=', uid),
            '|',
                ('parent.coordinator', '=', uid),
                ('parent.projects.manager', '=', uid),
        ]''',
        string=u"Organizacja",
    )
    organization_name = fields.Char(related='organization.name', store=True, readonly=True, string=u"Nazwa organizacji")
    proposed_by = fields.Many2one('organization', oldname='activated_by', string=u"Organizacja potwierdzająca")
    proposed_time = fields.Datetime(string=u"Czas zaproponowania")
    top_project = fields.Many2one(
        'bestja.project',
        related='project.top_parent',
        store=True,
    )
    date_start = fields.Date(related='project.top_parent.date_start', readonly=True)
    date_stop = fields.Date(related='project.top_parent.date_stop', readonly=True)
    days = fields.One2many('bestja_stores.day', inverse_name='store')
    state = fields.Selection(STATES, default='waiting_bank', required=True, string=u"Status aktywacji")
    time_deactivated = fields.Datetime(string=u"Czas dezaktywacji")
    name = fields.Char(related='store.name', store=True, readonly=True)
    address = fields.Char(related='store.address', readonly=True)
    city = fields.Char(related='store.city', store=True, readonly=True)
    user_can_moderate = fields.Boolean(compute="_compute_user_can_moderate")
    user_is_federation = fields.Boolean(compute="_compute_is_federation")
    user_is_owner = fields.Boolean(compute="_compute_is_owner")
    user_is_bank = fields.Boolean(compute="_compute_is_bank")
    duplicated = fields.Char(compute="_compute_duplicated", string="Duplikat sklepu")

    @api.multi
    def display_state(self):
        return dict(StoreInProject.STATES).get(self.state)

    @api.model
    def _needaction_domain_get(self):
        """
        Show pending count in menu.
        """
        return [
            ('state', 'in', ['waiting_bank', 'waiting_partner']),
            '|',  # noqa
                ('project.manager', '=', self.env.uid),
            '|',
                ('project.organization.coordinator', '=', self.env.uid),
            '|',
                ('project.parent.manager', '=', self.env.uid),
                ('project.parent.organization.coordinator', '=', self.env.uid),
        ]

    @api.multi
    def is_bank(self):
        """
        Does the current user have privileges to act as bank
        (organization level 1) overseeing current project?
        """
        self.ensure_one()
        authorised_uids_1 = [
            self.sudo().project.organization.coordinator.id,
            self.sudo().project.manager.id,
        ]
        authorised_uids_2 = [
            self.sudo().project.parent.organization.coordinator.id,
            self.sudo().project.parent.manager.id,
        ]
        return (self.env.uid in authorised_uids_1 and self.sudo().project.organization_level == 1) or \
            (self.env.uid in authorised_uids_2 and self.sudo().project.organization_level == 2)

    @api.one
    @api.depends('project', 'project.parent')
    def _compute_is_bank(self):
        self.user_is_bank = self.is_bank()

    @api.multi
    def is_federation(self):
        """
        Does the current user have privileges to act as federation
        (organization level 0) overseeing current project?
        """
        self.ensure_one()
        authorised_uids = [
            self.sudo().project.top_parent.organization.coordinator.id,
            self.sudo().project.top_parent.manager.id,
        ]
        return self.env.uid in authorised_uids and self.sudo().project.top_parent.organization_level == 0

    @api.one
    @api.depends('project', 'project.parent')
    def _compute_is_federation(self):
        self.user_is_federation = self.is_federation()

    @api.multi
    def is_owner(self):
        """
        Does the current user have privileges to act as an owner
        of the current project.
        """
        self.ensure_one()
        authorised_uids = [
            self.sudo().project.organization.coordinator.id,
            self.sudo().project.manager.id,
        ]
        return self.env.uid in authorised_uids

    @api.one
    @api.depends('project')
    def _compute_is_owner(self):
        self.user_is_owner = self.is_owner()

    @api.one
    @api.depends('project', 'project.parent')
    def _compute_user_can_moderate(self):
        """
        Is current user authorized to moderate (accept/reject) the store?
        """
        if self.state == 'waiting_bank':
            self.user_can_moderate = self.is_bank() and self.sudo().project.organization_level == 2
        elif self.state == 'waiting_partner':
            self.user_can_moderate = self.is_owner() or self.is_bank()
        elif self.state in ('proposed', 'chain', 'activated'):
            self.user_can_moderate = self.is_owner() or self.is_bank() or self.is_federation()
        else:
            self.user_can_moderate = False

    @api.one
    @api.depends('top_project', 'store')
    def _compute_duplicated(self):
        """
        "duplikat" if there are previous StoresInProject in this project linked to the same store,
        empty otherwise. Used as a column for the XLS export.
        """
        stores = self.search([
            ('top_project', '=', self.top_project.id),
            ('state', 'not in', ['rejected', 'deactivated']),
            ('store', '=', self.store.id),
        ])
        if len(stores) > 1 and stores[0].id != self.id:
            self.duplicated = "duplikat"
        else:
            self.duplicated = ""

    @api.one
    def set_proposed(self):
        if not self.user_can_moderate:
            raise exceptions.AccessError("Nie masz uprawnień aby proponować ten sklep!")

        self.sudo().state = 'proposed'
        self.sudo().proposed_time = fields.Datetime.now()
        if self.is_owner():
            self.sudo().proposed_by = self.project.organization
        elif self.is_bank():
            self.sudo().proposed_by = self.project.parent.organization
        else:
            # This shouldn't really happen, but we can't forbid super user
            # from doing anything, so theoretically speaking it might...
            self.sudo().proposed_by = False

    @api.one
    def set_deactivated(self):
        if not self.user_can_moderate:
            raise exceptions.AccessError("Nie masz uprawnień aby dezaktywować ten sklep!")
        self.send(
            template='bestja_stores.msg_in_project_deactivated',
            recipients=self.top_project.responsible_user,
        )
        self.sudo().state = 'deactivated'
        self.sudo().time_deactivated = fields.Datetime.now()

    @api.one
    def set_rejected(self):
        if not self.user_can_moderate:
            raise exceptions.AccessError("Nie masz uprawnień aby dezaktywować ten sklep!")

        if self.state in ('proposed', 'chain', 'activated'):
            raise exceptions.AccessError("Uprzednio proponowany sklep nie może zostać odrzucony!")

        if self.state == 'waiting_bank':
            self.send(
                template='bestja_stores.msg_in_project_rejected',
                recipients=self.project.responsible_user,
            )
        self.sudo().state = 'rejected'

    @api.one
    @api.depends('project.organization')
    def _compute_organization(self):
        if isinstance(self.id, models.NewId):
            # can't use sudo with draft models,
            # changing enviroment loses their values
            self.organization = self.project.organization
        else:
            self.organization = self.sudo().project.organization

    @api.one
    def _compute_show_all_stores(self):
        self.show_all_stores = False

    @api.one
    def _compute_hide_used_stores(self):
        self.show_all_stores = True

    @api.one
    def _inverse_show_stores(self):
        # The field is used for temporary purposes,
        # no need to store its value
        pass

    @api.one
    def _inverse_organization(self):
        """
        If project is readonly the onchange('organization') below is not enough.
        """
        if self.project and self.project.organization != self.organization:
            organization_project = self.env['bestja.project'].search([
                ('organization', '=', self.organization.id),
                ('top_parent', '=', self.project.top_parent.id),
            ])
            self.project = organization_project.id

    @api.onchange('organization')
    def _onchange_organization(self):
        """
        Change project to a one from the same project hierarchy,
        but from the right organization.
        """
        if not self.organization:
            return  # Leave the previous project information

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

    @api.onchange('show_all_stores', 'hide_used_stores')
    def _onchange_show_all_stores(self):
        if self.show_all_stores and self.hide_used_stores:
            store_domain = """[
                ('state', '=', 'accepted'),
                ('id', '__free_for_project__', project),
                '|',
                    ('responsible', '=', organization),
                    ('responsible.children', '=', organization),
            ]"""
        elif self.show_all_stores:
            store_domain = """[
                ('state', '=', 'accepted'),
                '|',
                    ('responsible', '=', organization),
                    ('responsible.children', '=', organization),
            ]"""
        else:
            self.hide_used_stores = True
            store_domain = self._fields['store'].domain

        return {
            'domain': {
                'store': store_domain,
            }
        }

    @api.one
    @api.constrains('project', 'store')
    def _check_free_for_project(self):
        """
        Check if chosen store is free to be used in this project.
        """
        if self.is_bank() or self.is_federation():
            return  # Bank can overwrite this
        is_free = self.store.search_count([
            ('id', '=', self.store.id),
            ('id', '__free_for_project__', self.project.id),
        ])
        if not is_free:
            raise exceptions.ValidationError("Wybrany sklep jest już wykorzystany w tym projekcie!")

    @api.model
    def create(self, vals):
        record = super(StoreInProject, self).create(vals)
        if record.organization.level == 1 and record.is_owner():
            # Middle organization adding for itself
            record.sudo().state = 'proposed'
            record.sudo().proposed_time = fields.Datetime.now()
            record.sudo().proposed_by = record.project.organization.id
        elif record.organization.level == 2:
            if record.is_bank():
                # Middle organization adding for its child
                record.sudo().state = 'waiting_partner'
            else:
                record.sudo().state = 'waiting_bank'
        else:
            raise exceptions.AccessError("Nie masz uprawnień aby przypisać ten sklep!")

        if not record.days:
            # No days defined. Add the default set.
            record.add_days()
        return record

    @api.multi
    def write(self, vals):
        if 'store' in vals:
            raise exceptions.ValidationError("Pole sklep nie może być modyfikowane!")

        if ('project' in vals or 'organization' in vals) and not self.is_bank() and not self.is_federation():
            raise exceptions.ValidationError("Nie masz uprawnień żeby modyfikować pola projekt i organizacja!")
        return super(StoreInProject, self).write(vals)

    @api.one
    def add_days(self):
        """
        Create `bestja_stores.day` objects for all days in the project.
        """
        # Find a previous time an event was held in the store.
        # We want to find the second (yes!) day of the last event.
        # This will be used to copy default values for from / to times.
        previous_day = self.env['bestja_stores.day'].search(
            [
                ('store.store', '=', self.store.id),
                ('store.state', '=', 'activated'),
            ],
            order='store desc, date',
            limit=2,
        )
        previous_day = previous_day[1] if len(previous_day) > 1 else previous_day

        delta = datetime.timedelta(days=1)
        day = fields.Date.from_string(self.date_start)
        last_day = fields.Date.from_string(self.date_stop)
        while day <= last_day:
            self.env['bestja_stores.day'].create({
                'store': self.id,
                'date': fields.Date.to_string(day),
                'time_from': previous_day.time_from or "09:00",
                'time_to': previous_day.time_to or "18:00",
            })
            day += delta

    @api.one
    def add_days_dummy(self):
        """
        Action for a "Add days" button. But we add days on create anyway, so it
        doesn't actually have to do anything.
        """
        pass

    @api.one
    def name_get(self):
        name_string = u"{store} ({project})".format(store=self.store.name, project=self.project.name)
        return (self.id, name_string)

    def _auto_init(self, cr, context=None):
        todo_end = super(StoreInProject, self)._auto_init(cr, context)
        # Add UNIQUE index, since UNIQUE indexes (in opposite to UNIQUE constraints)
        # can include conditional clauses.
        if self._auto:
            cr.execute("DROP INDEX IF EXISTS unique_store_project;")
            cr.execute(
                """CREATE UNIQUE INDEX unique_store_project
                    ON bestja_stores_store_in_project(project,store)
                    WHERE (state NOT IN ('rejected', 'deactivated'));""")
        # Custom error message
        self.pool._sql_error['unique_store_project'] = \
            "Ten sklep jest już przypisany w tym projekcie do tej organizacji!"
        return todo_end


class DayInStore(models.Model):
    _name = 'bestja_stores.day'
    _order = 'date'

    store = fields.Many2one(
        'bestja_stores.store_in_project',
        required=True,
        ondelete='cascade',
        string=u"Sklep",
    )
    date = fields.Date(
        required=True,
        string=u"Dzień zbiórki",
    )
    time_from = fields.Char(
        string=u"Start"
    )
    time_to = fields.Char(
        string=u"Koniec",
    )
    # Computed versions of the above fields, to be able to
    # provide store specific defaults
    time_from_default = fields.Char(
        required=True,
        compute='_compute_time_from',
        inverse='_inverse_time_from',
        string=u"Start"
    )
    time_to_default = fields.Char(
        required=True,
        compute='_compute_time_to',
        inverse='_inverse_time_to',
        string=u"Koniec",
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
        needed for default hours. We want to find
        the second (yes!) day of the last event.
        """
        previous_day = self.env['bestja_stores.day'].search(
            [
                ('store.store', '=', self.store.store.id),
                ('store.state', '=', 'activated'),
            ],
            order='store desc, date',
            limit=2,
        )
        self.previous_day = previous_day[1].id if len(previous_day) > 1 else previous_day.id

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
    @api.constrains('time_from', 'time_to')
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

    stores = fields.One2many(
        'bestja_stores.store_in_project',
        inverse_name='project',
        groups='bestja_project.managers',
    )

    enable_stores = fields.Boolean(string=u"Projekt zbiórkowy?")
    use_stores = fields.Boolean(
        compute='_compute_use_stores',
        compute_sudo=True,
        search='_search_use_stores',
    )

    @api.one
    @api.depends('enable_stores', 'parent.enable_stores', 'parent.parent.enable_stores')
    def _compute_use_stores(self):
        self.use_stores = (
            self.enable_stores or
            self.parent.enable_stores or
            self.parent.parent.enable_stores
        )

    def _search_use_stores(self, operator, value):
        return [
            '|',  # noqa
                ('enable_stores', operator, value),
            '|',
                ('parent.enable_stores', operator, value),
                ('parent.parent.enable_stores', operator, value),
        ]
