# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from dateutil import relativedelta
from datetime import datetime, timedelta

class product_product(models.Model):
    _inherit ='product.product'
    
    posx = fields.Integer('Corridor (X)',related = 'property_stock_inventory.posx', default=0, help="Optional localization details, for information purpose only")
    posy = fields.Integer('Shelves (Y)', related = 'property_stock_inventory.posy',default=0, help="Optional localization details, for information purpose only")
    posz = fields.Integer('Height (Z)',related = 'property_stock_inventory.posz', default=0, help="Optional localization details, for information purpose only")


class product_template(models.Model):
    _inherit = 'product.template'
    
    posx = fields.Integer('Corridor (X)',related = 'property_stock_inventory.posx', default=0, help="Optional localization details, for information purpose only")
    posy = fields.Integer('Shelves (Y)', related = 'property_stock_inventory.posy',default=0, help="Optional localization details, for information purpose only")
    posz = fields.Integer('Height (Z)',related = 'property_stock_inventory.posz', default=0, help="Optional localization details, for information purpose only")
