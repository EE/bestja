from openerp import models, api


class File(models.Model):
    _inherit = 'bestja.file'

    @api.model
    def create(self, vals):
        record = super(File, self).create(vals)
        if(record.project):
            recipients = [child.responsible_user for child in record.sudo().project.children]
            record.send(
                template='bestja_project_hierarchy_files.msg_new_file',
                recipients=recipients,
            )

        return record
