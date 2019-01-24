# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import Warning,UserError, ValidationError
from datetime import datetime, timedelta

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    initial_qty=fields.Float("Initial Qty",compute='_get_initial_qty',default=0.0)
    initial_qty_relate=fields.Float("Initial Qty",default=0.0)
    re_order_qty_relate =fields.Float("Re order  Qty",compute='_get_initial_qty',default=0.0)
    re_order_qty = fields.Float(string="Re Order Qty")
    @api.one
    def _get_initial_qty(self):
        initial_load_product =[]
        for quant in self:
            if quant.location_id.fleet_product_id:
                fleet_prod_obj = self.env['fleet.product'].search([('id','=',self.location_id.fleet_product_id.id)])
                for prod_line in fleet_prod_obj.fleet_product_line:
                    if quant.product_id.id == prod_line.product_id.id:
                        self.initial_qty = prod_line.product_qty
                        self.re_order_qty_relate = prod_line.re_order_qty
                        self.write({'initial_qty_relate': prod_line.product_qty,'re_order_qty':prod_line.re_order_qty})
