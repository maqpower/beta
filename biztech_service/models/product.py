from odoo import api, fields, models
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    @api.one
    def _sale_order_count(self):
        wo_ids_list = []
        domain = [('product_id', '=', self.id)]
        sale_odr = self.env['sale.order.line'].search(domain)
        for order in sale_odr:
            wo_ids_list.append(order.order_id.id)
        self.sales_order_count = len(wo_ids_list)

    @api.multi
    def action_view_saleorder(self):
        wo_ids_list = []
        action = self.env.ref('biztech_service.action_product_sale_list').read()[0]
        domain = [('product_id', '=', self.id)]
        sale_odr = self.env['sale.order.line'].search(domain)
        for order in sale_odr:
            wo_ids_list.append(order.order_id.id)
            if sale_odr:
                action['domain'] = [('id', 'in',wo_ids_list)]
                action['context'] = {'search_default_id': order.order_id.id}
        return action

    sales_order_count = fields.Integer(compute='_sale_order_count', string='Sales Order')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('product_variant_ids.sales_order_count')
    def _sale_order_count(self):
        for product in self:
            product.sales_order_count = sum([p.sales_order_count for p in product.with_context(active_test=False).product_variant_ids])

    @api.multi
    @api.depends('product_variant_ids.sales_order_count')
    def action_view_saleorder(self):
        wo_ids_list = []
        action = self.env.ref('biztech_service.action_product_sale_list').read()[0]
        domain = [('product_id', '=', self.product_variant_id.id)]
        sale_odr = self.env['sale.order.line'].search(domain)
        for order in sale_odr:
            wo_ids_list.append(order.order_id.id)
            if sale_odr:
                action['domain'] = [('id', 'in',wo_ids_list)]
                action['context'] = {'search_default_id': order.order_id.id}
        return action

    sales_order_count = fields.Integer(compute='_sale_order_count', string='Sales Order')
    