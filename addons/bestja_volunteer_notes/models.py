# -*- coding: utf-8 -*-

from openerp import models, fields, api


class VolunteerWithNotes(models.Model):
    _inherit = 'res.users'

    notes = fields.One2many(
        'bestja.volunteer_note',
        inverse_name='user',
        groups="bestja_base.instance_admin,bestja_organization.coordinators",
    )

    def __init__(self, pool, cr):
        super(VolunteerWithNotes, self).__init__(pool, cr)
        self.add_permitted_fields(level='privileged', fields={'notes'})


class VolunteerNote(models.Model):
    _name = 'bestja.volunteer_note'

    @api.model
    def default_user(self):
        return self.env.context.get('active_id')

    @api.model
    def default_organization(self):
        return self.env.user.coordinated_org.id

    body = fields.Text(required=True, string="Treść")
    user = fields.Many2one(
        'res.users',
        required=True,
        default=default_user,
        string="Wolontariusz",
    )
    organization = fields.Many2one(
        'organization',
        default=default_organization,
    )

    @api.one
    def save_note(self):
        """
        A dummy method - can't figure out how to save a modal without
        executing a method. Odoo doesn't seem to provide us with an example.
        TODO: Figure it out.
        """
        pass
