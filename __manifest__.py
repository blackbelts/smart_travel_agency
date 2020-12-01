# -*- coding: utf-8 -*-
{
    'name': "smart_travel_agency",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Travel',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','helpdesk_inherit','arope_conf','report_xml'],


    # always loaded
    'data': [
        # 'security/ir.model.access.csv',

        'reports/travel_policy_report.xml',
        'data/send_mail.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/rating_table.xml',
        'views/travel_policy.xml',
        'views/benefits.xml',
        'views/excess.xml',
        'views/products.xml',
        'views/ticket.xml',
        'views/priceTable.xml',
        'views/companyAssist.xml',
        'views/menu_item.xml',
        'wizard/users.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'css': ['static/src/css/travel.css'],

}