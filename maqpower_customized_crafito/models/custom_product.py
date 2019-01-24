
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_info = fields.Html(
        string="Information", help="Summary of product information", translate=True)
    product_features = fields.Html(
        string="Features", help="Details of product features", translate=True)
    product_options = fields.Html(
        string="Options", help="Details of product options", translate=True)
    product_features_and_benefits = fields.Html(
        string="Features and Benefits", help="Details of product features and benefits", translate=True)
    product_specification = fields.Html(
        string="Specifications", help="Product Specifications", translate=True)
    product_extra_info = fields.Html(
        string="More Information", help="Detail information about product", translate=True)
    ask_for_quote = fields.Boolean(string='Ask for Quote?')
