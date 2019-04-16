{
    'name': "cPurchase",
    'summary': """
        cPurchase""",
    'author': "SimpleIT",
    'website': "http://simpleit.com",
    'category': 'account_invoicing',
    'version': '11.0.1',
    'depends': ['hr', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/model_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
