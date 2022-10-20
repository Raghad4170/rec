from odoo import models, fields, api

class Company(models.Model):
    _inherit = "res.company"
    
    def update_expiration_date(self):
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('database.expiration_date', '2032-6-7 04:11:37')
