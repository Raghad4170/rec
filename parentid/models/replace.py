from odoo import models, api, _, fields

class Replace(models.Model):
    _name = "note.replace"
    _description = 'استبدالات الشروط والأحكام'
    
    name = fields.Char(string='الاختصار')
    sale_field = fields.Selection(string='الحقل المستبدل له', selection=lambda self: self.dynamic_selection())

    def dynamic_selection(self):
        model = self.env['sale.order']
        selection_list=[]
        for field in model._fields.values():
            if field.type != 'one2many':
                field_list =[]
                field_list.append(field.name)
                field_list.append(field.string)
                selection_list.append(tuple(field_list))
        return selection_list