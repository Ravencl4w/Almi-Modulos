# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta
from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class TreasurySettlementAPI(http.Controller):
    """
    API REST para la app móvil de transportistas.
    Permite consultar rutas y enviar liquidaciones.
    """
    
    def _authenticate(self):
        """Verifica la autenticación del usuario"""
        if not request.env.user or request.env.user._is_public():
            return {
                'error': True,
                'message': _('Authentication required')
            }, 401
        return None, 200
    
    def _get_driver_for_user(self):
        """Obtiene el conductor asociado al usuario actual"""
        driver = request.env['dispatch.driver'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not driver:
            return None, {
                'error': True,
                'message': _('No driver associated with this user')
            }, 404
        
        return driver, None, 200
    
    @http.route('/api/settlement/my_routes', type='json', auth='user', methods=['GET', 'POST'], csrf=False)
    def get_my_routes(self, **kwargs):
        """
        Retorna las rutas asignadas al transportista autenticado.
        Incluye planillas y facturas pendientes.
        """
        try:
            # Verificar autenticación
            auth_error, status = self._authenticate()
            if auth_error:
                return auth_error
            
            # Obtener conductor
            driver, error, status = self._get_driver_for_user()
            if error:
                return error
            
            # Buscar rutas del conductor (últimos 30 días)
            date_limit = fields.Date.today() - timedelta(days=30)
            routes = request.env['dispatch.route'].sudo().search([
                ('driver_id', '=', driver.id),
                ('route_date', '>=', date_limit),
            ], order='route_date desc')
            
            result = []
            for route in routes:
                route_data = {
                    'id': route.id,
                    'name': route.name,
                    'date': str(route.route_date),
                    'state': route.state,
                    'vehicle': {
                        'id': route.vehicle_id.id,
                        'license_plate': route.vehicle_id.license_plate,
                    } if route.vehicle_id else None,
                    'has_settlement_sheet': bool(route.settlement_sheet_id),
                    'settlement_sheet': None,
                }
                
                # Agregar información de planilla si existe
                if route.settlement_sheet_id:
                    sheet = route.settlement_sheet_id
                    route_data['settlement_sheet'] = {
                        'id': sheet.id,
                        'name': sheet.name,
                        'state': sheet.state,
                        'total_invoices': sheet.total_invoices,
                        'total_amount': float(sheet.total_amount),
                        'total_collected': float(sheet.total_collected),
                        'pending_count': sheet.pending_count,
                        'delivered_count': sheet.delivered_count,
                    }
                
                result.append(route_data)
            
            return {
                'success': True,
                'data': result,
                'total': len(result)
            }
            
        except Exception as e:
            _logger.error('Error in get_my_routes: %s', str(e))
            return {
                'error': True,
                'message': str(e)
            }
    
    @http.route('/api/settlement/route/<int:route_id>', type='json', auth='user', methods=['GET', 'POST'], csrf=False)
    def get_route_detail(self, route_id, **kwargs):
        """
        Retorna el detalle de una ruta con planilla y facturas.
        Lista de clientes y montos a cobrar.
        """
        try:
            # Verificar autenticación
            auth_error, status = self._authenticate()
            if auth_error:
                return auth_error
            
            # Obtener conductor
            driver, error, status = self._get_driver_for_user()
            if error:
                return error
            
            # Buscar ruta
            route = request.env['dispatch.route'].sudo().browse(route_id)
            
            if not route.exists():
                return {
                    'error': True,
                    'message': _('Route not found')
                }
            
            # Verificar que la ruta pertenezca al conductor
            if route.driver_id.id != driver.id:
                return {
                    'error': True,
                    'message': _('This route does not belong to you')
                }
            
            # Preparar respuesta
            result = {
                'id': route.id,
                'name': route.name,
                'date': str(route.route_date),
                'state': route.state,
                'start_datetime': str(route.start_datetime) if route.start_datetime else None,
                'end_datetime': str(route.end_datetime) if route.end_datetime else None,
                'vehicle': {
                    'id': route.vehicle_id.id,
                    'license_plate': route.vehicle_id.license_plate,
                    'brand': route.vehicle_id.brand,
                } if route.vehicle_id else None,
                'settlement_sheet': None,
                'invoices': []
            }
            
            # Agregar información de planilla y facturas
            if route.settlement_sheet_id:
                sheet = route.settlement_sheet_id
                result['settlement_sheet'] = {
                    'id': sheet.id,
                    'name': sheet.name,
                    'state': sheet.state,
                    'total_amount': float(sheet.total_amount),
                    'currency': sheet.currency_id.name,
                }
                
                # Agregar facturas de la planilla
                for line in sheet.line_ids:
                    invoice_data = {
                        'line_id': line.id,
                        'invoice_id': line.invoice_id.id,
                        'invoice_name': line.invoice_name,
                        'invoice_date': str(line.invoice_date),
                        'customer': {
                            'id': line.partner_id.id,
                            'name': line.partner_id.name,
                            'street': line.partner_street or '',
                            'city': line.partner_city or '',
                            'phone': line.partner_phone or '',
                        },
                        'amount_total': float(line.amount_total),
                        'amount_collected': float(line.amount_collected),
                        'delivery_status': line.delivery_status,
                        'collection_status': line.collection_status,
                        'payment_method': line.payment_method or '',
                        'sequence': line.sequence,
                    }
                    result['invoices'].append(invoice_data)
                
                # Ordenar por secuencia
                result['invoices'] = sorted(result['invoices'], key=lambda x: x['sequence'])
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            _logger.error('Error in get_route_detail: %s', str(e))
            return {
                'error': True,
                'message': str(e)
            }
    
    @http.route('/api/settlement/submit', type='json', auth='user', methods=['POST'], csrf=False)
    def submit_settlement(self, **kwargs):
        """
        Crea liquidación y envía a revisión.
        
        Parámetros esperados:
        - route_id: ID de la ruta
        - sheet_id: ID de la planilla
        - driver_notes: Notas del transportista (opcional)
        - collections: Lista de cobros por factura
          [
            {
              "invoice_id": int,
              "amount_collected": float,
              "payment_method": str,
              "delivery_status": str,
              "notes": str (opcional),
              "evidence_base64": str (opcional),
              "latitude": float (opcional),
              "longitude": float (opcional)
            }
          ]
        """
        try:
            # Verificar autenticación
            auth_error, status = self._authenticate()
            if auth_error:
                return auth_error
            
            # Obtener conductor
            driver, error, status = self._get_driver_for_user()
            if error:
                return error
            
            # Obtener parámetros
            route_id = kwargs.get('route_id')
            sheet_id = kwargs.get('sheet_id')
            collections = kwargs.get('collections', [])
            driver_notes = kwargs.get('driver_notes', '')
            
            if not route_id or not sheet_id:
                return {
                    'error': True,
                    'message': _('route_id and sheet_id are required')
                }
            
            if not collections:
                return {
                    'error': True,
                    'message': _('At least one collection is required')
                }
            
            # Verificar que la ruta pertenezca al conductor
            route = request.env['dispatch.route'].sudo().browse(route_id)
            if not route.exists() or route.driver_id.id != driver.id:
                return {
                    'error': True,
                    'message': _('Invalid route')
                }
            
            # Verificar planilla
            sheet = request.env['treasury.settlement.sheet'].sudo().browse(sheet_id)
            if not sheet.exists() or sheet.route_id.id != route_id:
                return {
                    'error': True,
                    'message': _('Invalid settlement sheet')
                }
            
            # Crear liquidación
            settlement_vals = {
                'sheet_id': sheet_id,
                'date': fields.Date.today(),
                'driver_notes': driver_notes,
            }
            settlement = request.env['treasury.settlement'].sudo().create(settlement_vals)
            
            # Crear líneas de liquidación
            for collection in collections:
                invoice_id = collection.get('invoice_id')
                
                if not invoice_id:
                    continue
                
                # Buscar línea de planilla
                sheet_line = sheet.line_ids.filtered(lambda l: l.invoice_id.id == invoice_id)
                
                if not sheet_line:
                    _logger.warning(f'Invoice {invoice_id} not found in sheet {sheet_id}')
                    continue
                
                line_vals = {
                    'settlement_id': settlement.id,
                    'sheet_line_id': sheet_line.id,
                    'invoice_id': invoice_id,
                    'amount_invoice': collection.get('amount_invoice', sheet_line.amount_total),
                    'amount_collected': collection.get('amount_collected', 0.0),
                    'payment_method': collection.get('payment_method', 'none'),
                    'delivery_status': collection.get('delivery_status', 'not_delivered'),
                    'delivery_notes': collection.get('notes', ''),
                    'delivery_datetime': fields.Datetime.now(),
                }
                
                # Agregar geolocalización si está disponible
                if collection.get('latitude') and collection.get('longitude'):
                    line_vals['latitude'] = collection.get('latitude')
                    line_vals['longitude'] = collection.get('longitude')
                
                # Agregar evidencia si está disponible
                if collection.get('evidence_base64'):
                    line_vals['collection_evidence'] = collection.get('evidence_base64')
                    line_vals['collection_evidence_filename'] = f'evidence_{invoice_id}.jpg'
                
                request.env['treasury.settlement.line'].sudo().create(line_vals)
            
            # Enviar para revisión
            settlement.sudo().action_submit_for_review()
            
            return {
                'success': True,
                'message': _('Settlement submitted successfully'),
                'data': {
                    'settlement_id': settlement.id,
                    'settlement_name': settlement.name,
                    'state': settlement.state,
                    'total_collected': float(settlement.total_collected),
                    'total_to_collect': float(settlement.total_to_collect),
                }
            }
            
        except ValidationError as e:
            _logger.error('Validation error in submit_settlement: %s', str(e))
            return {
                'error': True,
                'message': str(e)
            }
        except Exception as e:
            _logger.error('Error in submit_settlement: %s', str(e))
            return {
                'error': True,
                'message': str(e)
            }
    
    @http.route('/api/settlement/status/<int:settlement_id>', type='json', auth='user', methods=['GET', 'POST'], csrf=False)
    def get_settlement_status(self, settlement_id, **kwargs):
        """
        Consulta el estado de una liquidación.
        Muestra si fue aprobada/rechazada.
        """
        try:
            # Verificar autenticación
            auth_error, status = self._authenticate()
            if auth_error:
                return auth_error
            
            # Obtener conductor
            driver, error, status = self._get_driver_for_user()
            if error:
                return error
            
            # Buscar liquidación
            settlement = request.env['treasury.settlement'].sudo().browse(settlement_id)
            
            if not settlement.exists():
                return {
                    'error': True,
                    'message': _('Settlement not found')
                }
            
            # Verificar que pertenezca al conductor
            if settlement.driver_id.id != driver.id:
                return {
                    'error': True,
                    'message': _('This settlement does not belong to you')
                }
            
            result = {
                'id': settlement.id,
                'name': settlement.name,
                'state': settlement.state,
                'date': str(settlement.date),
                'total_to_collect': float(settlement.total_to_collect),
                'total_collected': float(settlement.total_collected),
                'difference': float(settlement.difference),
                'collection_rate': float(settlement.collection_rate),
                'submission_date': str(settlement.submission_date) if settlement.submission_date else None,
                'approval_date': str(settlement.approval_date) if settlement.approval_date else None,
                'rejection_reason': settlement.rejection_reason or '',
                'liquidator': settlement.liquidator_user_id.name if settlement.liquidator_user_id else '',
            }
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            _logger.error('Error in get_settlement_status: %s', str(e))
            return {
                'error': True,
                'message': str(e)
            }

