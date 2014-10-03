from openerp import models


class BestJaSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'bestja.config.settings'
