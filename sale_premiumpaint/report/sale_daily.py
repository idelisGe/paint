# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ReportSaleDaily(models.AbstractModel):

    _name = 'report.sale_premiumpaint.report_saledaily'

    @api.multi
    def get_report_consolidate(self, date_at=False):

        if not date_at:
            date_at = fields.Date.context_today(self)
        domain = [('confirmation_date','>=', date_at[:8] + "01 00:00:00"),('confirmation_date','<=', date_at + " 23:59:59"),('state','in',('sale','done'))]
        sale_data = self.env['sale.order'].read_group(domain,fields=['warehouse_id','amount_calculate_cost','amount_total'], groupby=['warehouse_id'])
        for sd in sale_data:
            sd['Contado'] = sd['Credito'] =0.0
            if '__domain' in sd:
                sale_payment_type = self.env['sale.order'].read_group(sd['__domain'],fields=['payment_type','amount_total'], groupby=['payment_type'])
                for spt in sale_payment_type:
                    sd[spt['payment_type']] = spt['amount_total']
        return sale_data

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        wiz_date = data.get('form', {}).get('date',False)
        
        if not wiz_date:
            wiz_date = fields.Date.context_today(self)
        domain = [('confirmation_date','>=', wiz_date + " 00:00:00"),('confirmation_date','<=', wiz_date + " 23:59:59"),('state','in',('sale','done'))]
        docs = self.env['sale.order'].browse(docids)
        sale_data = self.env['sale.order'].read_group(domain,fields=['warehouse_id','amount_calculate_cost','amount_total'], groupby=['warehouse_id'])
        for sd in sale_data:
            sd['Contado'] = sd['Credito'] =0.0
            if '__domain' in sd:
                sale_payment_type = self.env['sale.order'].read_group(sd['__domain'],fields=['payment_type','amount_total'], groupby=['payment_type'])
                for spt in sale_payment_type:
                    sd[spt['payment_type']] = spt['amount_total']
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'data': sale_data,
            'date_at': wiz_date,
            'get_report_consolidate': self.get_report_consolidate,
        }
        return data
