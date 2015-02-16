# -*- coding: utf-8 -*-
from lxml import etree

from openerp import models, fields, api, exceptions, SUPERUSER_ID


class Organization(models.Model):
    _inherit = 'organization'
    _parent_name = 'parent'
    _order = 'parent_left'
    _parent_store = True

    def _allowed_parents(self):
        if self.user_has_groups('bestja_base.instance_admin'):
            return [('level', '<=', 1)]
        return [('level', '=', 1)]

    parent = fields.Many2one(
        'organization',
        domain=_allowed_parents,
        index=True,
        ondelete='restrict',
        string="Organizacja nadrzędna",
    )
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)
    children = fields.One2many(
        'organization',
        inverse_name='parent',
    )
    level = fields.Integer(
        compute='_compute_level',
        compute_sudo=True,
        store=True,
        string="Poziom w hierarchii organizacji"
    )

    @api.multi
    def write(self, vals):
        success = super(Organization, self).write(vals)
        if 'parent' in vals:
            self.coordinator._sync_coordinators_group()
        return success

    @api.one
    @api.depends('parent', 'parent.parent')
    def _compute_level(self):
        """
        Level of organization hierarchy. 0 = root level.
        """
        parent = self.parent
        i = 0
        while parent:
            parent = parent.parent
            i += 1
        self.level = i

    @api.one
    @api.constrains('parent')
    def _check_parent(self):
        """
        Only super admin is able to add primary (parentless) organizations.
        """
        if self.env.uid == SUPERUSER_ID:
            return
        if not self.parent:
            raise exceptions.ValidationError("Wybierz organizację nadrzędną!")

    @api.multi
    def _is_parent_coordinator(self):
        """
        Is the current user a coordinator of an parent organization?
        """
        return self.parent.id == self.env.user.coordinated_org.id

    @api.multi
    def _is_permitted(self):
        """
        Allow parent coordinators to modify protected fields
        """
        permitted = super(Organization, self)._is_permitted()
        return permitted or self._is_parent_coordinator()

    @api.model
    def fields_view_get(self, **kwargs):
        """
        Show header buttons to parent coordinators.
        """
        view = super(Organization, self).fields_view_get(**kwargs)
        if 'view_type' in kwargs and kwargs['view_type'] != 'form':
            return view

        doc = etree.XML(view['arch'])

        # Only coordinators and admins should see moderation buttons
        # TODO: because of the issue with conditional hiding
        # of view buttons, for now coordinators see those buttons
        # for ALL organizations - not only those they can moderate.
        if not (self.env.user.coordinated_org or self.user_has_groups('bestja_base.instance_admin')):
            buttons = doc.xpath("//header/button")
            for button in buttons:
                button.getparent().remove(button)

        view['arch'] = etree.tostring(doc)
        return view

    @api.one
    def send_registration_messages(self):
        self.send(
            template='bestja_organization.msg_registered',
            recipients=self.sudo().coordinator,
        )
        if self.parent:
            self.send(
                template='bestja_organization.msg_registered_admin',
                recipients=self.sudo().parent.coordinator,
            )


class UserWithOrganization(models.Model):
    _inherit = 'res.users'

    @api.one
    def _sync_coordinators_group(self):
        """
        Add / remove user from groups for coordinators of different levels.
        """
        super(UserWithOrganization, self)._sync_coordinators_group()

        for i in xrange(3):
            self._sync_group(
                group=self.env.ref('bestja_organization_hierarchy.coordinators_level' + str(i)),
                domain=[('coordinated_org.level', '=', i)],
            )
