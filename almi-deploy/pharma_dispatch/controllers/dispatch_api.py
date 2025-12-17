# -*- coding: utf-8 -*-

import json
import logging
from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import ValidationError, UserError, AccessError

_logger = logging.getLogger(__name__)


class DispatchAPI(http.Controller):
    """
    API REST para la aplicación móvil de transportistas.
    Permite a los conductores ver sus rutas, marcar entregas y registrar pagos.
    """
    
    def _authenticate_driver(self, token=None, driver_id=None):
        """
        Autentica al conductor usando token o ID.
        Por simplicidad, validamos que el driver_id exista.
        En producción, se debería implementar un sistema de tokens más robusto.
        """
        if not driver_id:
            return None, {'error': 'driver_id es requerido', 'code': 'MISSING_DRIVER_ID'}
        
        driver = request.env['dispatch.driver'].sudo().search([('id', '=', driver_id)], limit=1)
        if not driver:
            return None, {'error': 'Conductor no encontrado', 'code': 'DRIVER_NOT_FOUND'}
        
        return driver, None
    
    def _response(self, data=None, error=None, status=200):
        """Genera una respuesta JSON consistente"""
        response_data = {}
        
        if error:
            response_data['success'] = False
            response_data['error'] = error
        else:
            response_data['success'] = True
            response_data['data'] = data or {}
        
        return Response(
            json.dumps(response_data, ensure_ascii=False, default=str),
            content_type='application/json',
            status=status
        )
    
    @http.route('/api/dispatch/route/<int:route_id>', type='http', auth='public', 
                methods=['GET'], csrf=False, cors='*')
    def get_route(self, route_id, driver_id=None, **kwargs):
        """
        Obtiene los detalles de una ruta específica.
        
        Parámetros:
            - route_id: ID de la ruta
            - driver_id: ID del conductor (para autenticación)
        
        Retorna:
            Detalles de la ruta con sus líneas de entrega
        """
        try:
            # Autenticar conductor
            driver, auth_error = self._authenticate_driver(driver_id=driver_id)
            if auth_error:
                return self._response(error=auth_error, status=401)
            
            # Buscar la ruta
            route = request.env['dispatch.route'].sudo().search([
                ('id', '=', route_id),
                ('driver_id', '=', driver.id)
            ], limit=1)
            
            if not route:
                return self._response(
                    error={'error': 'Ruta no encontrada o no pertenece al conductor', 
                           'code': 'ROUTE_NOT_FOUND'},
                    status=404
                )
            
            # Preparar datos de la ruta
            route_data = {
                'id': route.id,
                'name': route.name,
                'route_date': route.route_date.isoformat() if route.route_date else None,
                'state': route.state,
                'state_name': dict(route._fields['state'].selection).get(route.state),
                'driver': {
                    'id': route.driver_id.id,
                    'name': route.driver_id.name,
                    'license_number': route.driver_id.license_number,
                },
                'vehicle': {
                    'id': route.vehicle_id.id,
                    'license_plate': route.vehicle_id.license_plate,
                    'brand': route.vehicle_id.brand or '',
                    'model': route.vehicle_id.model or '',
                },
                'totals': {
                    'total_orders': route.total_orders,
                    'pending_orders': route.pending_orders,
                    'delivered_orders': route.delivered_orders,
                    'failed_orders': route.failed_orders,
                },
                'lines': []
            }
            
            # Agregar líneas de ruta
            for line in route.line_ids:
                line_data = {
                    'id': line.id,
                    'sequence': line.sequence,
                    'state': line.state,
                    'state_name': dict(line._fields['state'].selection).get(line.state),
                    'order': {
                        'id': line.order_id.id,
                        'name': line.order_id.name,
                        'amount_total': float(line.order_amount_total),
                    },
                    'partner': {
                        'id': line.partner_id.id,
                        'name': line.partner_name,
                        'address': line.partner_address,
                        'phone': line.partner_phone,
                    },
                    'delivery_datetime': line.delivery_datetime.isoformat() if line.delivery_datetime else None,
                    'notes': line.notes,
                }
                route_data['lines'].append(line_data)
            
            # Agregar líneas de cobranza (facturas disponibles para cobro)
            sheet = route.sheet_id
            if sheet:
                settlement = request.env['dispatch.settlement'].sudo().search([
                    ('sheet_id', '=', sheet.id)
                ], limit=1)
                
                if settlement and settlement.collection_sheet_id:
                    collection_lines = []
                    for col_line in settlement.collection_sheet_id.collection_line_ids:
                        collection_lines.append({
                            'id': col_line.id,
                            'invoice_id': col_line.invoice_id.id,
                            'invoice_name': col_line.invoice_id.name,
                            'partner_name': col_line.partner_id.name if col_line.partner_id else '',
                            'invoice_amount_total': float(col_line.invoice_amount_total),  # Monto de la factura
                            'amount': float(col_line.amount),  # Monto cobrado
                            'collection_type': col_line.collection_type,
                            'payment_method': col_line.payment_method,
                            'state': col_line.state,
                        })
                    route_data['collection_lines'] = collection_lines
            
            return self._response(data=route_data)
        
        except Exception as e:
            _logger.error(f"Error en get_route: {str(e)}", exc_info=True)
            return self._response(
                error={'error': 'Error interno del servidor', 'code': 'INTERNAL_ERROR', 
                       'details': str(e)},
                status=500
            )
    
    @http.route('/api/dispatch/route/line/<int:line_id>/deliver', type='json', 
                auth='public', methods=['POST'], csrf=False, cors='*')
    def mark_delivered(self, line_id, driver_id=None, signature=None, 
                      receiver_name=None, notes=None, **kwargs):
        """
        Marca una línea de ruta como entregada.
        
        Parámetros:
            - line_id: ID de la línea de ruta
            - driver_id: ID del conductor
            - signature: Firma del cliente (base64, opcional)
            - receiver_name: Nombre de quien recibió
            - notes: Notas adicionales
        """
        try:
            # Autenticar conductor
            driver, auth_error = self._authenticate_driver(driver_id=driver_id)
            if auth_error:
                return auth_error
            
            # Buscar la línea de ruta
            line = request.env['dispatch.route.line'].sudo().search([
                ('id', '=', line_id),
                ('route_id.driver_id', '=', driver.id)
            ], limit=1)
            
            if not line:
                return {
                    'success': False,
                    'error': 'Línea de ruta no encontrada o no pertenece al conductor'
                }
            
            # Actualizar datos opcionales
            vals = {}
            if signature:
                vals['signature'] = signature
            if receiver_name:
                vals['receiver_name'] = receiver_name
            if notes:
                vals['notes'] = notes
            
            if vals:
                line.write(vals)
            
            # Marcar como entregado
            line.action_mark_delivered()
            
            return {
                'success': True,
                'data': {
                    'line_id': line.id,
                    'state': line.state,
                    'message': 'Entrega marcada exitosamente'
                }
            }
        
        except (ValidationError, UserError) as e:
            _logger.warning(f"Error de validación en mark_delivered: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            _logger.error(f"Error en mark_delivered: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }
    
    @http.route('/api/dispatch/route/line/<int:line_id>/fail', type='json', 
                auth='public', methods=['POST'], csrf=False, cors='*')
    def mark_failed(self, line_id, driver_id=None, failure_reason=None, 
                   notes=None, **kwargs):
        """
        Marca una línea de ruta como no entregada (fallida).
        
        Parámetros:
            - line_id: ID de la línea de ruta
            - driver_id: ID del conductor
            - failure_reason: Motivo del fallo
            - notes: Notas adicionales
        """
        try:
            # Autenticar conductor
            driver, auth_error = self._authenticate_driver(driver_id=driver_id)
            if auth_error:
                return auth_error
            
            # Buscar la línea de ruta
            line = request.env['dispatch.route.line'].sudo().search([
                ('id', '=', line_id),
                ('route_id.driver_id', '=', driver.id)
            ], limit=1)
            
            if not line:
                return {
                    'success': False,
                    'error': 'Línea de ruta no encontrada o no pertenece al conductor'
                }
            
            # Actualizar motivo y notas
            vals = {}
            if failure_reason:
                vals['failure_reason'] = failure_reason
            if notes:
                vals['notes'] = notes
            
            if vals:
                line.write(vals)
            
            # Marcar como fallido
            line.action_mark_failed()
            
            return {
                'success': True,
                'data': {
                    'line_id': line.id,
                    'state': line.state,
                    'message': 'Entrega marcada como fallida'
                }
            }
        
        except (ValidationError, UserError) as e:
            _logger.warning(f"Error de validación en mark_failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            _logger.error(f"Error en mark_failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }
    
    @http.route('/api/dispatch/collection/register', type='json', auth='public', 
                methods=['POST'], csrf=False, cors='*')
    def register_payment(self, driver_id=None, route_id=None, invoice_id=None,
                        amount=None, collection_type=None, payment_method=None,
                        bank_reference=None, notes=None, **kwargs):
        """
        Registra o actualiza un pago recibido por el conductor.
        Si ya existe una línea de cobranza para la factura, actualiza su monto.
        Si no existe, crea una nueva línea.
        
        Parámetros:
            - driver_id: ID del conductor
            - route_id: ID de la ruta
            - invoice_id: ID de la factura (requerido)
            - amount: Monto recibido
            - collection_type: Tipo de cobranza (cash, credit, deposit)
            - payment_method: Método de pago (cash, transfer, deposit, check, card)
            - bank_reference: Referencia bancaria (opcional)
            - notes: Notas adicionales
        """
        try:
            # Autenticar conductor
            driver, auth_error = self._authenticate_driver(driver_id=driver_id)
            if auth_error:
                return auth_error
            
            # Validar parámetros requeridos
            if not route_id:
                return {
                    'success': False,
                    'error': 'route_id es requerido'
                }
            
            if not invoice_id:
                return {
                    'success': False,
                    'error': 'invoice_id es requerido'
                }
            
            # Permitir monto 0 o mayor
            if amount is None or float(amount) < 0:
                return {
                    'success': False,
                    'error': 'amount debe ser mayor o igual a cero'
                }
            
            if not collection_type:
                collection_type = 'cash'
            
            if not payment_method:
                payment_method = 'cash'
            
            # Buscar la ruta y validar que pertenezca al conductor
            route = request.env['dispatch.route'].sudo().search([
                ('id', '=', route_id),
                ('driver_id', '=', driver.id)
            ], limit=1)
            
            if not route:
                return {
                    'success': False,
                    'error': 'Ruta no encontrada o no pertenece al conductor'
                }
            
            # Obtener la planilla y liquidación
            sheet = route.sheet_id
            if not sheet:
                return {
                    'success': False,
                    'error': 'La ruta no tiene una planilla asociada'
                }
            
            settlement = request.env['dispatch.settlement'].sudo().search([
                ('sheet_id', '=', sheet.id)
            ], limit=1)
            
            if not settlement or not settlement.collection_sheet_id:
                return {
                    'success': False,
                    'error': 'No se encontró la hoja de cobranzas para esta ruta'
                }
            
            # Verificar que la factura esté en la liquidación
            invoice = request.env['account.move'].sudo().search([
                ('id', '=', invoice_id),
                ('id', 'in', settlement.invoice_ids.ids)
            ], limit=1)
            
            if not invoice:
                return {
                    'success': False,
                    'error': 'Factura no encontrada en esta liquidación'
                }
            
            # Buscar si ya existe una línea de cobranza para esta factura
            existing_line = request.env['dispatch.collection.line'].sudo().search([
                ('collection_sheet_id', '=', settlement.collection_sheet_id.id),
                ('invoice_id', '=', invoice.id),
                ('state', '=', 'pending')
            ], limit=1)
            
            if existing_line:
                # Actualizar la línea existente
                update_vals = {
                    'amount': float(amount),
                    'collection_type': collection_type,
                    'payment_method': payment_method,
                }
                
                if notes:
                    update_vals['notes'] = notes
                if bank_reference:
                    update_vals['bank_reference'] = bank_reference
                
                existing_line.write(update_vals)
                collection_line = existing_line
                message = 'Pago actualizado exitosamente'
            else:
                # Crear nueva línea de cobranza
                line_vals = {
                    'collection_sheet_id': settlement.collection_sheet_id.id,
                    'invoice_id': invoice.id,
                    'amount': float(amount),
                    'collection_type': collection_type,
                    'payment_method': payment_method,
                    'registered_by': driver.id,
                    'notes': notes,
                }
                
                if bank_reference:
                    line_vals['bank_reference'] = bank_reference
                
                collection_line = request.env['dispatch.collection.line'].sudo().create(line_vals)
                message = 'Pago registrado exitosamente'
            
            return {
                'success': True,
                'data': {
                    'collection_line_id': collection_line.id,
                    'invoice_id': collection_line.invoice_id.id,
                    'invoice_name': collection_line.invoice_id.name,
                    'amount': float(collection_line.amount),
                    'state': collection_line.state,
                    'message': message
                }
            }
        
        except (ValidationError, UserError) as e:
            _logger.warning(f"Error de validación en register_payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            _logger.error(f"Error en register_payment: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }
    
    @http.route('/api/dispatch/driver/<int:driver_id>/routes', type='http', 
                auth='public', methods=['GET'], csrf=False, cors='*')
    def get_driver_routes(self, driver_id, date=None, state=None, **kwargs):
        """
        Obtiene las rutas de un conductor.
        
        Parámetros:
            - driver_id: ID del conductor
            - date: Fecha específica (YYYY-MM-DD, opcional)
            - state: Estado de las rutas (opcional)
        """
        try:
            # Autenticar conductor
            driver, auth_error = self._authenticate_driver(driver_id=driver_id)
            if auth_error:
                return self._response(error=auth_error, status=401)
            
            # Construir dominio de búsqueda
            domain = [('driver_id', '=', driver.id)]
            
            if date:
                domain.append(('route_date', '=', date))
            
            if state:
                domain.append(('state', '=', state))
            
            # Buscar rutas
            routes = request.env['dispatch.route'].sudo().search(domain, order='route_date desc')
            
            # Preparar datos
            routes_data = []
            for route in routes:
                routes_data.append({
                    'id': route.id,
                    'name': route.name,
                    'route_date': route.route_date.isoformat() if route.route_date else None,
                    'state': route.state,
                    'state_name': dict(route._fields['state'].selection).get(route.state),
                    'totals': {
                        'total_orders': route.total_orders,
                        'pending_orders': route.pending_orders,
                        'delivered_orders': route.delivered_orders,
                        'failed_orders': route.failed_orders,
                    }
                })
            
            return self._response(data={'routes': routes_data, 'count': len(routes_data)})
        
        except Exception as e:
            _logger.error(f"Error en get_driver_routes: {str(e)}", exc_info=True)
            return self._response(
                error={'error': 'Error interno del servidor', 'code': 'INTERNAL_ERROR'},
                status=500
            )

