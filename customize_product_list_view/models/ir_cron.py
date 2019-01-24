# -*- coding: utf-8 -*-
# Part of BiztechCS. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class CustomProductProduct(models.Model):
    _inherit = 'product.product'


    @api.model
    def update_product_type(self):
        products = self.search([])
        if products:
            for product in products:
                if product.qty_available > 1:
                    product.write({'type' : 'product'})