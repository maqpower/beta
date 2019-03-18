from odoo import models, api, fields, _

class res_partner(models.Model):
    _inherit = "res.partner"
    
    @api.multi
    def hide_create_button(self):
        module_category_id= self.env['ir.module.category'].search([('name','=','Extra Rights')])
        if module_category_id:
            group_ids = self.env['res.groups'].search([('name','=','Create'), ('category_id', '=', module_category_id.id)])
            uid=self.env.user
            for group_id in group_ids:
                self._cr.execute("select uid from res_groups_users_rel where gid=%s", (group_id.id,))
                r = self._cr.fetchall()
                for user_id in r:
                    if uid.id == user_id[0]:
                        return True
        return False
    
    @api.multi
    def hide_edit_button(self):
        module_category_id= self.env['ir.module.category'].search([('name','=','Extra Rights')])
        if module_category_id:
            edit_group_ids = self.env['res.groups'].search([('name','in',['Edit','Create']), ('category_id', '=', module_category_id.id)])
            uid=self.env.user
            for group_id in edit_group_ids:
                self._cr.execute("select uid from res_groups_users_rel where gid=%s", (group_id.id,))
                r = self._cr.fetchall()
                for user_id in r:
                    if uid.id == user_id[0]:
                        return True
        return False
    
    @api.multi
    def hide_delete_button(self):
        module_category_id= self.env['ir.module.category'].search([('name','=','Extra Rights')])
        if module_category_id:
            delete_group_ids = self.env['res.groups'].search([('name','=','Delete'), ('category_id', '=', module_category_id.id)])
            uid=self.env.user
            for group_id in delete_group_ids:
                self._cr.execute("select uid from res_groups_users_rel where gid=%s", (group_id.id,))
                r = self._cr.fetchall()
                for user_id in r:
                    if uid.id == user_id[0]:
                        return True
        return False
    
    @api.multi
    def display_name_get(self):
        for partner in self:
            ship_ids = self.search([('type','=','delivery'),('name','=',''),('active','=',False)])
            if partner.type == "delivery" and partner.active == False:
                for shipping_ids in ship_ids:
                    shipping_ids._compute_display_name()