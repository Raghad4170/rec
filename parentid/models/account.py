# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

from babel.dates import format_datetime, format_date
from odoo import models, api, _, fields
from odoo.osv import expression
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang
import random
import ast
import requests
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    tax_percentage = fields.Char(compute='_get_tax_percentage')

    def _get_tax_percentage(self):
        for account in self:
            tax = ''
            for line in account.line_ids:
                if line.tax_ids:                    
                    tax = str(line.tax_ids.amount)
            account.tax_percentage = tax + "%"

    @api.model
    def _get_tax_totals(self, partner, tax_lines_data, amount_total, amount_untaxed, currency):
        lang_env = self.with_context(lang=partner.lang).env
        account_tax = self.env['account.tax']

        grouped_taxes = defaultdict(lambda: defaultdict(lambda: {'base_amount': 0.0, 'tax_amount': 0.0, 'base_line_keys': set()}))
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data['tax'].tax_group_id

            # Update subtotals priorities
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                # When needed, the default subtotal is always the most prioritary
                subtotal_title = _("المبلغ بدون ضريبة القيمة المضافة")
                new_priority = 0

            if subtotal_title not in subtotal_priorities or new_priority < subtotal_priorities[subtotal_title]:
                subtotal_priorities[subtotal_title] = new_priority

            # Update tax data
            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if 'base_amount' in line_data:
                # Base line
                if tax_group == line_data.get('tax_affecting_base', account_tax).tax_group_id:
                    # In case the base has a tax_line_id belonging to the same group as the base tax,
                    # the base for the group will be computed by the base tax's original line (the one with tax_ids and no tax_line_id)
                    continue

                if line_data['line_key'] not in tax_group_vals['base_line_keys']:
                    # If the base line hasn't been taken into account yet, at its amount to the base total.
                    tax_group_vals['base_line_keys'].add(line_data['line_key'])
                    tax_group_vals['base_amount'] += line_data['base_amount']

            else:
                # Tax line
                tax_group_vals['tax_amount'] += line_data['tax_amount']

        # Compute groups_by_subtotal
        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [{
                'tax_group_name': group.name,
                'tax_group_amount': amounts['tax_amount'],
                'tax_group_base_amount': amounts['base_amount'],
                'formatted_tax_group_amount': formatLang(lang_env, amounts['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(lang_env, amounts['base_amount'], currency_obj=currency),
                'tax_group_id': group.id,
                'group_key': '%s-%s' %(subtotal_title, group.id),
            } for group, amounts in sorted(groups.items(), key=lambda l: l[0].sequence)]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = [] # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append({
                'name': subtotal_title,
                'amount': subtotal_value,
                'formatted_amount': formatLang(lang_env, subtotal_value, currency_obj=currency),
            })

            subtotal_tax_amount = sum(group_val['tax_group_amount'] for group_val in groups_by_subtotal[subtotal_title])
            previous_subtotals_tax_amount += subtotal_tax_amount

        # Assign json-formatted result to the field
        return {
            'amount_total': amount_total,
            'amount_untaxed': amount_untaxed,
            'formatted_amount_total': formatLang(lang_env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(lang_env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals_list,
            'allow_tax_edition': False,
        }

class account_journal(models.Model):
    _inherit = "account.journal"
    
    name = fields.Char(translate=False)
                                        
    def get_journal_dashboard_datas(self):
        currency = self.currency_id or self.company_id.currency_id
        number_to_reconcile = number_to_check = last_balance = 0
        has_at_least_one_statement = False
        bank_account_balance = nb_lines_bank_account_balance = 0
        outstanding_pay_account_balance = nb_lines_outstanding_pay_account_balance = 0
        total_account_balance = 0
        title = ''
        number_draft = number_waiting = number_late = to_check_balance = 0
        sum_draft = sum_waiting = sum_late = 0.0
        if self.type in ('bank', 'cash'):
            last_statement = self._get_last_bank_statement(
                domain=[('move_id.state', '=', 'posted')])
            last_balance = last_statement.balance_end
            has_at_least_one_statement = bool(last_statement)
            bank_account_balance, nb_lines_bank_account_balance = self._get_journal_bank_account_balance(
                domain=[('move_id.state', '=', 'posted')])
            outstanding_pay_account_balance, nb_lines_outstanding_pay_account_balance = self._get_journal_outstanding_payments_account_balance(
                domain=[('move_id.state', '=', 'posted')])

            self._cr.execute('''
                SELECT COUNT(st_line.id)
                FROM account_bank_statement_line st_line
                JOIN account_move st_line_move ON st_line_move.id = st_line.move_id
                JOIN account_bank_statement st ON st_line.statement_id = st.id
                WHERE st_line_move.journal_id IN %s
                AND st.state = 'posted'
                AND NOT st_line.is_reconciled
            ''', [tuple(self.ids)])
            number_to_reconcile = self.env.cr.fetchone()[0]

            to_check_ids = self.to_check_ids()
            number_to_check = len(to_check_ids)
            to_check_balance = sum([r.amount for r in to_check_ids])
        #TODO need to check if all invoices are in the same currency than the journal!!!!
        elif self.type in ['sale', 'purchase']:
            title = _('Bills to pay') if self.type == 'purchase' else _('Invoices owed to you')
            self.env['account.move'].flush(['amount_residual', 'currency_id', 'move_type', 'invoice_date', 'company_id', 'journal_id', 'date', 'state', 'payment_state'])

            (query, query_args) = self._get_open_bills_to_pay_query()
            self.env.cr.execute(query, query_args)
            query_results_to_pay = self.env.cr.dictfetchall()

            (query, query_args) = self._get_draft_bills_query()
            self.env.cr.execute(query, query_args)
            query_results_drafts = self.env.cr.dictfetchall()

            today = fields.Date.context_today(self)
            query = '''
                SELECT
                    (CASE WHEN move_type IN ('out_refund', 'in_refund') THEN -1 ELSE 1 END) * amount_residual AS amount_total,
                    currency_id AS currency,
                    move_type,
                    invoice_date,
                    company_id
                FROM account_move move
                WHERE journal_id = %s
                AND date <= %s
                AND state = 'posted'
                AND payment_state in ('not_paid', 'partial')
                AND move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt');
            '''
            self.env.cr.execute(query, (self.id, today))
            late_query_results = self.env.cr.dictfetchall()
            curr_cache = {}
            (number_waiting, sum_waiting) = self._count_results_and_sum_amounts(query_results_to_pay, currency, curr_cache=curr_cache)
            (number_draft, sum_draft) = self._count_results_and_sum_amounts(query_results_drafts, currency, curr_cache=curr_cache)
            (number_late, sum_late) = self._count_results_and_sum_amounts(late_query_results, currency, curr_cache=curr_cache)
            read = self.env['account.move'].read_group([('journal_id', '=', self.id), ('to_check', '=', True)], ['amount_total'], 'journal_id', lazy=False)
            if read:
                number_to_check = read[0]['__count']
                to_check_balance = read[0]['amount_total']
        elif self.type == 'general':
            read = self.env['account.move'].read_group([('journal_id', '=', self.id), ('to_check', '=', True)], ['amount_total'], 'journal_id', lazy=False)
            if read:
                number_to_check = read[0]['__count']
                to_check_balance = read[0]['amount_total']

        is_sample_data = self.kanban_dashboard_graph and any(data.get('is_sample_data', False) for data in json.loads(self.kanban_dashboard_graph))

        return {
            'number_to_check': number_to_check,
            'to_check_balance': formatLang(self.env, to_check_balance, currency_obj=currency),
            'number_to_reconcile': number_to_reconcile,
            'account_balance': formatLang(self.env, currency.round(bank_account_balance), currency_obj=currency),
            'has_at_least_one_statement': has_at_least_one_statement,
            'nb_lines_bank_account_balance': nb_lines_bank_account_balance,
            'outstanding_pay_account_balance': formatLang(self.env, currency.round(outstanding_pay_account_balance), currency_obj=currency),
            'nb_lines_outstanding_pay_account_balance': nb_lines_outstanding_pay_account_balance,
            'last_balance': formatLang(self.env, currency.round(last_balance) + 0.0, currency_obj=currency),
            'number_draft': number_draft,
            'number_waiting': number_waiting,
            'number_late': number_late,
            'sum_draft': formatLang(self.env, currency.round(sum_draft) + 0.0, currency_obj=currency),
            'sum_waiting': formatLang(self.env, currency.round(sum_waiting) + 0.0, currency_obj=currency),
            'sum_late': formatLang(self.env, currency.round(sum_late) + 0.0, currency_obj=currency),
            'currency_id': currency.id,
            'bank_statements_source': self.bank_statements_source,
            'title': title,
            'is_sample_data': is_sample_data,
            'company_count': len(self.env.companies),
            'total_account_balance': formatLang(self.env, currency.round(bank_account_balance + outstanding_pay_account_balance), currency_obj=currency),
        }


    def get_bar_graph_datas(self):
        data = []
        today = fields.Date.today()
        data.append({'label': _('Due'), 'value':0.0, 'type': 'past'})
        day_of_week = int(format_datetime(today, 'e', locale=get_lang(self.env).code))
        first_day_of_week = today + timedelta(days=-day_of_week+1)
        for i in range(-1,4):
            if i==0:
                label = _('This Week')
            elif i==3:
                label = _('Not Due')
            else:
                start_week = first_day_of_week + timedelta(days=i*7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' + str(end_week.day) + ' ' + format_date(end_week, 'MMM', locale=get_lang(self.env).code)
                else:
                    label = format_date(start_week, 'd MMM', locale=get_lang(self.env).code) + '-' + format_date(end_week, 'd MMM', locale=get_lang(self.env).code)
            data.append({'label':label,'value':0.0, 'type': 'past' if i<0 else 'future'})

        # Build SQL query to find amount aggregated by week
        (select_sql_clause, query_args) = self._get_bar_graph_select_query()
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        weeks = []
        for i in range(0,6):
            if i == 0:
                query += "("+select_sql_clause+" and invoice_date_due < '"+start_date.strftime(DF)+"')"
                weeks.append((start_date.min, start_date))
            elif i == 5:
                query += " UNION ALL ("+select_sql_clause+" and invoice_date_due >= '"+start_date.strftime(DF)+"')"
                weeks.append((start_date, start_date.max))
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL ("+select_sql_clause+" and invoice_date_due >= '"+start_date.strftime(DF)+"' and invoice_date_due < '"+next_date.strftime(DF)+"')"
                weeks.append((start_date, next_date))
                start_date = next_date
        # Ensure results returned by postgres match the order of data list
        self.env.cr.execute(query, query_args)
        query_results = self.env.cr.dictfetchall()
        is_sample_data = True
        for index in range(0, len(query_results)):
            if query_results[index].get('aggr_date') != None:
                is_sample_data = False
                aggr_date = query_results[index]['aggr_date']
#                 week_index = next(i for i in range(0, len(weeks)) if weeks[i][0] <= aggr_date < weeks[i][1])
                week_index = next(i for i in range(0, len(weeks)))
                data[week_index]['value'] = query_results[index].get('total')

        [graph_title, graph_key] = self._graph_title_and_key()

        if is_sample_data:
            for index in range(0, len(query_results)):
                data[index]['type'] = 'o_sample_data'
                # we use unrealistic values for the sample data
                data[index]['value'] = random.randint(0, 20)
                graph_key = _('Sample data')

        return [{'values': data, 'title': graph_title, 'key': graph_key, 'is_sample_data': is_sample_data}]

class account_asset(models.Model):
    _inherit = "account.asset"
    
    employees_asset = fields.One2many('account.asset.employee', 'asset_id', string='العهدة')

class account_employee(models.Model):
    _name = "account.asset.employee"
    _description = 'الأصول والعهد'

    asset_id = fields.Many2one('account.asset', string='الأصل')
    employee_id = fields.Many2one('hr.employee', string='الموظف')
    recived = fields.Date(string='تاريخ استلام العهدة')
    back = fields.Date(string='تاريخ تسليم العهدة')
