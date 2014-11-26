# -*- coding: utf-8 -*-

from openerp import models, api, exceptions, SUPERUSER_ID


class ProtectedFieldsMixin(models.AbstractModel):
    """
    This Mixin allows model creators to specify a list
    of "protected fields" (`_protected_fields` property).

    Protected fields can be read by everyone with read
    permissions to the object, but can be modified
    only by users in groups listed in `_permitted_groups`
    or with ids listed in `_permitted_user_ids`.
    """
    _name = 'protected_fields.mixin'

    _protected_fields = []
    _permitted_user_ids = [SUPERUSER_ID, ]
    _permitted_groups = []

    @api.model
    def _is_permitted(self):
        """
        Is the current user permitted to modify protected fields?

        For more advanced rules, you can modify this method in your model.
        """
        # User permissions
        if self.env.user.id in self._permitted_user_ids:
            return True

        # Group permissions
        permitted_group_ids = [self.env.ref(group) for group in self._permitted_groups]
        user_group_ids = self.env.user.groups_id.ids
        return any(group in permitted_group_ids for group in user_group_ids)

    @api.model
    def _check_field_permissions(self, vals):
        if not self._is_permitted():
            for field_name in self._protected_fields:
                if field_name in vals:
                    raise exceptions.AccessError(
                        "You don't have permissions to modify the {} field!".format(field_name)
                    )

    @api.model
    def create(self, vals):
        self._check_field_permissions(vals)
        record = super(ProtectedFieldsMixin, self).create(vals)
        return record

    @api.multi
    def write(self, vals):
        self._check_field_permissions(vals)
        record = super(ProtectedFieldsMixin, self).write(vals)
        return record
