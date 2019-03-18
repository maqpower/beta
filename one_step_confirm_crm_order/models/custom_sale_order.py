# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class sale_order(models.Model):
    _inherit = "sale.order"
        
    is_direct_crm_confirm = fields.Boolean(string='Is Direct CRM confirm order', default=False)
    is_cancel_crm_order = fields.Boolean(string="Coming from cancelled crm order", default=False)

    @api.model
    def create(self, vals):
        ctx = self._context
        if ctx and ctx.get('default_other_field'):
            vals.update({
                'is_direct_crm_confirm': True
                })

        res = super(sale_order, self).create(vals)
        if vals.get('order_line') and ctx.get('default_other_field'):
            res.action_confirm()

        return res

    @api.multi
    def write(self, vals):
        res = super(sale_order, self).write(vals)
        for rec in self:
            if rec.is_direct_crm_confirm and rec.order_line:
                if rec.state in ['draft', 'sent'] and not rec.is_cancel_crm_order:
                    rec.action_confirm()
        return res


    @api.multi
    def action_draft(self):
        res = super(sale_order, self).action_draft()
        self.write({
            'is_cancel_crm_order' : True
            })

        return res