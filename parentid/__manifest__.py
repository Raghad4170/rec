# -*- coding: utf-8 -*-
{
    'name': "parentid",

    'summary': """""",

    'description': """""",
    'sequence': -999999,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'contacts', 'sign', 'helpdesk', 'sale', 'account', 'web', 'website','account_asset','calendar','crm','mail','im_livechat','note','utm','project','hr','account_accountant'],

    # always loaded
    'data': [
        'security/security.xml',
        'view/template.xml',
        'view/sale_report.xml',
        'view/report_invoice.xml',
        'view/account.xml',
        'view/web_menu.xml',
        'view/views.xml',
        'view/asset_report.xml',
        'view/menu.xml',
        'view/replace.xml',
        'view/sale_sign.xml',
        'view/report_layout.xml',
        'view/expiration_date.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.report_assets_common': [
            'parentid/static/src/css/font.css',
        ],
        'web.assets_common': [
            'parentid/static/src/css/font.css',
        ],
        'web.assets_backend': [
            'parentid/static/src/css/font.css',
            'parentid/static/src/scss/font.scss',
            'parentid/static/src/css/change_color_backend.css',
            'parentid/static/src/js/sign_back_js_changes.js',
        ],
        'web.assets_frontend': [
            'parentid/static/src/css/font.css',
            'parentid/static/src/js/sign_front_js_changes.js',
        ],
        'web.assets_qweb': [
            'parentid/static/src/sign.xml',
        ],
    }

}
