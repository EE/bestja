# -*- coding: utf-8 -*-
import re
from operator import mul

from openerp import tools, models, fields, api, exceptions


class Organization(models.Model):
    _name = 'organization'
    _inherit = [
        'protected_fields.mixin',
        'ir.needaction_mixin',
        'message_template.mixin',
    ]
    _order = 'name'
    _protected_fields = ['state', 'coordinator']
    _permitted_groups = ['bestja_base.instance_admin']

    STATES = [
        ('pending', u"oczekująca na akceptację"),
        ('approved', u"zaakceptowana"),
        ('rejected', u"odrzucona"),
        ('archived', u"zarchiwizowana"),
    ]

    name = fields.Char(string=u"Nazwa", required=True)
    state = fields.Selection(
        STATES,
        default='pending',
        string=u"Stan",
    )
    krs = fields.Char(string=u"KRS")
    regon = fields.Char(string=u"REGON")
    nip = fields.Char(string=u"NIP")
    street_address = fields.Char(string=u"Ulica", required=True)
    city = fields.Char(string=u"Miejscowość", required=True)
    street_number = fields.Char(string=u"Numer budynku", required=True)
    apartment_number = fields.Char(string=u"Numer mieszkania")
    postal_code = fields.Char(size=6, required=True, string=u"Kod pocztowy")
    address = fields.Text(
        compute='_compute_address',
        string=u"Pełen adres",
    )
    email = fields.Char(string=u"E-mail", required=True)
    phone = fields.Char(required="True", string=u"Numer Telefonu")
    phone_extension = fields.Char(size=10, string=u"Numer wewnętrzny")
    www = fields.Char(string=u"WWW")
    fbfanpage = fields.Char(string=u"Fanpage na FB")
    volunteers = fields.Many2many(
        'res.users',
        relation='organization_volunteers_rel',
        column1='organization',
        column2='volunteer',
        string=u"Wolontariusze"
    )
    coordinator = fields.Many2one(
        'res.users', ondelete='restrict',
        string=u"Koordynator",
        default=lambda self: self.env.user,
        domain="['|', ('coordinated_org', '=', id), ('coordinated_org', '=', False)]",
    )
    coordinator_uid = fields.Integer(compute='_compute_coordinator_uid')
    active = fields.Boolean(
        compute='_compute_active',
        store=True,
    )
    organization_description = fields.Text(string=u"Opis Organizacji")
    image = fields.Binary()
    image_medium = fields.Binary(compute='_compute_image_medium', inverse='_inverse_image_medium', store=True)

    _sql_constraints = [
        ('coordinator_uniq', 'unique(coordinator)', 'Jedna osoba nie może koordynować wielu organizacji!'),
        ('nip_uniq', 'unique(nip)', 'Istnieje już organizacja z takim numerem NIP!'),

    ]

    @api.multi
    @api.depends('image')
    def _compute_image_medium(self):
        self.image_medium = tools.image_resize_image_medium(self.image)

    @api.one
    @api.depends('image_medium')
    def _inverse_image_medium(self):
        self.image = tools.image_resize_image_big(self.image_medium)

    @api.one
    @api.depends('state')
    def _compute_active(self):
        self.active = (self.state == 'approved')

    @api.one
    @api.depends('coordinator')
    def _compute_coordinator_uid(self):
        """
        Needed for `fonts` attribute on the tree view.
        """
        self.coordinator_uid = self.coordinator.id

    @api.one
    @api.depends('name', 'street_address', 'street_number', 'apartment_number', 'postal_code', 'city')
    def _compute_address(self):
        self.address = u"""{self.name}
{self.street_address} {self.street_number}{apartment}
{self.postal_code} {self.city}""".format(
            self=self,
            apartment=u" lok. " + self.apartment_number if self.apartment_number else "",
        )

    @api.one
    @api.constrains('email')
    def _check_email(self):
        email = self.email
        if not re.match(r"^[_a-z0-9-]+([.+][_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email):
            raise exceptions.ValidationError("Adres e-mail jest niepoprawny.")

    @staticmethod
    def _is_gov_id_valid(number, weights):
        """
        Check governmental identification number.
        `weights` is a list of weights for subsequent digits.
        """
        try:
            digits = map(int, number)
        except ValueError:
            return False  # only proper numbers!

        if len(digits) != len(weights) + 1:
            return False

        control_sum = sum(map(mul, digits[:-1], weights)) % 11
        control_sum = 0 if control_sum == 10 else control_sum
        return control_sum == digits[-1]

    def _clean_field_value(self, field_name):
        """
        Removes redundant characters from numeric fields
        """
        useless_chars = '-. /'
        value = str(getattr(self, field_name))
        if any(char in value for char in useless_chars):
            value = value.translate(None, useless_chars)
            setattr(self, field_name, value)

    @api.one
    @api.constrains('nip')
    def _check_nip(self):
        weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
        self._clean_field_value('nip')
        if self.nip and not self._is_gov_id_valid(self.nip, weights):
            raise exceptions.ValidationError("Niepoprawny NIP.")

    @api.one
    @api.constrains('regon')
    def _check_regon(self):
        weights = (8, 9, 2, 3, 4, 5, 6, 7)
        self._clean_field_value('regon')
        if self.regon and len(self.regon) > 9:
            weights = (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8)

        if self.regon and not self._is_gov_id_valid(self.regon, weights):
            raise exceptions.ValidationError("Niepoprawny REGON.")

    @api.one
    @api.constrains('krs')
    def _check_krs(self):
        self._clean_field_value('krs')
        if self.krs and (len(self.krs) != 10 or not self.krs.isdigit()):
            raise exceptions.ValidationError("Niepoprawny KRS.")

    @api.one
    def set_approved(self):
        self.state = 'approved'
        self.coordinator._sync_coordinators_group()
        self.send(
            template='bestja_organization.msg_approved',
            recipients=self.coordinator,
        )

    @api.one
    def set_rejected(self):
        self.state = 'rejected'
        self.coordinator._sync_coordinators_group()
        self.send(
            template='bestja_organization.msg_rejected',
            recipients=self.coordinator,
            sender=self.env.user,
        )

    @api.one
    def set_archived(self):
        self.state = 'archived'
        self.coordinator._sync_coordinators_group()

    @api.one
    def _send_registration_messages(self):
        self.send(
            template='bestja_organization.msg_registered',
            recipients=self.coordinator,
        )

        self.send_group(
            template='bestja_organization.msg_registered_admin',
            group='bestja_base.instance_admin',
        )

    @api.model
    def create(self, vals):
        record = super(Organization, self).create(vals)
        record._send_registration_messages()
        record.coordinator._sync_coordinators_group()
        return record

    @api.multi
    def write(self, vals):
        old_coordinator = self.coordinator
        val = super(Organization, self).write(vals)
        if 'coordinator' in vals:
            self.coordinator._sync_coordinators_group()
            old_coordinator._sync_coordinators_group()
            self.send(
                template='bestja_organization.msg_coordinator',
                recipients=self.coordinator,
            )
        return val

    @api.multi
    def unlink(self):
        coordinator = self.coordinator
        val = super(Organization, self).unlink()
        coordinator._sync_coordinators_group()
        return val

    @api.model
    def _needaction_domain_get(self):
        """
        Show pending organizations count in menu.
        """
        return [
            ('state', '=', 'pending'),
            ('active', '=?', False),
            ('coordinator', '!=', self.env.uid),
        ]


class UserWithOrganization(models.Model):
    _inherit = 'res.users'

    coordinated_org = fields.One2many('organization', inverse_name='coordinator')
    organizations = fields.Many2many(
        'organization',
        relation='organization_volunteers_rel',
        column1='volunteer',
        column2='organization',
        string=u"Organizacje"
    )

    def __init__(self, pool, cr):
        super(UserWithOrganization, self).__init__(pool, cr)
        self._add_permitted_fields(level='all', fields={'coordinated_org'})
        self._add_permitted_fields(level='owner', fields={'organizations'})
        self._add_permitted_fields(level='privileged', fields={'organizations'})

    @api.one
    def _sync_coordinators_group(self):
        """
        Add / remove user from the coordinators group, based on whether
        she have an active organization associated.
        """
        self._sync_group(
            group=self.env.ref('bestja_organization.coordinators'),
            domain=[('coordinated_org.active', '=', True)],
        )

    @api.one
    @api.depends('organizations')
    def _compute_user_access_level(self):
        """
        Access level that the current (logged in) user has for the object.
        Either "owner", "admin", "privileged" or None.
        """
        super(UserWithOrganization, self)._compute_user_access_level()
        if not self.user_access_level and self.user_has_groups('bestja_organization.coordinators') \
                and (self.env.user.coordinated_org.id in self.sudo().organizations.ids):
            self.user_access_level = 'privileged'
