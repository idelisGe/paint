# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from base64 import b64decode, b64encode
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"
    @api.multi
    def assert_balanced(self):
        return True

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    fiscal_printer_status = fields.Selection([
            ('unsent','Sin enviar'),
            ('sent','Enviada'),
            ('printed','Impresa'),
        ], 'Impresora Fiscal', readonly=True, default=lambda *a: 'unsent')

    @api.multi
    def send_invoice_proxy(self):
        self.ensure_one()
        cmd = "jR%s"%(self.partner_id.vat,)
        cmd += "\njS%s"%(self.partner_id.name,)
        cmd += "\nj%s"%(self.partner_id.street,) if self.partner_id.street else ''
        for line in self.invoice_line_ids:
            if line.invoice_line_tax_ids:
                tmp = '\n!{:011.2f}{:09.3f}{}'.format(line.price_unit, line.quantity, line.name.replace('\n','')[:117])
                cmd += tmp.replace('.','')
            else:
                tmp = '\n {:011.2f}{:09.3f}{}'.format(line.price_unit, line.quantity, line.name.replace('\n','')[:117])
                cmd += tmp.replace('.','')
        cmd += "\n3\n101"
        cmd = b64encode(cmd.encode('utf-8'))
        self.fiscal_printer_status = 'sent'
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': 'http://127.0.0.1:8080/sendcmd/%s'%(cmd.decode("utf-8"),),
        }
