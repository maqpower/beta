from odoo import fields, models, api,_
from odoo import tools

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

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


    delivery_type = fields.Selection([
        ('third_party_billing', 'Third Party Billing'),
        ('prepay_and_add', 'Prepay & Add'),
        ],string="Ship Billing")
    delivery_method = fields.Many2one('delivery.method.dynamic', string='Provider')
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
    account_number = fields.Char()

    @api.onchange('delivery_method')
    def _onchange_partner_id(self):
        self.fedex = False
        self.dhl = False
        self.usps = False
        self.ups = False
        if self.delivery_method.name == 'FEDEX':
            self.fedex = True
        if self.delivery_method.name == 'DHL':
            self.dhl = True
        if self.delivery_method.name == 'USPS':
            self.usps = True
        if self.delivery_method.name == 'UPS':
            self.ups = True


    @api.onchange('delivery_method')
    def _get_account_number(self):
        if self.delivery_method.name == 'FEDEX':
            last_id = self.env['delivery.carrier'].sudo().search([('delivery_type', '=', self.delivery_method.name.lower() )],order="id desc", limit=1)
            self.account_number = last_id.fedex_account_number
        if self.delivery_method.name == 'DHL':
            last_id = self.env['delivery.carrier'].sudo().search([('delivery_type', '=', self.delivery_method.name.lower() )],order="id desc", limit=1)
            self.account_number = last_id.dhl_account_number
        if self.delivery_method.name == 'USPS':
            last_id = self.env['delivery.carrier'].sudo().search([('delivery_type', '=', self.delivery_method.name.lower() )],order="id desc", limit=1)
            self.account_number = last_id.usps_username
        if self.delivery_method.name == 'UPS':
            last_id = self.env['delivery.carrier'].sudo().search([('delivery_type', '=', self.delivery_method.name.lower() )], limit=1)
            self.account_number = last_id.ups_access_number

class StrategicPurchasing(models.Model):
    _name = 'delivery.method.dynamic'
    _auto = False

    name = fields.Char(string='Name')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as
            select 
            min(id) as id,
            UPPER(delivery_type) as name
            from
            delivery_carrier
            where delivery_type not in ('base_on_rule','fixed')
            group by delivery_type;
                """ % (self._table))