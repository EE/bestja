# -*- coding: utf-8 -*-
from openerp import models, fields


class DriversLicense(models.Model):
    _name = 'volunteer.drivers_license'
    name = fields.Char(required=True, string=u"nazwa")


class Volunteer(models.Model):
    _inherit = 'res.users'

    drivers_license = fields.Many2many(
        'volunteer.drivers_license',
        string=u"prawo jazdy",
        ondelete='restrict',
    )
    sanepid = fields.Date(string=u"badania sanepidu")
    forklift = fields.Date(string=u"uprawnienia na wózek widłowy")

    def __init__(self, pool, cr):
        super(Volunteer, self).__init__(pool, cr)
        self._add_permitted_fields(
            level='privileged',
            fields={'drivers_license', 'sanepid', 'forklift'},
        )
        self._add_permitted_fields(
            level='owner',
            fields={'drivers_license', 'sanepid', 'forklift'},
        )


class Offer(models.Model):
    _inherit = 'offer'

    drivers_license = fields.Many2one('volunteer.drivers_license', string=u"Prawa jazdy")
    sanepid = fields.Boolean(string=u"Badania sanepidu")
    forklift = fields.Boolean(string=u"Uprawnienia na wózek widłowy")
