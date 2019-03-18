# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.
import odoo
import sys
from odoo import fields, models, api, tools, _
from odoo.tools.misc import formatLang
import odoo.addons.decimal_precision as dp
import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning
from imp import reload

_DELIVERY_TYPE = []
     
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    delivery_package_type= fields.Many2one("product.packaging", strinf="Deliver Type")
    delivery_type=fields.Char(string="Provider")
    proceed_without_po=fields.Boolean(string="Is Proceed Without PO",default=False)

    def chnage_order_line_qty(self):
        order_line = self.env['sale.order.line'].search([('product_uom.name','=','Hour(s)')])
        for lines in order_line:
            if lines.product_uom.name == "Hour(s)":
                lines._compute_amount()
                lines.order_id._amount_all()
        return True

    @api.multi
    def action_confirm(self):
        if not self.client_order_ref and not self.proceed_without_po:
            self.proceed_without_po=True
            self._cr.commit()
            raise Warning(_('Do you want to proceed without a Purchase Order Number?'))
        return super(SaleOrder, self).action_confirm()
    
    @api.onchange('carrier_id')
    def onchange_delivery_method(self):
        if self.carrier_id:
            self.delivery_type=self.carrier_id.delivery_type

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            new_template_id = ir_model_data.get_object_reference(
                'customize_general_template', 'report_sale_order_classic')[1]
            if self.report_template_id.id == new_template_id:
                new_template_id = ir_model_data.get_object_reference(
                    'sale', 'email_template_edi_sale')[1]
            else:
                new_template_id = ir_model_data.get_object_reference(
                    'biztech_service', 'email_template_edi_service_quotation')[1]
        except ValueError:
            new_template_id = False
        try:
            template_id = ir_model_data.get_object_reference(
                'sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(new_template_id),
            'default_template_id': new_template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
    @api.multi
    def _get_street(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.street:
            address = "%s" % (partner.street)
        if partner.street2:
            address += ", %s" % (partner.street2)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False

    @api.multi
    def _get_address_details(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.city:
            address = "%s" % (partner.city)
        if partner.state_id.name:
            address += ", %s" % (partner.state_id.code)
        if partner.zip:
            address += ", %s" % (partner.zip)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False
