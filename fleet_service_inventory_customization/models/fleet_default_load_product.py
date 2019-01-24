# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import Warning,UserError, ValidationError
from datetime import datetime, timedelta

class FleetDefaultLoadProduct(models.Model):
    _name = 'fleet.product'

    fleet_product_line = fields.One2many('fleet.product.line','fleet_product_line_id',string ="Fleet Products")
    name = fields.Char("Product List",index=True)

    _sql_constraints = [('fleet_product_unique', 'unique(name)', 'Fleet product name should be unique..!'), ]
    
class FleetProductLine(models.Model): 
    _name = 'fleet.product.line'

    fleet_product_line_id = fields.Many2one('fleet.product',string='Fleet Product Id')
    product_id = fields.Many2one('product.product',string='Product')
    name = fields.Text(string="Description")
    product_qty = fields.Float(string="Required Quantity")
    re_order_qty = fields.Float(string="Re Order Quantity")

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            name = self.product_id.name_get()
            desc=name[0][1]
            if self.product_id.description_sale:
                desc += '\n' + self.product_id.description_sale
            self.name = desc
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()
        for order in self:
            order.order_line._action_launch_procurement_rule()
            
            
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_move', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                continue
            qty = 0.0
            for move in line.move_ids.filtered(lambda r: r.state != 'cancel'):
                qty += move.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue
 
            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)
 
            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty
            try:
                if line.order_id.is_service_quote_temp==True:
                    self.env['procurement.group'].run(line.product_id, product_qty, line.product_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
                else:
                    pass
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True
  
