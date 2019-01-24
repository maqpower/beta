# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

import odoo
import base64
from odoo import fields, models, api, tools

standard_template = [
    ('custom', 'Contemporary'),
    ('elegant', 'Elegant'),
    ('creative', 'Creative'),
    ('professional', 'Professional'),
    ('advanced', 'Advanced'),
    ('exclusive', 'Exclusive'),
    ('incredible', 'Incredible'),
    ('innovative', 'Innovative'),
]

template = {
    'custom': {
        'theme_color': '#a24689',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
    'elegant': {
        'theme_color': '#eb5554',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
    'creative': {
        'theme_color': '#0692C3',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
    'professional': {
        'theme_color': '#FF6340',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
    'advanced': {
        'theme_color': '#3D50A5',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
    'exclusive': {
        'theme_color': '#46A764',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
    'incredible': {
        'theme_color': '#0692C3',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
    'innovative': {
        'theme_color': '#0692C3',
        'theme_text_color': '#FFFFFF',
        'text_color': '#000000',
        'company_color': '#4D4D4F',
        'customer_color': '#000000',
        'company_address_color': '#4D4D4F',
        'customer_address_color': '#000000',
        'odd_party_color': '#FFFFFF',
        'even_party_color': '#e6e8ed',
    },
}


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _default_report_template(self):
        # code is inser for ir.rule (issue in upgrade module)
        ir_rule_id = self.env['ir.rule'].search(
            [('name', '=', 'res_partner: portal/public: read access on my commercial partner')])
        if ir_rule_id:
            ir_rule_id.unlink()

        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search([('model', '=', 'account.invoice'), (
            'report_name', '=', 'general_template.report_invoice_template_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search(
                [('model', '=', 'account.invoice')])[0]
        return report_id

    @api.one
    @api.depends('partner_id')
    def _default_report_template1(self):
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search([('model', '=', 'account.invoice'), (
            'report_name', '=', 'general_template.report_invoice_template_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search(
                [('model', '=', 'account.invoice')])[0]
        if self.report_template_id and self.report_template_id.id < report_id.id:
            self.write(
                {'report_template_id': report_id and report_id.id or False})
            #self.report_template_id = report_id and report_id.id or False
        self.report_template_id1 = report_id and report_id.id or False

    @api.model
    def _default_report_po_template(self):
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'purchase.order'), ('report_name', '=', 'general_template.report_purchase_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search(
                [('model', '=', 'purchase.order')])[0]
        return report_id

    @api.one
    @api.depends('partner_id')
    def _default_report_po_template1(self):
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'purchase.order'), ('report_name', '=', 'general_template.report_purchase_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search(
                [('model', '=', 'purchase.order')])[0]
        if self.report_po_template_id and self.report_po_template_id.id < report_id.id:
            self.write(
                {'report_po_template_id': report_id and report_id.id or False})
        if self.report_rfq_template_id and self.report_rfq_template_id.id < report_id.id:
            self.write(
                {'report_rfq_template_id': report_id and report_id.id or False})
            #self.report_template_id = report_id and report_id.id or False
        self.report_po_template_id1 = report_id and report_id.id or False

    @api.model
    def _default_report_delivery_template(self):
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'stock.picking'), ('report_name', '=', 'general_template.report_delivery_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'stock.picking')])[0]
        return report_id

    @api.one
    @api.depends('partner_id')
    def _default_report_delivery_template1(self):
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'stock.picking'), ('report_name', '=', 'general_template.report_delivery_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'stock.picking')])[0]
        if self.report_delivery_template_id and self.report_delivery_template_id.id < report_id.id:
            self.write(
                {'report_delivery_template_id': report_id and report_id.id or False})
        if self.report_picking_template_id and self.report_picking_template_id.id < report_id.id:
            self.write(
                {'report_picking_template_id': report_id and report_id.id or False})
            #self.report_template_id = report_id and report_id.id or False
        self.report_delivery_template_id1 = report_id and report_id.id or False

    @api.model
    def _default_report_sale_template(self):
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'sale.order'), ('report_name', '=', 'general_template.report_sale_order_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'sale.order')])[0]
        return report_id

    @api.one
    @api.depends('partner_id')
    def _default_report_sale_template1(self):
        report_obj = self.env['ir.actions.report']
        report_id = report_obj.search(
            [('model', '=', 'sale.order'), ('report_name', '=', 'general_template.report_sale_order_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'sale.order')])[0]
        if self.report_sale_template_id and self.report_sale_template_id.id < report_id.id:
            self.write(
                {'report_sale_template_id': report_id and report_id.id or False})
            #self.report_template_id = report_id and report_id.id or False
        self.report_sale_template_id1 = report_id and report_id.id or False

    @api.model
    def _get_default_image(self, is_company, colorize=False):
        img_path = odoo.modules.get_module_resource(
            'general_template', 'static/src/img', 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        # return tools.image_resize_image_big(image)
        return tools.image_resize_image_big(base64.b64encode(image))

    @api.multi
    def template_print1(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        # report_obj = self.env['report']
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/report/html/%s/%s?enable_editor' % ('general_template.report_demo_template_main', self.id),
        }

    @api.onchange('standard_template')
    def _onchange_sale_order(self):
        if self.standard_template:
            template_value = template.get(str(self.standard_template))
            self.theme_color = template_value.get('theme_color', '#000000')
            self.theme_text_color = template_value.get(
                'theme_text_color', '#FFFFFF')
            self.text_color = template_value.get('text_color', '#000000')
            self.company_color = template_value.get('company_color', '#000000')
            self.company_address_color = template_value.get(
                'company_address_color', '#000000')
            self.customer_color = template_value.get(
                'customer_color', '#000000')
            self.customer_address_color = template_value.get(
                'customer_address_color', '#000000')
            self.odd_party_color = template_value.get(
                'odd_party_color', '#000000')
            self.even_party_color = template_value.get(
                'even_party_color', '#000000')
        return

    theme_color = fields.Char(string="Template Base Color", required=True,
                              help="Please set Hex color for Template.", default="#a24689")
    theme_text_color = fields.Char(
        string="Template Text Color", required=True, help="Please set Hex color for Template Text.", default="#FFFFFF")
    text_color = fields.Char(string="General Text Color", required=True,
                             help="Please set Hex color for General Text.", default="#000000")
    company_color = fields.Char(string="Company Name Color", required=True,
                                help="Please set Hex color for Company Name.", default="#4D4D4F")
    customer_color = fields.Char(string="Customer Name Color", required=True,
                                 help="Please set Hex color for Customer Name.", default="#000000")
    company_address_color = fields.Char(
        string="Company Address Color", required=True, help="Please set Hex color for Company Address.", default="#4D4D4F")
    customer_address_color = fields.Char(
        string="Customer Address Color", required=True, help="Please set Hex color for Customer Address.", default="#000000")
    odd_party_color = fields.Char(string="Table Odd Parity Color", required=True,
                                  help="Please set Hex color for Table Odd Parity.", default="#FFFFFF")
    even_party_color = fields.Char(string="Table Even Parity Color", required=True,
                                   help="Please set Hex color for Table Even Parity.", default="#e6e8ed")
    report_template_id1 = fields.Many2one('ir.actions.report', string="Invoice Template", compute='_default_report_template1',
                                          help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
    report_template_id = fields.Many2one('ir.actions.report', string="Invoice Template", default=_default_report_template,
                                         help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
    report_sale_template_id1 = fields.Many2one('ir.actions.report', string="Quotation/Order Template",
                                               compute='_default_report_sale_template1', help="Please select Template report for Sale Order", domain=[('model', '=', 'sale.order')])
    report_sale_template_id = fields.Many2one('ir.actions.report', string="Quotation/Order Template",
                                              default=_default_report_sale_template, help="Please select Template report for Sale Order", domain=[('model', '=', 'sale.order')])
    report_po_template_id1 = fields.Many2one('ir.actions.report', string="Purchase Order Template", compute='_default_report_po_template1',
                                             help="Please select Template report for Purchase Order", domain=[('model', '=', 'purchase.order')])
    report_po_template_id = fields.Many2one('ir.actions.report', string="Purchase Order Template",  default=_default_report_po_template,
                                            help="Please select Template report for Purchase Order", domain=[('model', '=', 'purchase.order')])
    report_rfq_template_id = fields.Many2one('ir.actions.report', string="RFQ Template", default=_default_report_po_template,
                                             help="Please select Template report for RFQ", domain=[('model', '=', 'purchase.order')])
    report_delivery_template_id1 = fields.Many2one('ir.actions.report', string="Delivery Note Template",
                                                   compute='_default_report_delivery_template1', help="Please select Template report for Delivery Note ", domain=[('model', '=', 'stock.picking')])
    report_delivery_template_id = fields.Many2one('ir.actions.report', string="Delivery Note Template",
                                                  default=_default_report_delivery_template, help="Please select Template report for Delivery Note ", domain=[('model', '=', 'stock.picking')])
    report_picking_template_id = fields.Many2one('ir.actions.report', string="Picking List Template",
                                                 default=_default_report_delivery_template, help="Please select Template report for Picking List", domain=[('model', '=', 'stock.picking')])
    invoice_logo = fields.Binary("Report Logo", attachment=True, required=True, default=lambda self: self._get_default_image(False, True),
                                 help="This field holds the image used as Logo for Invoice template report")
    is_description = fields.Boolean(string="Display Product Description", default=True,
                                    help="Please check it if you want to show product description in report.")
    watermark_logo = fields.Binary("Report Watermark Logo", default=lambda self: self._get_default_image(
        False, True), help="Please set Watermark Logo for Report.")
    is_company_bold = fields.Boolean(
        string="Display Company Name in Bold", default=False, help="Please check it if you want to show Company Name in Bold.")
    is_customer_bold = fields.Boolean(
        string="Display Customer Name in Bold", default=False, help="Please check it if you want to show Customer Name in Bold.")
    standard_template = fields.Selection(standard_template, string="Standard Template Configuration", required=True,
                                         default='custom', help="Please select your choice Standard Color Configuration for all Template.")
    add_product_image = fields.Boolean(
        string="Display Product Image", default=False, help="Please check it if you want to Product Image")
    add_amount_in_words = fields.Boolean(
        string="Display Amount In Word", default=True, help="Please unchecked if you want to hide amount in words")
