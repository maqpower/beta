from odoo import api, fields, models


class Equiepment(models.Model):
    """ Inherit the equiepment to add favicon. """
    _inherit = 'service.equipment'

    isequipment_located_this_address = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Equipment Is Located In This Address', default='yes')
    street = fields.Char()
    street2 = fields.Char()
    zip1 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict')
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict',)
    location_indoors_outdoors = fields.Selection([
        ('indoors', 'Indoors'),
        ('outdoors', 'Outdoors')
    ], string='loc', default='indoors')
    google_map=fields.Char(string='map')