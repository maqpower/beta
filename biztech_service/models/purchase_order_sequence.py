# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

#Rearrange Po line in ascending order based on id
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    @api.multi
    def get_original_sequence(self):
        for rec in self:
            po_line = self.env['purchase.order.line'].search([
                            ('order_id', '=', rec.id)], order='id asc')
            count = 1
            for line in po_line:
                line.sequence=count
                count = count+1
        return  True