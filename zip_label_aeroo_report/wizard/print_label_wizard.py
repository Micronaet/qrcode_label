# -*- coding: utf-8 -*-
###############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class ZipLabelPrintReportWizard(orm.TransientModel):
    ''' Print report wizard
    '''    
    _name = 'zip.label.print.report.wizard'
    
    # --------------
    # Button events:
    # --------------
    def print_report(self, cr, uid, ids, context=None):
        ''' Print report wizard
        ''' 
        # Initial setup:
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        label_pool = self.pool.get('zip.label')            
        report_name = 'zip_label_report'
        
        # Create domain:
        total = len(wiz_proxy.start_code_ids)
        if total > 1:
            domain = ['|' for item in range(
                0, len(wiz_proxy.start_code_ids) - 1)]
        else:    
            domain = []
            
        for start in wiz_proxy.start_code_ids:
            domain.append(('code', '=ilike', '%s%%' % start.name))
        _logger.info('Domain search for report: %s' % domain)
        
        # Search lable:    
        object_ids = label_pool.search(cr, uid, domain, context=context)        
        if not object_ids:
            raise osv.except_osv(
                _('Print report'), 
                _('No label selected change filter'),
                )

        datas = {
            'from_wizard': True,            
            'object_ids': object_ids,
            }
        
        # Open report:
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            }

    _columns = {
        'start_code': fields.char('Start code', size=64),
        }

class ZipLabelPrintReportLineWizard(orm.TransientModel):
    ''' Wizard for line
    '''
    _name = 'zip.label.print.report.line.wizard'
    
    _columns = {
        'name': fields.char('Start code', size=64),
        'wizard_id': fields.many2one(
            'zip.label.print.report.wizard', 'Wizard'),        
        }
        
class ZipLabelPrintReportWizard(orm.TransientModel):
    ''' Add relations
    '''
    _inherit = 'zip.label.print.report.wizard'
    
    _columns = {
        'start_code_ids': fields.one2many(
            'zip.label.print.report.line.wizard', 'wizard_id', 'Start code'),
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
