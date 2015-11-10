# -*- coding: utf-8 -*-
from openerp import models, fields


class StoreInProject(models.Model):
    _inherit = 'bestja_stores.store_in_project'

    DECISIONS = [
        ('activated', "aktywowany"),
        ('deactivated', "dezaktywowany"),
    ]

    chain_decision = fields.Selection(DECISIONS, string=u"Decyzja sieci")
    time_decision = fields.Datetime(string=u"Data importu")
    rejection_reason = fields.Text(string=u"Powód odrzucenia")
    rejection_replacement_id = fields.Char(
        string=u"Proponowany w zamian (ID sieci)",
        groups="bestja_base.instance_admin",
    )
    rejection_replacement_address = fields.Char(string=u"Proponowany w zamian (adres)")
    rejection_replacement_city = fields.Char(string=u"Proponowany w zamian (miasto)")
