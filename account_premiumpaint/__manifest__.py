{
    'name': "Account custom Premium Paint",

    'summary': """
        Account custom Premium Paint""",

    'author': "SimpleIT",
    'website': "http://simpleit.com",

    'category': 'account_invoicing',
    'version': '11.0.1',

    'depends': [
        'account',
        'sale_premiumpaint',
    ],

    'data': [
        'views/account_invoice_view.xml',
        'views/report_invoice_daily.xml',
        'wizard/invoice_daily_report.xml',
        'wizard/invoice_user_report.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
