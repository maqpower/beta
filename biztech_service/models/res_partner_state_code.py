from odoo import models, api, fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'
    _rec_name = 'code'
