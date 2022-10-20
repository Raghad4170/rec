# -*- coding: utf-8 -*-

from collections import OrderedDict
from operator import itemgetter
from odoo import http, _  
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import Website
import json 
import base64
from odoo.osv.expression import OR
import pytz 
import datetime
from datetime import datetime, timedelta, date
from datetime import date
 
 
     
class CustomerPortal(CustomerPortal):    
  
    # ------------------------------------------------------------
    # My Bills management 
    # ------------------------------------------------------------    
    @http.route(['/create_bills'], type='http', auth="user", website=True)
    def create_bills(self,**post):   
        return request.render("Bills.create_bills")

    @http.route(['/submit_bills'], type='http', auth="public", methods=['POST'], csrf=False,website=True)
    def submit_bills(self,**post):
        bills_obj=request.env['bills.management']  
        employee_id = request.env.user.employee_id.id
        company_id = request.env.user.company_id.id
        
        bills_dic = {}
        

        bills_dic['employee_id'] = int(employee_id)
        bills_dic['company_id'] = int(company_id)
        bills_dic['name'] = post['name']
        bills_dic['expense_amount'] = post['expense_amount']
        bills_dic['note'] = post['note']
        
            
        bills_id = bills_obj.create(bills_dic)
        
        if post['bank']:
            FileStorage = post['bank']
            FileData = FileStorage.read()
            file_base64_seven = base64.encodestring(FileData)
            bills_id.write({'bank':file_base64_seven})
        if post['file']:
            FileStorage = post['file']
            FileData = FileStorage.read()
            file_base64_seven = base64.encodestring(FileData)
            bills_id.write({'file':file_base64_seven})

        
        return request.render("Bills.thankyou_msg_bills")  
     
    
    # ------------------------------------------------------------
    # My custody management 
    # ------------------------------------------------------------    
    @http.route(['/create_custody'], type='http', auth="user", website=True)
    def create_custody(self,**post):   
        return request.render("Bills.create_custody")

    @http.route(['/submit_custody'], type='http', auth="public", methods=['POST'], csrf=False,website=True)
    def submit_custody(self,**post):
        custody_obj=request.env['custody.management']  
        employee_id = request.env.user.employee_id.id
        company_id = request.env.user.company_id.id
        
        custody_dic = {}
        if post['date_custody']:
            date_custody = datetime.strptime(post['date_custody'], '%Y-%m-%d')
            custody_dic['date_custody'] = date_custody

        custody_dic['employee_id'] = int(employee_id)
        custody_dic['company_id'] = int(company_id)
        custody_dic['name'] = post['name']
        custody_dic['job_position'] = post['job_position']
        custody_dic['iban'] = post['iban']
        custody_dic['custody'] = post['custody']
        custody_dic['custody_remaining'] = post['custody_remaining']
        
            
        custody_id = custody_obj.create(custody_dic)

        
        return request.render("Bills.thankyou_msg_custody")
    


    # ------------------------------------------------------------
    # My asset custody 
    # ------------------------------------------------------------ 
    @http.route(['/create_asset'], type='http', auth="user", website=True)
    def create_asset(self,**post):
        asset_obj = request.env['account.asset'] 
        asset_id = asset_obj.sudo().search([])
        return request.render("Bills.create_asset",{'asset_list':asset_id})

    @http.route(['/submit_asset'], type='http', auth="public", methods=['POST'], csrf=False,website=True)
    def submit_asset(self,**post):
        assets_custody_obj=request.env['asset.custody']  
        employee_id = request.env.user.employee_id.id
        company_id = request.env.user.company_id.id
        
        asset_dic = {}
        if post['recived']:
            recived = datetime.strptime(post['recived'], '%Y-%m-%d')
            asset_dic['recived'] = recived
        if post['back']:
            back = datetime.strptime(post['back'], '%Y-%m-%d')
            asset_dic['back'] = back

        asset_dic['employee_id'] = int(employee_id)
        asset_dic['company_id'] = int(company_id)
        asset_dic['name'] = post['name']
        asset_dic['job_position'] = post['job_position']
        asset_dic['asset_id'] = int(post['asset_list'])
        asset_dic['back_state'] = post['back_state']
            
        asset_custody_id = assets_custody_obj.create(asset_dic)

        
        return request.render("Bills.thankyou_msg_asset")
       
    # ------------------------------------------------------------
    # My buying order 
    # ------------------------------------------------------------ 
    @http.route(['/create_buying'], type='http', auth="user", website=True)
    def create_buying(self,**post):
        partner_obj = request.env['res.partner'] 
        partner_id = partner_obj.sudo().search([])
        return request.render("Bills.create_buying",{'partner_list':partner_id})

    @http.route(['/submit_buying'], type='http', auth="public", methods=['POST'], csrf=False,website=True)
    def submit_buying(self,**post):
        buying_obj=request.env['buying.order']  
        employee_id = request.env.user.employee_id.id
        company_id = request.env.user.company_id.id
        
        buying_dic = {}

        buying_dic['employee_id'] = int(employee_id)
        buying_dic['company_id'] = int(company_id)
        buying_dic['name'] = post['name']
        buying_dic['partner_id'] = int(post['partner_list'])
        buying_dic['product'] = post['product']
        buying_dic['amount'] = post['amount']
        buying_dic['expense_amount'] = post['expense_amount']
        buying_dic['reason'] = post['reason']
        buying_dic['note'] = post['note']
        buying_dic['terms'] = post['terms']
            
        buying_id = buying_obj.create(buying_dic)

        
        return request.render("Bills.thankyou_msg_buying")
       
     
    