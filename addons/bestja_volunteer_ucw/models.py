# -*- coding: utf-8 -*-
from openerp import models, fields


class VolunteerUWStatus(models.Model):
    _name = 'volunteer.uw_status'
    name = fields.Char(required=True, string=u"nazwa")


class Volunteer(models.Model):
    _inherit = 'res.users'

    uw_status = fields.Many2one(
        'volunteer.uw_status',
        string=u"status na UW",
        ondelete='restrict',
    )

    def __init__(self, pool, cr):
        super(Volunteer, self).__init__(pool, cr)
        self._add_permitted_fields(level='privileged', fields={'uw_status'})
        self._add_permitted_fields(level='owner', fields={'uw_status'})
        self._remove_permitted_fields(level='privileged', fields={
            'email', 'phone', 'birthdate', 'place_of_birth',
            'citizenship', 'street_gov', 'street_number_gov', 'apt_number_gov', 'zip_code_gov', 'city_gov',
            'voivodeship_gov', 'country_gov', 'different_addresses', 'street', 'street_number', 'apt_number',
            'zip_code', 'city', 'voivodeship', 'country', 'document_id_kind', 'document_id'
        })


class Application(models.Model):
    _inherit = 'offers.application'

    # Access to those fields is restricted
    phone = fields.Char(groups='bestja_base.instance_admin')
    email = fields.Char(groups='bestja_base.instance_admin')
    age = fields.Integer(groups='bestja_base.instance_admin')


class Project(models.Model):
    _inherit = 'bestja.project'

    def _current_members(self):
        """
        Organizations shoudn't be able to add new people directly here.
        """
        return """[
            '|',
                '&',
                    ('projects', '!=', False),
                    ('projects', '=', id),
                '&',
                    ('coordinated_org', '!=', False),
                    ('coordinated_org', '=', organization),
            ]"""

    manager = fields.Many2one(domain=_current_members)
    members = fields.Many2many(domain=_current_members)
