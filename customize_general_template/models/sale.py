# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from dateutil import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, SUPERUSER_ID, _

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    default_report_template_id = fields.Many2one('ir.actions.report', string="Picking Template",
                                         help="Please select Template report for Picking", domain=[('model', '=', 'stock.picking')])

    # for getting default maqpower template in picking
    @api.one
    @api.depends('partner_id')
    def _default_report_template1(self):
        res = super(StockPicking, self)._default_report_template1()
        report_id = self.env['ir.actions.report'].search(
            [('model', '=', 'stock.picking'), ('report_name', '=', 'customize_general_template.report_delivery_custom_classic')])
        if report_id:
            report_id = report_id[0]
            self.report_template_id = report_id.id
        return res
    
    @api.onchange('default_report_template_id')
    def onchnage_default_report_template_id(self):
        if self.default_report_template_id:
            self.report_template_id=self.default_report_template_id.id

    @api.model
    def default_get(self, default_fields):
        vals = super(StockPicking, self).default_get(default_fields)
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'stock.picking'), ('report_name', '=', 'customize_general_template.report_delivery_custom_classic')])
        if report_id:
            report_id = report_id[0]
            vals.update({
                'default_report_template_id': report_id.id
            })
        return vals

class product_template(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, fields):
        vals = super(product_template, self).default_get(fields)
        if vals.get('supplier_taxes_id', False):
            vals.update({'supplier_taxes_id': []})
        return vals


class website(models.Model):
    _inherit = 'website'

    days_to_expire = fields.Float("Days To Expire")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    days_to_expire = fields.Float(
        related='website_id.days_to_expire', string="Days To Expire")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    zip = fields.Char(change_default=True, related='partner_id.zip')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict', related='partner_id.state_id')
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict', related='partner_id.country_id')
    inv_street = fields.Char(string="inv street")
    inv_street2 = fields.Char(string="inv street2")
    inv_zip = fields.Char(change_default=True,string="ZIP Billing")
    inv_city = fields.Char(string="Inv city")
    inv_state_id = fields.Many2one("res.country.state", string='State Billing',
                                   ondelete='restrict')
    inv_country_id = fields.Many2one(
        'res.country', string='Country Billing', ondelete='restrict')

    ship_street = fields.Char(string="Street Shipping")
    ship_street2 = fields.Char(string="Street2 Shipping")
    ship_zip = fields.Char(change_default=True, string="ZIP Shipping")
    ship_city = fields.Char(string="Shipping city")
    ship_state_id = fields.Many2one(
        "res.country.state", string='State Shipping', ondelete='restrict')
    ship_country_id = fields.Many2one(
        'res.country', string='Country Shipping', ondelete='restrict')
    is_partnumber = fields.Boolean(
        string='Display Part Number In Reports', default=True)
    is_price = fields.Boolean(string='Display Price In Reports')
    service_type = fields.Selection([
        ('repair', 'Repair'),
        ('troubleshoot', 'Troubleshoot'),
        ('start_up', 'Start Up'),
        ('minor_pm', 'Minor PM'),
        ('major_pm', 'Major PM'),
        ('elite_care', 'Elite Care')
    ], string="Service Type", store=True)
    
    customer_id=fields.Integer(string="Customer number",compute='_get_customer_number')

    @api.onchange('partner_invoice_id')
    def onchnage_inv_partner(self):
        self.inv_street= self.partner_invoice_id.street
        self.inv_street2= self.partner_invoice_id.street2
        self.inv_zip= self.partner_invoice_id.zip
        self.inv_state_id= self.partner_invoice_id.state_id.id
        self.inv_city = self.partner_invoice_id.city
        domain_invoice=[('customer','=',True),('custom_lead','=',False),('type','=','invoice'),('parent_id','=',self.customer_id)]
        return {'domain': {'partner_invoice_id': domain_invoice}}

    @api.onchange('partner_shipping_id')
    def onchnage_shipping_partner(self):
        self.ship_street= self.partner_shipping_id.street
        self.ship_street2= self.partner_shipping_id.street2
        self.ship_zip= self.partner_shipping_id.zip
        self.ship_state_id= self.partner_shipping_id.state_id.id
        self.ship_city = self.partner_shipping_id.city
        domain_invoice=[('customer','=',True),('custom_lead','=',False),('type','=','delivery'),('parent_id','=',self.customer_id)]
        return {'domain': {'partner_shipping_id': domain_invoice}}

    @api.onchange('customer_id')
    def onchnage_partner(self):
        if self.customer_id==0:
            return {'domain': {'partner_invoice_id': [('customer','=',True),('custom_lead','=',False),('type','=','invoice')],
                               'partner_shipping_id': [('customer','=',True),('custom_lead','=',False),('type','=','delivery')]}}
        else:
            domain_invoice=[('customer','=',True),('custom_lead','=',False),('type','=','invoice'),('parent_id','=',self.customer_id)]
            domain_shipping=[('customer','=',True),('custom_lead','=',False),('type','=','delivery'),('parent_id','=',self.customer_id)]
            invoice_res_id=self.env['res.partner'].search(domain_invoice,limit=1)
            if not invoice_res_id:
                self.partner_invoice_id=self.partner_id.id
            else:
                self.partner_invoice_id=invoice_res_id.id
            return {'domain': {'partner_invoice_id': domain_invoice}}
            shipping_res_id=self.env['res.partner'].search(domain_shipping,limit=1)
            if not shipping_res_id:
                self.partner_shipping_id=self.partner_id.id
            else:
                self.partner_shipping_id=shipping_res_id.id
            return {'domain': {'partner_invoice_id': domain_invoice, 'partner_shipping_id': domain_shipping}}
            
    
    @api.depends('partner_id')
    def _get_customer_number(self):
        if self.partner_id:
            self.customer_id=self.partner_id.id or False
#         
        #days_to_expire=fields.Float("Days To Expire")

    # get exoiry date and template in by default
    @api.model
    def default_get(self, data):
        vals = super(SaleOrder, self).default_get(data)
        today = datetime.now()
        website_obj = self.env['website'].search([], limit=1)
        final_days = website_obj.days_to_expire
        vals['validity_date'] = today + (timedelta(days=final_days))
        return vals

    # for getting default maqpower template in so
    @api.one
    @api.depends('partner_id')
    def _default_report_template1(self):
        res = super(SaleOrder, self)._default_report_template1()

        report_id = self.env['ir.actions.report'].search(
            [('model', '=', 'sale.order'), ('report_name', '=', 'customize_general_template.report_sale_order_custom_classic')])
        if report_id:
            report_id = report_id[0]
            self.report_template_id = report_id.id
        if self.partner_id:
            self.sale_payment_method_id = self.partner_id.sale_payment_method_id
        return res

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        result.partner_id.custom_lead = False
        return result

    @api.multi
    def unlink(self):
        partners = []
        for rec in self:
            partners.append(rec.partner_id.id)

        res = super(SaleOrder, self).unlink()
        res_partners_obj = self.env['res.partner'].sudo().search(
            [('id', 'in', list(set(partners)))])
        for partner in res_partners_obj:
            if partner.sale_order_count > 0:
                partner.write({'custom_lead': False})
            else:
                partner.write({'custom_lead': True})
        return res


class SaleOrderLineTrans(models.TransientModel):
    _name = 'sale.order.line.trans'

    comment = fields.Text(
        string='Comment', help="commnet for order line", translate=True)

    @api.model
    def create(self, vals):
        ctx = self._context
        so_line_id = self.env['sale.order.line'].search(
            [('id', '=', ctx.get('active_id'))])
        if so_line_id:
            so_line_id.write({
                'comment': vals.get('comment')
            })

        return super(SaleOrderLineTrans, self).create(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    comment = fields.Text(
        string='Internal Comment', help="Internal comment for order line", translate=True)
    external_comment = fields.Text(
        string='External Comment', help="External comment for order line", translate=True)

    # Use to show only product code in sale order line
    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(SaleOrderLine, self).read(fields=fields, load=load)
        product_obj = self.env['product.product']
        if result:
            for rec in result:
                if rec and rec.get('product_id') and isinstance(rec.get('product_id'), tuple):
                    p_id = rec.get('product_id')[0]

                    product_id = product_obj.search([('id', '=', p_id)])
                    rec.update({
                        'product_id': (p_id, str(product_id.default_code)),
                    })
        return result


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    vendor_street = fields.Char(related='partner_id.street')
    vendor_street2 = fields.Char(related='partner_id.street2')
    vendor_zip = fields.Char(change_default=True, related='partner_id.zip')
    vendor_city = fields.Char(related='partner_id.city')
    vendor_state_id = fields.Many2one(
        "res.country.state", string='State', ondelete='restrict', related='partner_id.state_id')
    vendor_country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict', related='partner_id.country_id')

    ship_street = fields.Char(related='custom_shipping_address.street',string="Street Shipping")
    ship_street2 = fields.Char(related='custom_shipping_address.street2',string="Street2 Shipping")
    ship_zip = fields.Char(change_default=True,
                           related='custom_shipping_address.zip')
    ship_city = fields.Char(related='custom_shipping_address.city',string="City Shipping")
    ship_state_id = fields.Many2one("res.country.state", string='State Shipping',
                                    ondelete='restrict', related='custom_shipping_address.state_id')
    ship_country_id = fields.Many2one(
        'res.country', string='Country Shipping', ondelete='restrict', related='custom_shipping_address.country_id')

    current_user_id = fields.Many2one(
        'res.users', string='Order Placed By', default=lambda self: self.env.user)
    custom_shipping_address = fields.Many2one(
        'res.partner', string='Shipping Address',)
    #ship to and bill to dynamic domain
    customer_id=fields.Integer(string="Customer number",compute='_get_customer_number')
    incoterm_id = fields.Many2one('stock.incoterms', 'Incoterm')

    @api.depends('partner_id')
    def _get_customer_number(self):
        if self.partner_id:
            self.customer_id=self.partner_id.id or False

    @api.multi
    def _get_line_product_name(self, line_id):
        name = False
        if line_id:
            line_vals = self.env['purchase.order.line'].browse([line_id])
            if line_vals.product_id.seller_ids:
                for seller_line in line_vals.product_id.seller_ids:
                    if seller_line.name.id == self.partner_id.id:
                        if seller_line.product_code:
                            name = str(seller_line.product_code)
                            return name
        return line_vals.product_id.default_code

    @api.multi
    def _get_ship_via(self, order):
        if order:
            name = False
            picking = self.env['stock.picking'].search(
                [('origin', '=', order.name)])
            if picking:
                for pick in picking:
                    name = pick.carrier_id.name
                return name
        return False

    def _get_method(self, method_type_fedex):
        if method_type_fedex:
            return method_type_fedex.replace('_', " ")

    def _get_method_name(self):
        if self and self.delivery_type:
            if self.fedex == True and self.method_type_fedex:
                return self.method_type_fedex.replace('_', " ")

            elif self.dhl == True and self.method_type_dhl:
                return self.method_type_dhl.name

            elif self.usps == True and self.method_type_usps:
                return self.method_type_usps

            elif self.ups == True and self.method_type_ups:
                ups_vals = self.get_ups_value()
                dict_ups_vals = dict(ups_vals)
                return dict_ups_vals.get(self.method_type_ups)
        return


# change for setting default Maqpower main 10-1-2018
    @api.model
    def default_get(self, data):
        
        vals = super(PurchaseOrder, self).default_get(data)
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'purchase.order'), ('report_name', '=', 'customize_general_template.report_purchase_custom_classic')])
        if report_id:
            report_id = report_id[0]
            vals.update({
                'report_template_id': report_id.id
            })
 
        # for setting default 'ex works'
        p_id = self.env['stock.incoterms'].search(
            [('name', '=', 'EX WORKS')], limit=1)
        if vals and not vals.get('incoterm_id') and p_id:
            vals.update({
                'incoterm_id': p_id.id
            })
        #for set default address as maqpower
        company = self.env.user.company_id
        vals.update({'custom_shipping_address':company.partner_id.id})
        return vals

    # method overridded because default get called first insted of onchange
    # relate to above method of default get.
    @api.one
    @api.depends('partner_id')
    def _default_report_template1(self):
        res = super(PurchaseOrder, self)._default_report_template1()

        report_id = self.env['ir.actions.report'].search(
            [('model', '=', 'purchase.order'), ('report_name', '=', 'customize_general_template.report_purchase_custom_classic')])
        if report_id:
            report_id = report_id[0]
            self.report_template_id = report_id.id

        return res

    @api.onchange('partner_id')
    def _onchange_biz_partner_id(self):

        if self.partner_id and not self.partner_id.child_ids:
            if self.env.user and self.env.user.company_id and self.env.user.company_id.partner_id:
                self.custom_shipping_address = self.env.user.company_id.partner_id


class PurchaseOrderLineTrans(models.TransientModel):
    _name = 'purchase.order.line.trans'

    comment = fields.Text(
        string='Internal Comment', help="commnet for order line", translate=True)

    @api.model
    def create(self, vals):
        ctx = self._context
        so_line_id = self.env['purchase.order.line'].search(
            [('id', '=', ctx.get('active_id'))])
        if so_line_id:
            so_line_id.write({
                'comment': vals.get('comment')
            })

        return super(PurchaseOrderLineTrans, self).create(vals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    comment = fields.Text(
        string='Internal Comment', help="commnet for order line", translate=True)
    external_comment = fields.Text(
        string='External Comment', help="External comment for order line", translate=True)

    # Use to show only product code in purchase order line
    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(PurchaseOrderLine, self).read(fields=fields, load=load)

        product_obj = self.env['product.product']
        if result:
            for rec in result:
                if rec and rec.get('product_id') and isinstance(rec.get('product_id'), tuple):
                    p_id = rec.get('product_id')[0]

                    product_id = product_obj.search([('id', '=', p_id)])
                    rec.update({
                        'product_id': (p_id, str(product_id.default_code)),
                    })
        return result

    @api.multi
    def unlink(self):
        for line in self:
            if line.order_id.state in ['purchase', 'done']:
                raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'. Please ensure to cancel and then validate once changes have been made.')%(line.state,))
        return super(PurchaseOrderLine, self).unlink()


# change for setting default United State main 10-1-2018
class CustomResPartner(models.Model):
    _inherit = 'res.partner'

    custom_lead = fields.Boolean(string="Lead", default=True)
    sale_payment_method_id = fields.Many2one(
        'sale.payment.method', string="Payment Method")
    login_user = fields.Many2one('res.users',string="Login User")

    @api.model
    def default_get(self, vals):
        res = super(CustomResPartner, self).default_get(vals)

        country_id = self.env['res.country'].search(
            [('name', '=', 'United States')], limit=1)
        res.update({
            'country_id': country_id.id
        })
        res.update({'login_user':self.env.uid})
        return res

     
    # Display those customer who have sale orders
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        ctx = self._context
        if domain:
            res_obj = self.env['res.partner'].search(domain)
            sales_ids = []
            if ctx and ctx.get('no_change'):
                return super(CustomResPartner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
     
            if ctx and ctx.get('default_lead'):
                for rec in res_obj:
                    if rec.sale_order_count == 0 and rec.customer and rec.custom_lead == True:
                        sales_ids.append(rec.id)
            else:
                for rec in res_obj:
                    if rec.sale_order_count > 0 or rec.custom_lead == False:
                        sales_ids.append(rec.id)
                    if rec.supplier:
                        sales_ids.append(rec.id)
            domain.append(['id', 'in', sales_ids])
            res = super(CustomResPartner, self).search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            return res
        else:
            return super(CustomResPartner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    customer_id=fields.Integer(string="Customer number",compute='_get_customer_number')

    @api.onchange('customer_id')
    def onchnage_partner(self):
         if self.customer_id==0:
            return {'domain': {'partner_shipping_id': [('customer','=',True),('custom_lead','=',False),('type','=','delivery')]}}
         else:
            domain=[('customer','=',True),('custom_lead','=',False),('type','=','delivery'),('parent_id','=',self.customer_id)]
            ship_res_id=self.env['res.partner'].search(domain,limit=1)
            if not ship_res_id:
                self.partner_shipping_id=self.partner_id.id
            else:
                self.partner_shipping_id=ship_res_id.id
            return {'domain': {'partner_shipping_id': domain}}

    @api.depends('partner_id')
    def _get_customer_number(self):
        if self.partner_id:
            self.customer_id=self.partner_id.id or False

    @api.multi
    def _get_customer(self, order):
        if order:
            sale_order = self.env['sale.order'].search([('name', '=', order)])
            if sale_order:
                for vals in sale_order:
                    if vals.client_order_ref != 'No PO' and vals.client_order_ref != '':
                        name = vals.client_order_ref
                        if name:
                            return name
                        else:
                            return False


#     @api.multi
#     def _get_ship_info(self, order):
#         name = False
#         if order:
#             sale_order = self.env['sale.order'].search([('name','=',str(order))])
#             if sale_order:
#                 for val in sale_order:
#                     if val and val.incoterm:
#                         name = val.incoterm.name
#                 return name
#             else:
#                 purchase_order = self.env['purchase.order'].search([('name','=',str(order))])
#                 if purchase_order:
#                     for vals in purchase_order:
#                         if vals and vals.incoterm_id:
#                             name = vals.incoterm_id.name
#                     return name
#         return False


    @api.multi
    def _get_ship_info(self, order):
        name = False
        if order:
            sale_order = self.env['sale.order'].search(
                [('name', '=', str(order))])
            dict_val={}
            if sale_order:
                for val in sale_order:
                    if val and val.carrier_id and val.carrier_id.id:
                        carrier_id = val.carrier_id.name
                         

                    if val and val.sale_payment_method_id and val.sale_payment_method_id.id:
                        name = val.sale_payment_method_id.name
                dict_val.update({'name':name,'carrier_id':carrier_id})
                return dict_val
            else:
                purchase_order = self.env['purchase.order'].search(
                    [('name', '=', str(order))])
                if purchase_order:
                    for vals in purchase_order:
                        if vals and vals.method_type_fedex and vals.delivery_method:
                            delivery_name = vals.delivery_method.name
                            payment_method_name = vals.method_type_fedex
                            name = delivery_name + " " + \
                                (payment_method_name.replace("_", " "))
                    return name
        return False

    @api.multi
    def get_deliver_qty(self, line_id):
        qty = 0.0
        if line_id:
            sql_query = """SELECT * FROM sale_order_line_invoice_rel 
                        WHERE invoice_line_id = %s"""
            params = (line_id,)
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()
            if results:
                for val in results:
                    line_vals = self.env['sale.order.line'].browse(
                        val.get('order_line_id'))
                    if line_vals:
                        return '%.3f' % line_vals.qty_delivered
        return '%.3f' % qty

    @api.multi
    def get_backorder_qty(self, line_id):
        qty = 0.0
        if line_id:
            sql_query = """SELECT * FROM sale_order_line_invoice_rel 
                        WHERE invoice_line_id = %s"""
            params = (line_id,)
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()
            if results:
                for val in results:
                    line_vals = self.env['sale.order.line'].browse(
                        val.get('order_line_id'))
                    if line_vals:
                        return '%.3f' % (line_vals.qty_invoiced - line_vals.qty_delivered)
        return '%.3f' % qty
