# -*- coding: utf-8 -*-
from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timedelta, date
import pytz
from odoo.tools.misc import formatLang
from odoo.tools import float_compare, date_utils, email_split, email_re

class QRCodeInvoice(models.Model):
    _inherit = 'account.move'

    qr_invoice = fields.Binary(compute='_generate_qr_code')    
    message = fields.Text(compute='get_message')
    invoice_date = fields.Datetime()
    invoice_date_due = fields.Datetime()

    invoice_date_due_report = fields.Date(compute='get_invoice_date_due')

    def get_invoice_date_due(self):
        for move in self:
            invoice_date_due_report = False
            if move.invoice_date_due:
                invoice_date_due_report = move.invoice_date_due.date()
            move.invoice_date_due_report = invoice_date_due_report


    def get_message(self):
        for move in self:
            invoice_date = datetime.now()
            if move.invoice_date:
                dt = pytz.timezone('UTC').localize(move.invoice_date).astimezone(pytz.timezone(self.env.user.tz))
                str_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                invoice_date = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
            amount_total = formatLang(self.env, move.amount_total)
            amount_tax = formatLang(self.env, move.amount_tax)
            move.message = (move.company_id.name + '\n' + 'رقم تسجيل ضريبة الـقـيـمـة الـمـضـافة: ' + str(move.company_id.vat) + '\n' + 'تاريخ الفاتورة: ' + str(invoice_date) + '\n' 
                            + 'ضــريــبـة الـقـيـمـة الـمـضـافـة: ' + str(amount_tax) + '\n' + 'إجمالي الفاتورة مع الضريبة: ' + str(amount_total))    
    
    def get_qr_code(self, data):
        qr = qrcode.QRCode(
                 version=1,
                 error_correction=qrcode.constants.ERROR_CORRECT_L,
                 box_size=20,
                 border=4,
                 )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        return qr_img
    
    def _generate_qr_code(self):
        for move in self:
            data = move.message
            move.qr_invoice = move.get_qr_code(data)

            
    def _get_accounting_date(self, invoice_date, has_tax):
        """Get correct accounting date for previous periods, taking tax lock date into account.

        When registering an invoice in the past, we still want the sequence to be increasing.
        We then take the last day of the period, depending on the sequence format.
        If there is a tax lock date and there are taxes involved, we register the invoice at the
        last date of the first open period.

        :param invoice_date (datetime.date): The invoice date
        :param has_tax (bool): Iff any taxes are involved in the lines of the invoice
        :return (datetime.date):
        """
        tax_lock_date = self.company_id.tax_lock_date
        today = datetime.now()
        if invoice_date and tax_lock_date and has_tax and invoice_date <= tax_lock_date:
            invoice_date = tax_lock_date + timedelta(days=1)

        if self.is_sale_document(include_receipts=True):
            return invoice_date
        elif self.is_purchase_document(include_receipts=True):
            highest_name = self.highest_name or self._get_last_sequence(relaxed=True)
            number_reset = self._deduce_sequence_number_reset(highest_name)
            if not highest_name or number_reset == 'month':
                if (today.year, today.month) > (invoice_date.year, invoice_date.month):
                    return date_utils.get_month(invoice_date)[1]
                else:
                    return max(invoice_date, today)
            elif number_reset == 'year':
                if today.year > invoice_date.year:
                    return date(invoice_date.year, 12, 31)
                else:
                    return max(invoice_date, today)
        return invoice_date

