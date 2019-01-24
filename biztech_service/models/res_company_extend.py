import odoo.addons.decimal_precision as dp
from dateutil import relativedelta
from datetime import datetime
from odoo import models, api, fields, _
from dateutil.relativedelta import relativedelta


class res_company(models.Model):
    _inherit = 'res.company'

    fax = fields.Char(string="Fax")
    generic_comment = fields.Text(string="Generic Comment")
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    cost_price = fields.Float(string="Cost Price")
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        self.cost_price = self.product_id.standard_price
        return res
    
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    service_id = fields.Many2one(string='Service',related='picking_id.service_id')

