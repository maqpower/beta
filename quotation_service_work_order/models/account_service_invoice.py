# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

class ResPartner(models.Model):
    _inherit="res.partner"

   

    def get_ups_value(self):
        return [('03', 'UPS Ground'),
                ('11', 'UPS Standard'),
                ('01', 'UPS Next Day'),
                ('14', 'UPS Next Day AM'),
                ('13', 'UPS Next Day Air Saver'),
                ('02', 'UPS 2nd Day'),
                ('59', 'UPS 2nd Day AM'),
                ('12', 'UPS 3-day Select'),
                ('65', 'UPS Saver'),
                ('07', 'UPS Worldwide Express'),
                ('08', 'UPS Worldwide Expedited'),
                ('54', 'UPS Worldwide Express Plus'),
                ('96', 'UPS Worldwide Express Freight')]

    provider_name = fields.Char(string='Provider')
    method_type_fedex = fields.Selection([('INTERNATIONAL_ECONOMY', 'INTERNATIONAL_ECONOMY'),
                                           ('INTERNATIONAL_PRIORITY', 'INTERNATIONAL_PRIORITY'),
                                           ('FEDEX_GROUND', 'FEDEX_GROUND'),
                                           ('FEDEX_2_DAY', 'FEDEX_2_DAY'),
                                           ('FEDEX_2_DAY_AM', 'FEDEX_2_DAY_AM'),
                                           ('FIRST_OVERNIGHT', 'FIRST_OVERNIGHT'),
                                           ('PRIORITY_OVERNIGHT', 'PRIORITY_OVERNIGHT'),
                                           ('STANDARD_OVERNIGHT', 'STANDARD_OVERNIGHT')],string='Method Type')
    fedex = fields.Boolean(string="fedex", default=False)
    method_type_dhl = fields.Many2one('product.packaging', string='Method Type')
    dhl = fields.Boolean(string="dhl", default=False)
    method_type_usps = fields.Selection([('First Class', 'First Class'),
                                         ('Priority', 'Priority'),
                                         ('Express', 'Express')],string='Method Type')
    usps = fields.Boolean(string="usps", default=False)
    method_type_ups = fields.Selection(
        get_ups_value, 
        string='Method Type')
    ups = fields.Boolean(string="ups", default=False)

    delivery_package_type= fields.Many2one("product.packaging", strinf="Deliver Type")

    @api.onchange('property_delivery_carrier_id')
    def onchange_delivery_method(self):
        if self.property_delivery_carrier_id:
            self.provider_name=self.property_delivery_carrier_id.delivery_type
    
    def send_msg(self):
        return True
    
class AccountInvoice(models.Model):
    _inherit='account.invoice'

    is_service_invocie = fields.Boolean(string="Service Invoice",default = False)
    
    @api.model
    def create(self, vals):
        if self._context.get('search_default_is_service_invocie'):
            vals.update({'is_service_invocie':True})
        return super(AccountInvoice, self).create(vals)

class AccountJournal(models.Model):
    _inherit='account.journal'

    @api.multi
    def get_journal_dashboard_datas(self):
        #for count
        self.env.cr.execute("SELECT count(*) FROM account_invoice WHERE is_service_invocie = True")
        fetched_data = self.env.cr.dictfetchall()
        count= fetched_data[0].get('count')
        #for total amount
        currency = self.currency_id or self.company_id.currency_id
        res= super(AccountJournal,self).get_journal_dashboard_datas()
        ser_inv_ids = self.env['account.invoice'].search([('is_service_invocie','=', True)])
        sum = 0.0
        if ser_inv_ids:
            for inv_id in ser_inv_ids:
                sum += inv_id.amount_total
        sum_service = sum
        res.update({'sum_service':formatLang(self.env, currency.round(sum_service) + 0.0, currency_obj=currency),
                    'service_count':count})
        return res

    @api.multi
    def open_action_service(self):
        """return action based on type for related journals"""
        action_name = self._context.get('action_name', False)
        if self.type == 'sale':
            action_name = 'action_invoice_service_tree1'
            [action] = self.env.ref('quotation_service_work_order.%s' % action_name).read()
            if action_name in ['action_invoice_tree1', 'action_invoice_tree2']:
                action['search_view_id'] = account_invoice_filter and account_invoice_filter.id or False
            return action

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        inv_id = super(SaleOrder, self).action_invoice_create()
        if self.is_service_quote_temp == False:
            self.env['account.invoice'].browse(inv_id[0]).write({'is_service_invocie':True})
        return inv_id

        