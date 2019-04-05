# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ReportInvoiceDaily(models.AbstractModel):

    _name = 'report.account_premiumpaint.report_invoicedaily'

    @api.multi
    def get_report_consolidate(self, date_at=False):

        if not date_at:
            date_at = fields.Date.context_today(self)
        domain = [('date_invoice','>=', date_at[:8] + "01"),('date_invoice','<=', date_at),('type','=', 'out_invoice'),('state','in',('open','paid'))]
        invoice_data = self.env['account.invoice'].read_group(domain,fields=['warehouse_id','amount_calculate_cost','amount_untaxed'], groupby=['warehouse_id'])
        for sd in invoice_data:
            sd['Contado'] = sd['Credito'] =0.0
            if '__domain' in sd:
                sale_payment_type = self.env['account.invoice'].read_group(sd['__domain'],fields=['payment_type','amount_untaxed'], groupby=['payment_type'])
                for spt in sale_payment_type:
                    sd[spt['payment_type']] = spt['amount_untaxed']
            sale_team = self.env['crm.team'].search([('warehouse_id','=',sd['warehouse_id'][0])], limit=1)
            sd['invoiced_target'] = sale_team.invoiced_target if sale_team else 0.0
        return invoice_data

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        wiz_date = data.get('form', {}).get('date',False)
        
        if not wiz_date:
            wiz_date = fields.Date.context_today(self)
        domain = [('date_invoice','>=', wiz_date),('date_invoice','<=', wiz_date),('type','=', 'out_invoice'),('state','in',('open','paid'))]
        docs = self.env['account.invoice'].browse(docids)
        invoice_data = self.env['account.invoice'].read_group(domain,fields=['warehouse_id','amount_calculate_cost','amount_untaxed'], groupby=['warehouse_id'])
        for sd in invoice_data:
            sd['Contado'] = sd['Credito'] =0.0
            if '__domain' in sd:
                sale_payment_type = self.env['account.invoice'].read_group(sd['__domain'],fields=['payment_type','amount_untaxed'], groupby=['payment_type'])
                for spt in sale_payment_type:
                    sd[spt['payment_type']] = spt['amount_untaxed']
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.invoice',
            'docs': docs,
            'data': invoice_data,
            'date_at': wiz_date,
            'get_report_consolidate': self.get_report_consolidate,
        }

class ReportInvoiceUser(models.AbstractModel):

    _name = 'report.account_premiumpaint.report_invoiceuser'

    @api.multi
    def get_report_user(self, data={}, payment_type='Contado', type='out_invoice'):
        start_date = data.get('start_date', False) or fields.Date.context_today(self)
        end_date = data.get('end_date', False) or fields.Date.context_today(self)
        user_id = data.get('user_id', False) and data.get('user_id', False)[0]
        domain = [('date_invoice','>=', start_date),('date_invoice','<=', end_date),('type','=', type),('payment_type','=', payment_type),('user_id','=', user_id),('state','in',('open','paid'))]
        return self.env['account.invoice'].search(domain)

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        return {
            'data': data.get('form', {}),
            'get_report_user': self.get_report_user
        }

class ReportInvoiceCash(models.AbstractModel):

    _name = 'report.account_premiumpaint.report_invoicecash'

    @api.multi
    def get_total(self, data={}, payment_type='Contado', type='out_invoice'):
        date = data.get('date', False) or fields.Date.context_today(self)
        user_id = data.get('user_id', False) and data.get('user_id', False)[0]
        domain = [('date_invoice','=', date),('type','=', type),('payment_type','=', payment_type),('create_uid','=', user_id),('state','in',('open','paid'))]
        return sum(self.env['account.invoice'].search(domain).mapped('amount_total'))

    
    @api.multi
    def get_payment(self, data={}):

        date = data.get('date', False) or fields.Date.context_today(self)
        user_id = data.get('user_id', False) and data.get('user_id', False)[0]
        domain = [('create_uid','=', user_id),('payment_date','=', date),('payment_type','=', 'inbound'),('state','in',('posted','reconciled'))]
        payment_data = self.env['account.payment'].read_group(domain,fields=['payment_subtype_id','amount'], groupby=['payment_subtype_id'])
        return payment_data

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        return {
            'data': data.get('form', {}),
            'get_total': self.get_total,
            'get_payment': self.get_payment
        }
