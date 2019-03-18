# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    customer_history_id = fields.One2many('customer.sale.history','res_partner_id',string="Customer Sale History",
        help="Information of customer sales history.")


class CustomerSaleHistory(models.Model):
    _name = 'customer.sale.history'
    _rec_name = 'res_partner_id'

    @api.model
    def _default_currency(self):
        return self.currency_id or self.current_company.currency_id or self.env.user.company_id.currency_id

    serial = fields.Char(string="Serial #",required=True)
    units = fields.Float(string="Order Amount")
    unit_price = fields.Char(string="Order Amount")
    ship_date = fields.Date(string="Ship Date")
    start_up_date = fields.Date(string="Warranty Date")
    description = fields.Char(string="Description")
    warranty_registration = fields.Char(string="Warranty")
    ship_to = fields.Many2one('res.partner',string="Ship To",help="Shipping address")
    bill_to = fields.Many2one('res.partner',string="Bill to",help="Billing address")
    res_partner_id = fields.Many2one('res.partner',string="Customer",help="link customer")
    top_bill=fields.Char("Top Bill")
    current_company =fields.Many2one('res.company',default=lambda self: self.env['res.company']._company_default_get('customer.sale.history'))
    currency_id = fields.Many2one('res.currency', related='current_company.currency_id',default=_default_currency)

    def get_price(self):
        all_id = self.search([])
        for history in all_id:
            val_string=history.unit_price
            final_val = float(val_string)
            history.units = round(final_val)
        return True