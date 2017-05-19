# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import os
import sys
import xlrd
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class ProductImportXLSWizard(orm.TransientModel):
    ''' Wizard for
    '''
    _name = 'product.import.xls.wizard'

    # --------------------
    # Wizard button event:
    # --------------------
    def action_import(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}                
        wizard_browse = self.browse(cr, uid, ids, context=context)[0]
        
        # Import procedure:
        label_pool = self.pool.get('zip.label')
        filename = '~/etl/smb/prodotti/etichette.xls'
        filename = os.path.expanduser(filename)

        _logger.info('Start import from path: %s' % filename)
        try:
            # from xlrd.sheet import ctype_text
            wb = xlrd.open_workbook(filename)
            ws = wb.sheet_by_index(0)
        except:
            raise osv.except_osv(
                _('Import file: %s' % filename),
                _('Error opening excel file'),
                )
        insert_code = []
        for line in range(1, ws.nrows):
            code = ws.cell(line, 0).value
            description_it = ws.cell(line, 1).value
            description_en = ws.cell(line, 2).value
            if not code:
                _logger.warning('Code not found, %s') % line

            label_ids = label_pool.search(cr,uid, [
                ('code', '=', code),
                ], context=context)
            data = {
                'code': code,
                'description_it': description_it,
                'description_en': description_en,
                }
            if label_ids:
                label_pool.write(cr, uid, label_ids, data, context=context)
                _logger.info('Update code: %s' % code)
            else:
                label_pool.create(cr, uid, data, context=context)
                _logger.info('Creata code: %s' % code)
            
            insert_code.append(code)
            
        if wizard_browse.mode == 'syncro':    
            remove_ids = label_pool.search(cr, uid, [
                ('code', 'not in', insert_code),
                ], context=context)        
            label_pool.unlink(cr, uid, remove_ids, context=context)
            _logger.info('Unlink element: %s' % len(remove_ids))
        return True

    _columns = {
        'mode': fields.selection([
            ('update', 'Update mode (create new and update present)'),
            ('syncro', 'Syncro mode (create, update and delete not present'),
            ], 'Mode', required=True)
        }
        
    _defaults = {
        'mode': lambda *x: 'syncro',
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


