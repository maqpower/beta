
from odoo import models, fields


class CustomWebsite(models.Model):
    _inherit = "website"

    def check_for_html_data(self):
        static_html = "<p><br></p>"
        return static_html
