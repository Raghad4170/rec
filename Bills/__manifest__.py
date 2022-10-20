# Copyright to The City Law Firm
{
    'name': "Bills Management",
    'summary': """Bills Management""",
    'description': """Bills Management""",
    'sequence': -111,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','portal','website','parentid','product','account','hr','account_asset'],
    'license': 'LGPL-3',
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/custody_report.xml',
        'views/portal.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
