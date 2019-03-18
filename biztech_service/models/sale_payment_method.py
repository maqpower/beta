# -*- coding: utf-8 -*-

from odoo import models, api, fields
import operator as py_operator


OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}
class sale_order(models.Model):
    _inherit = "sale.order"

    sale_payment_method_id = fields.Many2one('sale.payment.method', string="Payment Method")


class sale_payment_method(models.Model):
    _name = "sale.payment.method"

    name = fields.Char(string="Name")


class product_template(models.Model):
    _inherit = 'product.template'

    is_reference_code_set = fields.Boolean(string="Is Reference Code Set", default=False)
    sales_count = fields.Integer(compute='_sales_count', string='Qty Sold',search='_search_qty_sold')

    def _search_qty_sold(self, operator, value):
        domain = [('sales_count', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]

class product_product(models.Model):
    _inherit= 'product.product'

    sales_count = fields.Integer(compute='_sales_count', string='Qty Sold',search='_search_qty_sold')

    def _search_qty_sold(self, operator, value):
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)
        ids = []
        for product in self.with_context(prefetch_fields=False).search([]):
            if OPERATORS[operator](product['sales_count'], value):
                ids.append(product.id)
        return [('id', 'in', ids)]

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    invoice_original = fields.Char(string="Original Invoice Number")

    def chnage_invoice_line_qty(self):
        order_line = self.env['account.invoice.line'].search([('uom_id.name','=','Hour(s)')])
        for lines in order_line:
            if lines.uom_id.name == "Hour(s)":
                lines._compute_price()
                self._compute_amount()
        return True