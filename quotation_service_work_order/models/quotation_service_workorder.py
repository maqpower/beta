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


class ServiceInventoryWorkflow(models.Model):
    _inherit = "service.inventory.workflow"
    _description = "Service Inventory Workflow"
    
    sale_order_line_id = fields.Many2one('sale.order.line',string = "Sale Order Line")
    
class service_customer_information(models.Model):
    _inherit = 'service.customer.information'
    
    sale_order_id = fields.Many2one('sale.order',string = "Sale order")
    client_order_ref = fields.Char("Customer PO",related = "sale_order_id.client_order_ref")

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
#         sys.setdefaultencoding("utf-8")
        html_text= str(tools.plaintext2html(address,container_tag=True))
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
        #if partner.country_id.name:
        #    address += ", %s" % (partner.country_id.name)
        reload(sys)
        html_text= str(tools.plaintext2html(address,container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False
    
    @api.multi
    def write(self, values):
        
        res = super(service_customer_information, self).write(values)
        if self.sale_order_id:
            service_inventory_workflow_obj = self.env['service.inventory.workflow']
            sale_order_line_list =[]
            sale_line_list = []
            new_id_list = []
            if values.get('service_inventory_workflow'):
                for line in values.get('service_inventory_workflow'):
                    if line[0] != 0:
                        line_service_val = service_inventory_workflow_obj.browse(line[1])
                        if line_service_val:
                            for sale_line in self.sale_order_id.order_line:
                                if line_service_val.sale_order_line_id.id == sale_line.id:
                                    sale_order_line = self.env['sale.order.line'].browse(sale_line.id)
                                    wrt = sale_order_line.write({'product_id' : line_service_val.product_id.id,
                                                                              'product_uom_qty':line_service_val.product_uom_qty,
                                                                              'product_uom': line_service_val.product_uom.id,
                                                                              'price_unit' : line_service_val.product_price,
            #                                                                        'sale_order_line_id':so_line.id
                                                                                                    })
                    
                    if line[0] == 0:
                        new_record_dict = line[2]
                        parent_id = new_record_dict['service_customer_info_id']
                        if not new_record_dict['sale_order_line_id']:
                            new_so_line = self.env['sale.order.line'].create({'product_id' : new_record_dict.get('product_id'),
                                                                        'product_uom_qty':new_record_dict.get('product_uom_qty'),
                                                                        'product_uom': new_record_dict.get('product_uom'),
                                                                        'price_unit' : new_record_dict.get('product_price'),
                                                                        'order_id': self.sale_order_id.id,
                                                                        'equipment_id':self.equipment_id.id,
                                                                             })
                            if new_so_line:
                                new_id_list.append(new_so_line)
                                new_line_service_val = self.browse(parent_id)
                                for line in new_line_service_val.service_inventory_workflow:
                                    if not line.sale_order_line_id:
                                        for id in new_id_list:
                                            line.sale_order_line_id = id
                                            new_id_list = []
        return res
    
class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    
    equipment_id = fields.Many2one('service.equipment',string = "Equipment")

class sale_order(models.Model):
    _inherit = "sale.order"
    
    is_service_quote_temp = fields.Boolean(string = "Is Service Quote Temp",default = False)
    workorder_count = fields.Integer("Workorder Count",compute='_workorder_count',default = 0)
    no_edit = fields.Boolean("No Edit")
    single_multiple_quotation_reports = fields.Selection([
        ('single_report', 'Single Report'),
        ('multiple_report', 'Multiple Report'),
        ], string= "Single/Multiple Quotation Reports")
    single_multiple_invoice = fields.Selection([
        ('single_invocie', 'Single Invoice'),
        ('multiple_invocie', 'Multiple Invoice'),
        ], string= "Single/Multiple Invoices")
    service_workorder_history_id = fields.One2many('service.customer.information','sale_order_id',string = "Service Work order History")
    delivery_count_service = fields.Integer(string='Delivery Orders', compute='_compute_picking_service_ids')
    is_sale_order_line = fields.Boolean('Is Sale Order Line',compute='get_so_line_count', default = False)
    
    @api.multi
    def get_so_line_count(self):
        if len(self.order_line) >= 1:
             self.is_sale_order_line=True
    
    @api.depends('picking_ids')
    def _compute_picking_service_ids(self):
        for order in self:
            order.delivery_count_service = len(order.picking_ids)
    
    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if self.no_edit==True:
            default = dict(default or {})
            default['no_edit']=False
        return super(sale_order, self).copy(default=default)

    @api.onchange('report_template_id')
    def _onchange_report_template_id(self):
        if self.report_template_id:
            report_obj = self.env['ir.actions.report']
            delivery_obj = self.env['delivery.carrier']
            del_id = delivery_obj.search([('name','=','Service Truck')])
            report_id = report_obj.search(
            [('model', '=', 'sale.order'), ('report_name', '=', 'customize_general_template.report_quotation_sale_order_custom')])
            if self.report_template_id.id == report_id.id:
                self.is_service_quote_temp = False
                self.carrier_id=del_id
            if self.report_template_id.id != report_id.id:
                self.is_service_quote_temp = True

    @api.multi
    @api.depends('workorder_count')
    def _get_service_workorder(self):
        wo_ids_list = []
        for rec in self:
            domain = [('sale_order_id', '=', rec.id)]
            service_wororder = self.env['service.customer.information'].search(domain)
            for order_id in service_wororder:
                wo_ids_list.append((0, 0,{'service_workorder' : order_id.name,
                                          'sale_service_order_id':rec.id,
                                         }))
            rec.service_workorder_history_id = wo_ids_list
        return [(0, 0, {'service_workorder': 'balance', 'sale_service_order_id': self.id})]
    
    @api.one
    def _workorder_count(self):
        wo_ids_list = []
        domain = [('sale_order_id', '=', self.id)]
        service_wororder = self.env['service.customer.information'].search(domain)
        for order_id in service_wororder:
            wo_ids_list.append(order_id.id)
        self.workorder_count = len(wo_ids_list)

    @api.multi
    def action_view_workorder(self):
        wo_ids_list = []
        context = self._context
        action = self.env.ref('biztech_service.service_customert_info_action').read()[0]
        domain = [('sale_order_id', '=', self.id)]
        service_wororder = self.env['service.customer.information'].search([])
        for order_id in service_wororder:
            wo_ids_list.append(order_id.id)
            if service_wororder:
                action['domain'] = [('id', 'in',wo_ids_list)]
#                 action['views'] = [(self.env.ref('biztech_service.view_service_customert_info_form').id, 'form')]
                action['res_id'] = order_id.id
                action['context'] = {'search_default_sale_order_id': self.id}
                if context.get('search_default_sale_order_id', False):
                    context.update(search_default_journal_id=self.id)
        return action
        
        
    @api.multi
    def action_workorder_create(self):
        warn = {}
        service_customer_info_obj = self.env['service.customer.information']
        if self.no_edit == False:
            for sale in self:
                equipment_list = []
                for so_line in sale.order_line:
                    work_order_line = []
                    work_order_line_updated = []
                    if so_line.equipment_id.id:
                        self._cr.execute("""SELECT id FROM service_customer_information WHERE equipment_id = %s AND sale_order_id = %s""", (so_line.equipment_id.id,sale.id))
                        res = self._cr.fetchall()
                        if res:
                            work_order_id = res[0][0]
                            service_val = service_customer_info_obj.browse(work_order_id)
                            if so_line.equipment_id.id == service_val.equipment_id.id:
                                work_order_line_updated.append((0, 0,{'product_id' : so_line.product_id.id,
                                                                      'product_uom_qty':so_line.product_uom_qty,
                                                                      'product_uom': so_line.product_uom.id,
                                                                      'product_price' : so_line.price_unit,
                                                                      'sale_order_line_id':so_line.id
                                                                      }))
                                wrt = service_val.write({'service_inventory_workflow' : work_order_line_updated})
                        else:
                            work_order_line.append((0, 0,{'product_id' : so_line.product_id.id,
                                                          'product_uom_qty':so_line.product_uom_qty,
                                                          'product_uom': so_line.product_uom.id,
                                                          'product_price' : so_line.price_unit,
                                                          'sale_order_line_id':so_line.id}))
                            work_order_so = service_customer_info_obj.create({
                                                    'partner_id': sale.partner_id.id,
                                                    'partner_invoice_id':sale.partner_invoice_id.id,
                                                    'partner_shipping_id':sale.partner_shipping_id.id,
                                                    'payment_term_id':sale.payment_term_id.id,
                                                    'service_inventory_workflow':work_order_line,
                                                    'date_service_scheduled' : datetime.datetime.now(),
                                                    'sale_order_id':sale.id,
                                                    'equipment_id':so_line.equipment_id.id,
                                                    'user_id':self.env.uid,
                                                    'service_type':self.service_type
                                                    })
                self.no_edit = True 
        else:
            raise UserError(_('Service Work orders are already created for saleorder %s') %self.name )
        
      
            
                
        
