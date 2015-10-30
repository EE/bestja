# -*- coding: utf-8 -*-
from StringIO import StringIO
import csv

from openerp import models, fields, api, exceptions


class ChainImportWizard(models.TransientModel):
    _name = 'bestja.stores.chain_import'

    STATUS_OPTIONS = ('tak', 'nie')  # order: accepted, rejected

    def _default_project(self):
        stores = self.env['bestja_stores.store_in_project'].browse(self.env.context.get('active_ids'))
        return stores[0].top_project

    project = fields.Many2one(
        'bestja.project',
        string=u"Projekt",
        required=True,
        domain="[('enable_stores', '=', True), ('organization_level', '=', 0)]",
        default=_default_project,
    )
    chain = fields.Many2one(
        'bestja_stores.chain',
        string=u"Sieć Handlowa",
        required=True,
    )
    import_file = fields.Binary(required=True, string=u"Plik CSV")

    @api.one
    def start_import(self):
        if not self.user_has_groups('bestja_base.instance_admin'):
            raise exceptions.AccessError("Nie masz uprawnień do tego importu!")

        csv_content = self.import_file.decode('base64')
        dialect = csv.Sniffer().sniff(csv_content)  # Try to guess the format
        rows = csv.reader(StringIO(csv_content), dialect)

        results = {}

        for row in rows:
            if len(row) < 2:
                continue

            chain_id = row[0].strip()
            status = row[1].strip()
            replacement = row[2].strip() if len(row) >= 3 else ""

            if status not in ChainImportWizard.STATUS_OPTIONS:
                continue  # Unrecognised status

            rejected = (status == ChainImportWizard.STATUS_OPTIONS[1])

            store = self.env['bestja_stores.store_in_project'].search([
                ('store.chain_id', '=', chain_id),
                ('top_project', '=', self.project.id),
                ('store.chain', '=', self.chain.id),
                ('state', '=', 'activated'),
            ])

            replacement_obj = None
            if replacement:
                replacement_obj = self.env['bestja_stores.store'].search([
                    ('chain_id', '=', replacement),
                    ('chain', '=', self.chain.id),
                ])

            if store:
                if rejected:  # rejected
                    store.sudo().write({
                        'state': 'deactivated',
                        'time_deactivated': fields.Datetime.now(),
                    })

                project = store.project
                if project.id not in results:
                    results[project.id] = {
                        'project': project,
                        'accepted': [],
                        'rejected': [],
                    }

                results[project.id]['rejected' if rejected else 'accepted'].append(
                    (store, replacement_obj)
                )

        for _, result in results.iteritems():
            self.env.ref('bestja_stores_chain_import.project_raport').with_context(
                obj=self,
                accepted=result['accepted'],
                rejected=result['rejected'],
            ).send(
                recipients=result['project'].responsible_user,
                sender=self.env.user,
            )
