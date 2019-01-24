# -*- coding: utf-8 -*-

from odoo import api, fields, models

class stock_location(models.Model):
    _inherit = 'stock.location'

    is_fleet_location = fields.Boolean(string="Is Fleet Location")
    is_initial_load_transfer=fields.Boolean(string="Is Initial Load Transfer")
    fleet_product_id=fields.Many2one("fleet.product")

    @api.model
    def create(self, vals):
        res = super(stock_location, self).create(vals)
        context = self.env.context
        if context and context.get('is_fleet_location') == True:
            res['is_fleet_location'] = True
        return res
