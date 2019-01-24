
from odoo import api, fields, models


class sale_order(models.Model):
    """Adds the fields for options of the customer comment"""
    _inherit = "sale.order"

    customer_comment = fields.Text('Customer Order Comment',
                                   default="No comment")
