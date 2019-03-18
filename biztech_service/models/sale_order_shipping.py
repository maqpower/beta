from odoo import fields, models, api,_
from odoo import tools

class SaleOrder(models.Model):
    _inherit = "sale.order"

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

    method_type_fedex = fields.Selection([('INTERNATIONAL_ECONOMY', 'INTERNATIONAL_ECONOMY'),
                                           ('INTERNATIONAL_PRIORITY', 'INTERNATIONAL_PRIORITY'),
                                           ('FEDEX_GROUND', 'FEDEX_GROUND'),
                                           ('FEDEX_2_DAY', 'FEDEX_2_DAY'),
                                           ('FEDEX_2_DAY_AM', 'FEDEX_2_DAY_AM'),
                                           ('FIRST_OVERNIGHT', 'FIRST_OVERNIGHT'),
                                           ('PRIORITY_OVERNIGHT', 'PRIORITY_OVERNIGHT'),
                                           ('STANDARD_OVERNIGHT', 'STANDARD_OVERNIGHT')],string='Delivery Method Type')
    method_type_dhl = fields.Many2one('product.packaging', string='Method Type')
    method_type_usps = fields.Selection([('First Class', 'First Class'),
                                         ('Priority', 'Priority'),
                                         ('Express', 'Express')],string='Delivery Method Type')
    method_type_ups = fields.Selection(
        get_ups_value, 
        string='Delivery Method Type')



