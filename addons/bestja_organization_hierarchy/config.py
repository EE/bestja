# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BestJaSettings(models.TransientModel):
    _inherit = 'bestja.config.settings'

    master_org_id = fields.Many2one(
        'organization',
        required=True,
        domain=[('parent', '=', False)],
        string="Organizacja Główna",
        ondelete='restrict',
    )

    @api.model
    def get_default_values(self, fields=None):
        org_id = self.env['ir.model.data'].xmlid_to_res_id('bestja_organization_hierarchy.master_org')
        return {
            'master_org_id': org_id,
        }

    @api.one
    def set_values(self):
        org_ref = self.env['ir.model.data'].search([
            ('name', '=', 'master_org'),
            ('module', '=', 'bestja_organization_hierarchy'),
            ('model', '=', 'organization'),
        ])
        if org_ref:
            org_ref.res_id = self.master_org_id.id
            org_ref.clear_caches()
        else:
            self.env['ir.model.data'].create({
                'name': 'master_org',
                'module': 'bestja_organization_hierarchy',
                'model': 'organization',
                'res_id': self.master_org_id.id,
                'noupdate': True,
            })
