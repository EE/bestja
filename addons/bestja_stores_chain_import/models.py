from openerp import models, fields, api, exceptions


class StoreInProject(models.Model):
    _inherit = 'bestja_stores.store_in_project'

    DECISIONS = [
        ('activated', "aktywowany"),
        ('deactivated', "dezaktywowany"),
    ]

    chain_decision = fields.Selection(DECISIONS, string=u"Decyzja sieci")
    time_decision = fields.Datetime(string=u"Data importu")
