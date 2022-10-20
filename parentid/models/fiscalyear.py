from odoo import models, fields, api
            
class ResCompany(models.Model):
    _inherit = "res.company"
    
    def check_updation(self):
        for company in self:
            
            mail_template = self.env.ref('litigation.send_litigation_partner')
            mail_template.send_mail(company.id, force_send=True, notif_layout='mail.mail_notification_light')

