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

    @api.multi
    def start_import(self):
        if not self.user_has_groups('bestja_base.instance_admin'):
            raise exceptions.AccessError("Nie masz uprawnień do tego importu!")

        csv_content = self.import_file.decode('base64')
        dialect = csv.Sniffer().sniff(csv_content)  # Try to guess the format
        rows = csv.reader(StringIO(csv_content), dialect)

        results = {}

        for line_no, row in enumerate(rows, start=1):
            try:
                row = [unicode(cell, 'utf-8') for cell in row]
            except UnicodeDecodeError:
                raise exceptions.ValidationError(
                    """Problem z kodowaniem znaku w linii {}.
                    Upewnij się, że plik CSV używa kodowania UTF-8""".format(line_no)
                )
            if len(row) < 2:
                continue

            chain_id = row[0].strip()
            status = row[1].strip().lower()
            reason = row[2].strip() if len(row) >= 3 else ""
            replacement_id = row[3].strip() if len(row) >= 4 else ""
            replacement_name = ""
            if len(row) >= 6 and row[4] and row[5]:
                replacement_name = u"{}, {}".format(row[4], row[5])

            if status not in ChainImportWizard.STATUS_OPTIONS:
                continue  # Unrecognised status

            rejected = (status == ChainImportWizard.STATUS_OPTIONS[1])

            stores = self.env['bestja_stores.store_in_project'].search([
                ('store.chain_id', '=', chain_id),
                ('top_project', '=', self.project.id),
                ('store.chain', '=', self.chain.id),
                ('state', '=', 'activated'),
            ])

            replacement_obj = None
            if replacement_id:
                replacement_obj = self.env['bestja_stores.store'].search([
                    ('chain_id', '=', replacement_id),
                    ('chain', '=', self.chain.id),
                ])

            for store in stores:
                if rejected:
                    store.sudo().write({
                        'state': 'deactivated',
                        'chain_decision': 'deactivated',
                        'time_deactivated': fields.Datetime.now(),
                        'time_decision': fields.Datetime.now(),
                    })
                else:
                    store.sudo().write({
                        'chain_decision': 'activated',
                        'time_decision': fields.Datetime.now(),
                    })

                store_dic = {
                    'store_obj': store,
                    'replacement_obj': replacement_obj,
                    'replacement_name': replacement_name,
                    'reason': reason,
                }

                project = store.project
                if project.id not in results:
                    results[project.id] = {
                        'project': project,
                        'accepted': [],
                        'rejected': [],
                    }
                results[project.id]['rejected' if rejected else 'accepted'].append(store_dic)

                # Add to Bank's report
                if project.organization_level == 2 and project.parent:
                    parent = project.parent
                    if parent.id not in results:
                        results[parent.id] = {
                            'project': parent,
                            'accepted': [],
                            'rejected': [],
                        }
                    results[parent.id]['rejected' if rejected else 'accepted'].append(store_dic)

        for _, result in results.iteritems():
            self.env.ref('bestja_stores_chain_import.project_raport').with_context(
                obj=self,
                accepted=result['accepted'],
                rejected=result['rejected'],
                organization=result['project'].organization,
            ).send(
                recipients=result['project'].responsible_user,
                sender=self.env.user,
            )
