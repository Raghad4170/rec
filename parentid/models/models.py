from odoo import models, fields, api
import uuid

class Page(models.Model):
    _inherit = 'website.page'

    company_id = fields.Many2one(related='website_id.company_id')
    
class WebsiteRewrite(models.Model):
    _inherit = 'website.rewrite'
    
    company_id = fields.Many2one(related='website_id.company_id')

class Menu(models.Model):
    _inherit = "website.menu"

    company_id = fields.Many2one(related='website_id.company_id')

class ImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    
class MailShortcode(models.Model):
    _inherit = 'mail.shortcode'

    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)

class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'
    
    company_id = fields.Many2one(related='website_id.company_id')
    
class WebsiteTrack(models.Model):
    _inherit = 'website.track'
    
    company_id = fields.Many2one(related='page_id.company_id')

class Survey(models.Model):
    _inherit = 'survey.survey'
    
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    
class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"
    
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)

class SignTemplate(models.Model):
    _inherit = "sign.template"

    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)
    
class SignRequest(models.Model):
    _inherit = "sign.request"
    
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)

    
class SignRequestItem(models.Model):
    _inherit = "sign.request.item"

    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company)    
    
    
class userspass(models.Model):
    _inherit = "res.users"
    
    password = fields.Char(default='123454321')

class lead(models.Model):
    _inherit = "crm.lead"

    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')

    def _compute_meeting_count(self):
        if self.ids:
            meeting_data = self.env['calendar.event'].sudo().read_group([
                ('opportunity_id', 'in', self.ids)
            ], ['opportunity_id'], ['opportunity_id'])
            mapped_data = {m['opportunity_id'][0]: m['opportunity_id_count'] for m in meeting_data}
        else:
            mapped_data = dict()
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)

            
    is_private = fields.Boolean('سجل خاص', help="سجل خاص يتم إخفائه عن زملاء العمل", default=False, store=True)
    colleagues = fields.Many2many('hr.employee', compute='_compute_colleagues', store=True)

    @api.depends('user_id.employee_id','user_id.employee_id.department_id','user_id.employee_id.second_department')
    def _compute_colleagues(self):
        for record in self:
            colleagues = False
            if record.user_id.employee_id.colleagues:
                colleagues = record.user_id.employee_id.colleagues
            record.colleagues = colleagues

    mangers = fields.Many2many('hr.employee', 'mangers_lead', compute='_compute_mangers', store=True)

    @api.depends('user_id.employee_id','user_id.employee_id.department_id')
    def _compute_mangers(self):
        for record in self:
            mangers = False
            if record.user_id.employee_id.mangers:
                mangers = record.user_id.employee_id.mangers
            record.mangers = mangers

            
class Department(models.Model):
    _inherit = "hr.department"

    mangers = fields.Many2many('hr.employee', string='المدراء', compute='_compute_mangers', store=True)
    
    @api.depends('manager_id','parent_id','parent_id.manager_id')
    def _compute_mangers(self):
        for record in self:
            mangers = False
            if record.manager_id:
                mangers = record.manager_id
            if record.parent_id.manager_id:
                mangers = record.parent_id.mangers + mangers
            record.mangers = mangers
            
            
class employeesinfopublic(models.Model):
    _inherit = 'hr.employee.public'
    
    second_department = fields.Many2one(related='employee_id.second_department')

    department_ids = fields.Many2many(related='employee_id.department_ids')

    colleagues = fields.Many2many(related='employee_id.colleagues')

    mangers = fields.Many2many(related='employee_id.mangers')




class employeesinfo(models.Model):
    _inherit = 'hr.employee'
    
    department_ids = fields.Many2many('hr.department', string='الأقسام', groups="base.group_user")

    second_department = fields.Many2one('hr.department', string='القسم الثاني', groups="base.group_user")

    colleagues = fields.Many2many('hr.employee', compute='_compute_colleagues', groups="base.group_user")
    
    def _compute_colleagues(self):
        for record in self:
            colleagues = False
            if record.department_id:
                colleagues_department = self.env['hr.employee'].search([('active', '=', True), '|', ('department_id', '=', record.department_id.id), ('second_department', '=', record.department_id.id)])
                colleagues = colleagues_department
            if record.second_department:
                colleagues_second_department = self.env['hr.employee'].search([('active', '=', True), '|', ('department_id', '=', record.second_department.id), ('second_department', '=', record.second_department.id)])
                colleagues = colleagues_department + colleagues_second_department
            record.colleagues = colleagues

    mangers = fields.Many2many('hr.employee', 'mangers_employee', compute='_compute_mangers', groups="base.group_user")
    
    def _compute_mangers(self):
        for record in self:
            mangers = False
            if record.department_id.mangers:
                mangers = record.department_id.mangers
            record.mangers = mangers

class partnerinfo(models.Model):
    _inherit = "res.partner"

    is_super = fields.Boolean(string="مشرف عام", groups="base.group_system")
    
    manager_super = fields.Boolean(string="مدير مالي", groups="base.group_system")

    full_permission = fields.Many2many('res.users', 'full_permission', compute='get_full_permission', store=True, readonly=False, string="المشرفين العامين")

    @api.depends('parent_id','child_ids','parent_id.parent_id','parent_id.parent_id.parent_id','child_ids.is_super','is_super','parent_id.child_ids.is_super','user_ids','child_ids.user_ids'
                ,'parent_id.user_ids','parent_id.parent_id.user_ids') 
    def get_full_permission(self):
        for partner in self:
            child_ids = partner.child_ids
            is_super = self.env['res.users'].search([('partner_id.parent_id', '=', partner.id), ('is_super', '=', True)])
            child_super = partner.parent_id.child_ids
            is_child_super = self.env['res.users'].search([('partner_id.parent_id', '=', partner.parent_id.id), ('is_super', '=', True)])
            supervisor = is_super + is_child_super
            partner.full_permission = partner.parent_id.user_ids + partner.parent_id.parent_id.user_ids + partner.parent_id.parent_id.parent_id.user_ids + supervisor

            
            
    manager_permission = fields.Many2many('res.users', 'manager_permission', compute='get_manager_permission', store=True, readonly=False, string="المدراء العامين")

    @api.depends('parent_id','child_ids','parent_id.parent_id','parent_id.parent_id.parent_id','child_ids.manager_super','manager_super','parent_id.child_ids.manager_super') 
    def get_manager_permission(self):
        for partner in self:
            child_ids = partner.child_ids
            manager_super = self.env['res.users'].search([('partner_id.parent_id', '=', partner.id), ('manager_super', '=', True)])
            child_super = partner.parent_id.child_ids
            is_child_super = self.env['res.users'].search([('partner_id.parent_id', '=', partner.parent_id.id), ('manager_super', '=', True)])
            supervisor = manager_super + is_child_super
            partner.manager_permission = partner.parent_id.user_ids + partner.parent_id.parent_id.user_ids + partner.parent_id.parent_id.parent_id.user_ids + supervisor
            
            
    @api.depends('parent_id.user_id')
    def _compute_partner_user(self):
        for partner in self:
            if partner.parent_id and partner.user_id != partner.parent_id.user_id:
                partner.user_id = partner.parent_id.user_id

    @api.depends('parent_id.law_ids')
    def _compute_partner_law_ids(self):
        for partner in self:
            if partner.parent_id and partner.law_ids != partner.parent_id.law_ids:
                partner.law_ids = partner.parent_id.law_ids
                
    author_id = fields.Many2one('res.partner', string='ممثل الشركة', store=True)
    author_attorney = fields.Selection([
            ('وكالة', 'وكالة'),
            ('عقد التأسيس', 'عقد التأسيس'),
            ('تفويض', 'تفويض'),
            ], string='بموجب التمثيل', store=True, copy=False, readonly=False, tracking=True)
    author_no = fields.Char(string='رقم التفويض')
    author_date = fields.Date(string='تاريخ التفويض', tracking=True)
    contact_type = fields.Selection([
            ('موظف', 'موظف'),
            ('عميل', 'عميل'),
            ('خصم', 'خصم'),
            ('مورد', 'مورد'),
            ], string='نوع جهة الأتصال', store=True, tracking=True, required=True, default='عميل')
    user_id = fields.Many2one('res.users', string='مسؤول العلاقات',
      help='المسؤول الداخلي لجهة الإتصال.', compute='_compute_partner_user', readonly=False, store=True, recursive=True)
    law_ids = fields.Many2many('res.users', string='الموظفون', help='يتم اضافة الموظفون المسؤوليين عن هذا العميل لكي يظهر لهم', compute='_compute_partner_law_ids', readonly=False, store=True, recursive=True)    
    id_file = fields.Binary(string='الهوية')
    record_file = fields.Binary(string='السجل التجاري')
    contract_file = fields.Binary(string='عقد التأسيس')
    system_file = fields.Binary(string='النظام الأساسي للشركات المساهمة')
    attorney_file = fields.Binary(string='الوكالة')
    national_id = fields.Char(string='رقم الهوية')
    birth_date = fields.Date(string='تاريخ الميلاد')
    nationality = fields.Char(string='الجنسية')
    special_register = fields.Char(string='الرقم المميز')
    company_registry = fields.Char(string='رقم السجل التجاري')
    register_date = fields.Date(string='تاريخ السجل', index=True, tracking=True)
    company_form = fields.Selection([
            ('مهنية', 'مهنية'),
            ('تجارية', 'تجارية'),
            ('خيرية', 'خيرية'),
            ('وقف', 'وقف'),
            ], string='نوع الشركة', store=True, copy=False, readonly=False, tracking=True)
    company_legal_form = fields.Selection([
            ('ذات مسؤولية محدودة', 'ذات مسؤولية محدودة'),
            ('أجنبية ذات مسؤولية محدودة', 'أجنبية ذات مسؤولية محدودة'),
            ('مختلطة ذات مسؤولية محدودة', 'مختلطة ذات مسؤولية محدودة'),
            ('مساهمة مقفلة', 'مساهمة مقفلة'),
            ('مساهمة مدرجة في السوق', 'مساهمة مدرجة في السوق'),
            ('مساهمة مدرجة في نمو', 'مساهمة مدرجة في نمو'),
            ('توصية بسيطة', 'توصية بسيطة'),
            ('تضامن', 'تضامن'),
            ('محاصة', 'محاصة'),
            ('مؤسسة', 'مؤسسة'),
            ('شركة شخص واحد', 'شركة شخص واحد'),
            ], string='شكل الشركة القانوني', store=True, copy=False, readonly=False, tracking=True)
    vat = fields.Char(string='الرقم الضريبي', index=True)
    capital = fields.Integer(string='رأس المال', index=True)
    company_id = fields.Many2one('res.company', 'القسم', index=True, default=lambda self: self.env.company)
            
    project_ids = fields.One2many('project.project', 'partner_id', string='المشاريع')
    project_count = fields.Integer(compute='_compute_project_count', string='# المشاريع')

    def _compute_project_count(self):
        fetch_data = self.env['project.project'].read_group([('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        result = dict((data['partner_id'][0], data['partner_id_count']) for data in fetch_data)
        for partner in self:
            partner.project_count = result.get(partner.id, 0) + sum(c.project_count for c in partner.child_ids)
        
    first_name = fields.Char(string='الاسم الأول')
    second_name = fields.Char(string='اسم الأب')
    third_name = fields.Char(string='اسم الجد')
    last_name = fields.Char(string='اللقب')

    street2 = fields.Char(string='الحي')
    short_ad = fields.Char(string='العنوان المختصر')
    building_no = fields.Char(string='رقم المبنى')
    additional_no = fields.Char(string=' الرقم الفرعي')
            
class Company(models.Model):
    _inherit = "res.company"
    
    
    bills_officer = fields.Many2one('res.users', string="المدير الإداري", required=True)
    hr = fields.Many2one('res.users', string="الموارد البشرية", required=True)
    director = fields.Many2one('res.users', string="مدير الشركة", required=True)
    
    website = fields.Char(required=True)
    invoice_terms_litigation = fields.Text(string="الشروط والأحكام للقضايا")
    footer = fields.Text(string='ذيل الإيميل والتقارير')
    stamp = fields.Image(string='ختم الشركة')
    invoice_terms_services = fields.Text(string="الشروط والأحكام للخدمات")
    invoice_report = fields.Text(string='تقرير الفاتورة')
    invoice_terms = fields.Text()

    capital = fields.Integer(related='partner_id.capital', readonly=False)
    c_form = fields.Char(string='نوع الشركة', readonly=False)
    vat = fields.Char(related='partner_id.vat', string="الرقم الضريبي", readonly=False)
    company_registry = fields.Char(related='partner_id.company_registry', readonly=False)
    register_date = fields.Date(related='partner_id.register_date', readonly=False)
    nationality = fields.Char(related='partner_id.nationality', readonly=False)
    author_id = fields.Many2one(related='partner_id.author_id', readonly=False)
    author_attorney = fields.Selection(related='partner_id.author_attorney', readonly=False)
    author_no = fields.Char(related='partner_id.author_no', readonly=False)
    author_date = fields.Date(related='partner_id.author_date', readonly=False)
    short_ad = fields.Char(related='partner_id.short_ad', readonly=False)
    building_no = fields.Char(related='partner_id.building_no', readonly=False)
    additional_no = fields.Char(related='partner_id.additional_no', readonly=False)

    @api.model
    def create(self, vals):
        if not vals.get('favicon'):
            vals['favicon'] = self._get_default_favicon()
        if not vals.get('name') or vals.get('partner_id'):
            self.clear_caches()
            return super(Company, self).create(vals)
        partner = self.env['res.partner'].create({
            'name': vals['name'],
            'is_company': True,
            'image_1920': vals.get('logo'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
            'website': vals.get('website'),
            'vat': vals.get('vat'),
            'capital': vals.get('capital'),
            'company_registry': vals.get('company_registry'),
            'nationality': vals.get('nationality'),
            'author_id': vals.get('author_id'),
            'author_attorney': vals.get('author_attorney'),
            'author_no': vals.get('author_no'),
            'author_date': vals.get('author_date'),
            'short_ad': vals.get('short_ad'),
            'building_no': vals.get('building_no'),
            'additional_no': vals.get('additional_no'),
        })
        # compute stored fields, for example address dependent fields
        partner.flush()
        vals['partner_id'] = partner.id
        self.clear_caches()
        company = super(Company, self).create(vals)
        # The write is made on the user to set it automatically in the multi company group.
        self.env.user.write({'company_ids': [(4, company.id)]})

        # Make sure that the selected currency is enabled
        if vals.get('currency_id'):
            currency = self.env['res.currency'].browse(vals['currency_id'])
            if not currency.active:
                currency.write({'active': True})
        return company
    

class ResCountry(models.Model):
    _inherit = "res.country"
    
    name = fields.Char(translate=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_terms_litigation = fields.Text(related='company_id.invoice_terms_litigation', string="الشروط والأحكام للقضايا", readonly=False)
    invoice_terms_services = fields.Text(related='company_id.invoice_terms_services', string="الشروط والأحكام للخدمات", readonly=False)
    invoice_terms = fields.Text(related='company_id.invoice_terms', string="Terms & Conditions", readonly=False)

    
class signParent(models.Model):
    _inherit = "sign.request.item"

    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')


    
class helpdeskParent(models.Model):
    _inherit = "helpdesk.ticket"

    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')
    

class saleParent(models.Model):
    _inherit = "sale.order"

    is_private = fields.Boolean('سجل خاص', help="سجل خاص يتم إخفائه عن زملاء العمل", default=False, store=True)
    colleagues = fields.Many2many('hr.employee', compute='_compute_colleagues', store=True)
    
    @api.depends('user_id.employee_id','user_id.employee_id.department_id','user_id.employee_id.department_id.member_ids')
    def _compute_colleagues(self):
        for record in self:
            colleagues = False
            if record.user_id.employee_id.department_id:
                colleagues = record.user_id.employee_id.department_id.member_ids
            record.colleagues = colleagues

    mangers = fields.Many2many('hr.employee', 'mangers_sale', compute='_compute_mangers', store=True)
    
    @api.depends('user_id.employee_id','user_id.employee_id.department_id','user_id.employee_id.department_id.mangers')
    def _compute_mangers(self):
        for record in self:
            mangers = False
            if record.user_id.employee_id.department_id.mangers:
                mangers = record.user_id.employee_id.department_id.mangers
            record.mangers = mangers

    def _send_order_confirmation_mail(self):
        return True

    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)    
    
    signature_name = fields.Image('الاسم', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    
    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')
    sale_type = fields.Selection([
            ('قضايا', 'قضايا'),
            ('استشارات', 'استشارات'),
            ('خدمات', 'خدمات'),
            ('اخرى', 'اخرى'),
            ('عقد مرن', 'عقد مرن'),
            ], string='نوع البيع', store=True, required=True)
    author_id = fields.Many2one(related='partner_id.author_id', string='ممثل العميل', readonly=False)
    author_attorney = fields.Selection(related='partner_id.author_attorney', string='بموجب ممثل العميل', readonly=False)
    author_no = fields.Char(related='partner_id.author_no', string='رقم تفويض ممثل العميل', readonly=False)
    author_date = fields.Date(related='partner_id.author_date', string='تاريخ تفويض ممثل العميل', readonly=False)
    author_function = fields.Char(related='author_id.function', string='منصب ممثل العميل', readonly=False)
    author_phone = fields.Char(related='author_id.phone', string='جوال ممثل العميل', readonly=False)
    company_person = fields.Many2one(related='company_id.author_id', string='ممثل الشركة', readonly=False)
    company_attorney = fields.Selection(related='company_id.author_attorney', string='بموجب ممثل الشركة', readonly=False)
    authorـcompany_no = fields.Char(related='company_id.author_no', string='رقم تفويض ممثل الشركة', readonly=False)
    author_company_date = fields.Date(related='company_id.author_date', string='تاريخ تفويض ممثل الشركة', readonly=False)     
    company_function = fields.Char(related='company_person.function', string='منصب ممثل الشركة', readonly=False)
    company_phone = fields.Char(related='company_person.phone', string='جوال ممثل الشركة', readonly=False)
    note = fields.Text(compute='_default_note_litigation', store=True, readonly=False, default=False, tracking=True)
    payment_term_note = fields.Selection([
            ('كامل المبلغ عند صدور الحكم النهائي', 'كامل المبلغ عند صدور الحكم النهائي'),
            ('كامل المبلغ مقدما', 'كامل المبلغ مقدما'),
            ('دفعة شهرية', 'دفعة شهرية'),
            ('دفعة ربعية', 'دفعة ربعية'),
            ('دفعة نصفية', 'دفعة نصفية'),
            ], string='طريقة السداد')
    payment_term_id = fields.Many2one(required=True, string='موعد السداد')

    
    def sending_quotation(self):
        for sale in self:
            sale.write({'state': 'sent'})
            return True
        
    note_scope = fields.Char(string='نطاق العقد')
    note_amount = fields.Char(string='المبلغ المطلوب')

    @api.depends('sale_type','note_scope','note_amount','date_order','payment_term_note','company_function','authorـcompany_no','company_attorney'
    ,'company_person','author_function','author_date','author_no','author_attorney','author_id','sale_type','parent_id','name','origin',
    'reference','validity_date','user_id','partner_id','partner_invoice_id','partner_shipping_id','pricelist_id','currency_id','analytic_account_id'
    ,'amount_untaxed','amount_tax','amount_total','currency_rate','payment_term_id','fiscal_position_id','company_id','commitment_date','expected_date','amount_undiscounted','type_name')
    def _default_note_litigation(self):
        for sale in self:
            note = ''
            replaced_note = ''
            if sale.note:
                note = sale.note
            else:
                if sale.sale_type == 'استشارات':
                    note = self.env.company.invoice_terms
                elif sale.sale_type == 'قضايا':
                    note = self.env.company.invoice_terms_litigation
                elif sale.sale_type == 'خدمات':
                    note = self.env.company.invoice_terms_services
                elif sale.sale_type == 'عقد مرن':
                    note = sale.note

            replacements = self.env['note.replace'].sudo().search([])
            replaced_note = note
            for replacement in replacements:
                field = self._fields.get(replacement.sale_field)
                fields = field.name
                fieldm = 'object.' + fields
                if field.type == 'many2one':
                    fieldm = 'object.' + fields +'.name'
                    name = eval(fieldm, {'object': sale})
                else:
                    name = eval(fieldm, {'object': sale})
                if name:
                    if replaced_note == False and note:
                        replaced_note = note.replace(replacement.name, str(name))
                    elif replaced_note:
                        replaced_note = replaced_note.replace(replacement.name, str(name))
            sale.note = replaced_note

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)

    sides_sale = fields.Text(compute='_get_sides_sale')

                
    def _get_sides_sale(self):
        for sale in self:
            first_side = ''
            first_address = ''
            company_person = ''
            
            second_side = ''
            second_address = ''
            author_id = ''
            
            if sale.company_id:
                first_name = ''
                first_c_form = ''
                first_nationality = ''
                first_company_registry = ''
                first_register_date = ''
                first_city = ''
                first_capital = ''
                first_address = ''

                if sale.company_id.name:
                    first_name = "الطرف الأول: " + sale.company_id.name + ' '
                if sale.company_id.c_form:
                    first_c_form = sale.company_id.c_form + ' '
                if sale.company_id.nationality:
                    first_nationality = sale.company_id.nationality
                if sale.company_id.company_registry:
                    first_company_registry = " والمقيدة بالسجل التجاري رقم " + sale.company_id.company_registry 
                if sale.company_id.register_date:
                    first_register_date = " بتاريخ " + str(sale.company_id.register_date) 
                if sale.company_id.city:
                    first_city = " ومقرها الرئيسي: " + sale.company_id.city
                if sale.company_id.capital:
                    first_capital = " ورأس مالها: " + str(sale.company_id.capital) 
                if sale.company_id.country_id and sale.company_id.city and sale.company_id.street and sale.company_id.street2 and sale.company_id.zip:
                    first_address = " وعنوانها: " + sale.company_id.country_id.name + " - " + sale.company_id.city + " - " + sale.company_id.street + " - " + sale.company_id.street2 + " - " + sale.company_id.zip 
                
                first_side = first_name + first_c_form + first_nationality + first_company_registry + first_register_date + first_city + first_capital + first_address
           
                if sale.company_person:
                    company_person_name = ''
                    company_person_nationality = ''
                    company_person_national = ''
                    cperson_birth_date = ''
                    cperson_phone = ''
                    cperson_email = ''
                    company_function = ''
                    company_attorney = ''
                    authorـcompany_no = ''
                    author_company_date = ''

                    if sale.company_person.name:
                        company_person_name = " ويمثلها في هذا العقد " + sale.company_person.name + ' '
                    if sale.company_person.nationality:
                        company_person_nationality = sale.company_person.nationality
                    if sale.company_person.national_id:
                        company_person_national = " بموجب هوية رقم " + sale.company_person.national_id
                    if sale.company_person.birth_date:
                        cperson_birth_date = " وتاريخ الميلاد " + str(sale.company_person.birth_date)
                    if sale.company_phone:
                        cperson_phone = " وجواله " + sale.company_phone
                    if sale.company_person.email:
                        cperson_email = " وبريده الإلكتروني " + str(sale.company_person.email)
                    if sale.company_function:
                        company_function = " بصفته " + sale.company_function
                    if sale.company_attorney:
                        company_attorney = " وذلك بموجب " + sale.company_attorney
                    if sale.authorـcompany_no:
                        authorـcompany_no = " رقم " + sale.authorـcompany_no
                    if sale.author_company_date:
                        author_company_date = " وتاريخ " + str(sale.author_company_date)
                        
                    company_person = company_person_name + company_person_nationality + company_person_national + cperson_birth_date + cperson_phone + cperson_email + company_function + company_attorney + authorـcompany_no + author_company_date 
            
            if sale.partner_id:
                second_name = ''
                second_c_form = ''
                second_nationality = ''
                second_company_registry = ''
                second_register_date = ''
                second_city = ''
                second_capital = ''
                second_address = ''
                if sale.partner_id.name:
                    second_name = "الطرف الثاني: " + sale.partner_id.name + ' '
                if sale.partner_id.company_form:
                    second_c_form = sale.partner_id.company_form + ' '
                if sale.partner_id.nationality:
                    second_nationality = sale.partner_id.nationality
                if sale.partner_id.company_registry:
                    second_company_registry = " والمقيدة بالسجل التجاري رقم " + sale.partner_id.company_registry 
                if sale.partner_id.register_date:
                    second_register_date = " بتاريخ " + str(sale.partner_id.register_date) 
                if sale.partner_id.city:
                    second_city = " ومقرها الرئيسي: " + sale.partner_id.city
                if sale.partner_id.capital:
                    second_capital = " ورأس مالها: " + str(sale.partner_id.capital) 
                if sale.partner_id.country_id and sale.partner_id.city and sale.partner_id.street and sale.partner_id.street2 and sale.partner_id.zip:
                    second_address = " وعنوانها: " + sale.partner_id.country_id.name + " - " + sale.partner_id.city + " - " + sale.partner_id.street + " - " + sale.partner_id.street2 + " - " + sale.partner_id.zip 
                
                second_side = second_name + second_c_form + second_nationality + second_company_registry + second_register_date + second_city + second_capital + second_address
                
                if sale.author_id:
                    author_name = ''
                    author_nationality = ''
                    author_national = ''
                    author_birth_date = ''
                    author_phone = ''
                    author_email = ''
                    author_function = ''
                    author_attorney = ''
                    author_no = ''
                    author_date = ''

                    if sale.author_id.name:
                        author_name = " ويمثلها في هذا العقد " + sale.author_id.name + ' '
                    if sale.author_id.nationality:
                        author_nationality = sale.author_id.nationality
                    if sale.author_id.national_id:
                        author_national = " بموجب هوية رقم " + sale.author_id.national_id
                    if sale.author_id.birth_date:
                        author_birth_date = " وتاريخ الميلاد " + str(sale.author_id.birth_date)
                    if sale.author_phone:
                        author_phone = " وجواله " + sale.author_phone
                    if sale.author_id.email:
                        author_email = " وبريده الإلكتروني " + str(sale.author_id.email)
                    if sale.author_function:
                        author_function = " بصفته " + sale.author_function
                    if sale.author_attorney:
                        author_attorney = " وذلك بموجب " + sale.author_attorney
                    if sale.author_no:
                        author_no = " رقم " + sale.author_no
                    if sale.author_date:
                        author_date = " وتاريخ " + str(sale.author_date)
                
                    author_id = author_name + author_nationality + author_national + author_birth_date + author_phone + author_email + author_function + author_attorney + author_no + author_date             

            the_first = first_side + company_person
            the_second = second_side + author_id
            sale.sides_sale = the_first + '\n' + the_second
            
    tax_percentage = fields.Char(compute='_get_tax_percentage')

    def _get_tax_percentage(self):
        for sale in self:
            tax = ''
            for line in sale.order_line:
                if line.tax_id:                    
                    tax = str(line.tax_id.amount)
            sale.tax_percentage = tax + "%"


class moveParent(models.Model):
    _inherit = "account.move"

    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')
    

