# -*- coding: utf-8 -*-
# Part of Biztech Consultancy. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class CustomAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_miss_attachment = fields.Boolean('is miss attachement',default=False)



class CustomIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, values):
        res = super(CustomIrAttachment,self).create(values)
        if values.get('res_model') == 'account.invoice':
            if res and res.res_id:
                account_invoice = self.env['account.invoice'].browse(res.res_id)
                account_invoice.write({'is_miss_attachment':True})
        return res

    @api.one
    def unlink(self):
        dummy_id = self.res_id
        dummy_model = self.res_model
        res = super(CustomIrAttachment,self).unlink()
        if dummy_model == 'account.invoice':
            if dummy_model and dummy_id:
                attachment = self.search([('res_model','=','account.invoice'),('res_id','=',dummy_id)])
                if not attachment:
                    account_invoice = self.env['account.invoice'].browse(dummy_id)
                    account_invoice.write({'is_miss_attachment':False})
        return res

