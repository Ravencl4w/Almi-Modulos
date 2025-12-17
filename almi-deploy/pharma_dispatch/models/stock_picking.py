# -*- coding: utf-8 -*-

import logging
import json
import base64
import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    """
    Extensión del modelo stock.picking para agregar funcionalidad de
    Guías de Remisión Electrónica (GRE) con integración a SUNAT vía NubeFact
    y manejo de recojo en local.
    """
    _inherit = 'stock.picking'
    
    # ========== GUÍA DE REMISIÓN ELECTRÓNICA ==========
    is_electronic_guide = fields.Boolean(
        string='Es Guía Electrónica',
        default=False,
        help='Indica si es una guía de remisión electrónica para SUNAT'
    )
    
    gre_serie = fields.Char(
        string='Serie GRE',
        help='Serie de la guía electrónica (ej: T001)',
        copy=False
    )
    
    gre_number = fields.Char(
        string='Número GRE',
        help='Número correlativo de la guía electrónica',
        copy=False
    )
    
    # ========== MOTIVO DE TRASLADO (Catálogo 20 SUNAT) ==========
    transfer_reason = fields.Selection([
        ('01', '01 - Venta'),
        ('02', '02 - Compra'),
        ('04', '04 - Traslado entre establecimientos de la misma empresa'),
        ('08', '08 - Importación'),
        ('09', '09 - Exportación'),
        ('13', '13 - Otros'),
        ('14', '14 - Venta sujeta a confirmación del comprador'),
        ('18', '18 - Traslado emisor itinerante CP'),
        ('19', '19 - Traslado a zona primaria'),
    ], string='Motivo de Traslado',
       help='Motivo del traslado según catálogo 20 de SUNAT')
    
    transfer_reason_description = fields.Char(
        string='Descripción del Motivo',
        help='Descripción adicional del motivo de traslado'
    )
    
    # ========== DATOS DE ORIGEN Y DESTINO ==========
    origin_address = fields.Text(
        string='Dirección de Partida',
        help='Dirección completa del punto de partida'
    )
    
    origin_ubigeo = fields.Char(
        string='Ubigeo de Partida',
        help='Código de ubigeo del punto de partida (6 dígitos)'
    )
    
    destination_address = fields.Text(
        string='Dirección de Llegada',
        help='Dirección completa del punto de destino'
    )
    
    destination_ubigeo = fields.Char(
        string='Ubigeo de Llegada',
        help='Código de ubigeo del punto de destino (6 dígitos)'
    )
    
    # ========== DATOS DE TRANSPORTE ==========
    transport_mode = fields.Selection([
        ('private', 'Transporte Privado'),
        ('public', 'Transporte Público'),
    ], string='Modalidad de Transporte',
       default='private',
       help='Modalidad del transporte')
    
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        help='Conductor asignado al traslado'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo',
        help='Vehículo asignado al traslado'
    )
    
    # ========== PESO Y BULTOS ==========
    total_weight = fields.Float(
        string='Peso Total (kg)',
        compute='_compute_total_weight',
        store=True,
        readonly=False,
        digits=(10, 2),
        help='Peso total de la mercancía en kilogramos (calculado automáticamente, editable manualmente)'
    )
    
    total_packages = fields.Integer(
        string='Número de Bultos',
        default=1,
        help='Cantidad de bultos o paquetes'
    )
    
    # ========== ESTADO SUNAT ==========
    gre_state = fields.Selection([
        ('draft', 'Borrador'),
        ('ready', 'Listo para Enviar'),
        ('sent', 'Enviado a SUNAT'),
        ('accepted', 'Aceptado por SUNAT'),
        ('rejected', 'Rechazado por SUNAT'),
        ('cancelled', 'Anulado'),
    ], string='Estado GRE',
       default='draft',
       copy=False,
       tracking=True,
       help='Estado de la guía de remisión electrónica')
    
    gre_sent_date = fields.Datetime(
        string='Fecha de Envío',
        readonly=True,
        copy=False,
        help='Fecha y hora de envío a SUNAT'
    )
    
    gre_ticket_number = fields.Char(
        string='Número de Ticket',
        readonly=True,
        copy=False,
        help='Número de ticket generado por NubeFact/SUNAT'
    )
    
    # ========== ENLACES DE DOCUMENTOS ==========
    gre_pdf_url = fields.Char(
        string='Enlace PDF',
        readonly=True,
        copy=False,
        help='URL del PDF de la guía'
    )
    
    gre_xml_url = fields.Char(
        string='Enlace XML',
        readonly=True,
        copy=False,
        help='URL del XML de la guía'
    )
    
    gre_cdr_url = fields.Char(
        string='Enlace CDR',
        readonly=True,
        copy=False,
        help='URL de la Constancia de Recepción de SUNAT'
    )
    
    gre_hash_code = fields.Char(
        string='Código Hash',
        readonly=True,
        copy=False,
        help='Código hash del comprobante'
    )
    
    # ========== RESPUESTAS Y ERRORES ==========
    gre_response = fields.Text(
        string='Respuesta SUNAT',
        readonly=True,
        copy=False,
        help='Respuesta completa de SUNAT/NubeFact'
    )
    
    gre_error_message = fields.Text(
        string='Mensaje de Error',
        readonly=True,
        copy=False,
        help='Mensaje de error si el envío falló'
    )
    
    # ========== CAMPOS RELACIONADOS ==========
    driver_license = fields.Char(
        related='driver_id.license_number',
        string='Licencia del Conductor',
        readonly=True
    )
    
    vehicle_plate = fields.Char(
        related='vehicle_id.license_plate',
        string='Placa del Vehículo',
        readonly=True
    )
    
    @api.depends('move_ids', 'move_ids.product_id', 'move_ids.product_uom_qty', 'move_line_ids', 'move_line_ids.quantity')
    def _compute_total_weight(self):
        """Calcula el peso total de los productos"""
        for picking in self:
            total = 0.0
            # Si el picking está validado (done), usar move_line_ids para cantidades reales
            if picking.state == 'done' and picking.move_line_ids:
                for move_line in picking.move_line_ids:
                    if move_line.product_id.weight:
                        total += move_line.product_id.weight * move_line.quantity
            else:
                # Si está en borrador o asignado, usar product_uom_qty de los moves
                for move in picking.move_ids:
                    if move.product_id.weight:
                        total += move.product_id.weight * move.product_uom_qty
            picking.total_weight = total
    
    def action_recalculate_weight(self):
        """Recalcula manualmente el peso total"""
        for picking in self:
            total = 0.0
            # Si el picking está validado (done), usar move_line_ids para cantidades reales
            if picking.state == 'done' and picking.move_line_ids:
                for move_line in picking.move_line_ids:
                    if move_line.product_id.weight:
                        total += move_line.product_id.weight * move_line.quantity
            else:
                # Si está en borrador o asignado, usar product_uom_qty de los moves
                for move in picking.move_ids:
                    if move.product_id.weight:
                        total += move.product_id.weight * move.product_uom_qty
            picking.write({'total_weight': total})
    
    @api.constrains('transfer_reason')
    def _check_transfer_reason(self):
        """Valida que se haya seleccionado un motivo de traslado para GRE"""
        for picking in self:
            if picking.is_electronic_guide and not picking.transfer_reason:
                raise ValidationError(_(
                    'Debe seleccionar un motivo de traslado para generar la guía electrónica.'
                ))
    
    @api.constrains('total_weight')
    def _check_total_weight(self):
        """Valida que el peso total sea mayor a 0 para GRE"""
        for picking in self:
            if picking.is_electronic_guide and picking.total_weight <= 0:
                raise ValidationError(_(
                    'El peso total debe ser mayor a 0 para generar la guía electrónica. '
                    'Verifique que los productos tengan peso configurado.'
                ))
    
    @api.constrains('driver_id', 'vehicle_id')
    def _check_driver_vehicle_gre(self):
        """Valida que se hayan asignado conductor y vehículo para GRE"""
        for picking in self:
            if picking.is_electronic_guide and picking.gre_state in ['ready', 'sent']:
                if not picking.driver_id:
                    raise ValidationError(_('Debe asignar un conductor para la guía electrónica.'))
                if not picking.vehicle_id:
                    raise ValidationError(_('Debe asignar un vehículo para la guía electrónica.'))
    
    def action_mark_as_electronic_guide(self):
        """Marca el picking como guía electrónica"""
        for picking in self:
            if picking.state != 'done':
                raise UserError(_('Solo se pueden marcar como guía electrónica los traslados validados.'))
            
            picking.write({
                'is_electronic_guide': True,
                'gre_state': 'draft',
            })
            
            # Auto-completar datos desde la ubicación origen si es un warehouse
            if picking.location_id.warehouse_id:
                warehouse = picking.location_id.warehouse_id
                if warehouse.partner_id:
                    picking.origin_address = warehouse.partner_id.contact_address
            
            # Auto-completar datos desde el partner destino
            if picking.partner_id:
                picking.destination_address = picking.partner_id.contact_address
    
    def action_prepare_gre(self):
        """Prepara la guía para envío a SUNAT"""
        for picking in self:
            if not picking.is_electronic_guide:
                raise UserError(_('Este picking no está marcado como guía electrónica.'))
            
            # Validaciones antes de preparar
            if not picking.transfer_reason:
                raise UserError(_('Debe seleccionar el motivo de traslado.'))
            if not picking.driver_id:
                raise UserError(_('Debe asignar un conductor.'))
            if not picking.vehicle_id:
                raise UserError(_('Debe asignar un vehículo.'))
            if picking.total_weight <= 0:
                raise UserError(_(
                    'El peso total debe ser mayor a 0. '
                    'Verifique que los productos tengan peso configurado.'
                ))
            if not picking.origin_address:
                raise UserError(_('Debe especificar la dirección de partida.'))
            if not picking.destination_address:
                raise UserError(_('Debe especificar la dirección de llegada.'))
            
            picking.write({'gre_state': 'ready'})
    
    def action_cancel_gre(self):
        """Cancela la guía electrónica"""
        for picking in self:
            if picking.gre_state == 'accepted':
                raise UserError(_(
                    'No se puede cancelar una guía aceptada por SUNAT. '
                    'Debe generar una baja en el portal de SUNAT.'
                ))
            
            picking.write({'gre_state': 'cancelled'})
    
    def action_reset_gre(self):
        """Reinicia la guía a borrador"""
        for picking in self:
            if picking.gre_state == 'accepted':
                raise UserError(_('No se puede reiniciar una guía aceptada por SUNAT.'))
            
            picking.write({
                'gre_state': 'draft',
                'gre_sent_date': False,
                'gre_ticket_number': False,
                'gre_response': False,
                'gre_error_message': False,
            })
    
    def action_download_pdf(self):
        """Descarga el PDF de la guía"""
        self.ensure_one()
        if not self.gre_pdf_url:
            raise UserError(_('No hay PDF disponible para esta guía.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.gre_pdf_url,
            'target': 'new',
        }
    
    def action_download_xml(self):
        """Descarga el XML de la guía"""
        self.ensure_one()
        if not self.gre_xml_url:
            raise UserError(_('No hay XML disponible para esta guía.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.gre_xml_url,
            'target': 'new',
        }
    
    def action_download_cdr(self):
        """Descarga el CDR de la guía"""
        self.ensure_one()
        if not self.gre_cdr_url:
            raise UserError(_('No hay CDR disponible para esta guía.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.gre_cdr_url,
            'target': 'new',
        }
    
    # ========== INTEGRACIÓN CON NUBEFACT ==========
    
    def _get_sunat_uom_code(self, uom):
        """
        Convierte las unidades de medida de Odoo a códigos SUNAT (Catálogo 03).
        Retorna el código SUNAT correspondiente.
        """
        # Mapeo de unidades de medida comunes a códigos SUNAT
        uom_map = {
            # Unidades
            'unidad': 'NIU',
            'unidades': 'NIU',
            'unit': 'NIU',
            'units': 'NIU',
            'u': 'NIU',
            'und': 'NIU',
            'pieza': 'NIU',
            'piezas': 'NIU',
            
            # Peso
            'kg': 'KGM',
            'kilogramo': 'KGM',
            'kilogramos': 'KGM',
            'kgs': 'KGM',
            'gramo': 'GRM',
            'gramos': 'GRM',
            'g': 'GRM',
            'tonelada': 'TNE',
            'toneladas': 'TNE',
            
            # Volumen
            'litro': 'LTR',
            'litros': 'LTR',
            'l': 'LTR',
            'mililitro': 'MLT',
            'mililitros': 'MLT',
            'ml': 'MLT',
            'galón': 'GLL',
            'galon': 'GLL',
            
            # Longitud
            'metro': 'MTR',
            'metros': 'MTR',
            'm': 'MTR',
            'centímetro': 'CMT',
            'centimetro': 'CMT',
            'cm': 'CMT',
            
            # Otros
            'caja': 'BX',
            'cajas': 'BX',
            'paquete': 'PK',
            'paquetes': 'PK',
            'docena': 'DZN',
            'docenas': 'DZN',
            'millar': 'MIL',
            'millares': 'MIL',
        }
        
        # Normalizar el nombre de la unidad (minúsculas, sin espacios extra)
        uom_name = uom.name.lower().strip() if uom else ''
        
        # Buscar en el mapeo
        return uom_map.get(uom_name, 'NIU')  # Por defecto NIU (Unidad) si no se encuentra
    
    def _prepare_nubefact_gre_data(self):
        """
        Prepara los datos de la guía de remisión para enviar a NubeFact.
        Sigue la estructura de la API de NubeFact para guías de remisión.
        """
        self.ensure_one()
        
        # Validaciones previas
        if not self.company_id.vat:
            raise UserError(_('La compañía no tiene RUC configurado.'))
        
        if not self.partner_id:
            raise UserError(_('Debe especificar el destinatario.'))
        
        if not self.transfer_reason:
            raise UserError(_('Debe seleccionar el motivo de traslado.'))
        
        if not self.driver_id:
            raise UserError(_('Debe asignar un conductor.'))
        
        if not self.vehicle_id:
            raise UserError(_('Debe asignar un vehículo.'))
        
        # Preparar líneas de productos
        items = []
        
        # Si el picking está validado, usar move_line_ids para cantidades reales
        if self.state == 'done' and self.move_line_ids:
            for move_line in self.move_line_ids:
                if move_line.quantity > 0:
                    # Si el producto no tiene código, usar ID del producto
                    product_code = move_line.product_id.default_code or f"PROD-{move_line.product_id.id}"
                    items.append({
                        "unidad_de_medida": self._get_sunat_uom_code(move_line.product_uom_id),
                        "codigo": product_code,
                        "descripcion": move_line.product_id.name or '',
                        "cantidad": str(move_line.quantity),
                    })
        else:
            # Si no está validado, usar move_ids con product_uom_qty
            for move in self.move_ids:
                if move.product_uom_qty > 0:
                    # Si el producto no tiene código, usar ID del producto
                    product_code = move.product_id.default_code or f"PROD-{move.product_id.id}"
                    items.append({
                        "unidad_de_medida": self._get_sunat_uom_code(move.product_uom),
                        "codigo": product_code,
                        "descripcion": move.product_id.name or '',
                        "cantidad": str(move.product_uom_qty),
                    })
        
        if not items:
            raise UserError(_('No hay productos en el traslado.'))
        
        # Datos del cliente (destinatario)
        partner_vat = self.partner_id.vat or ''
        if partner_vat.startswith('PE'):
            partner_vat = partner_vat[2:]
        
        # Determinar tipo de documento del cliente: 6=RUC, 1=DNI
        cliente_tipo_doc = 6 if len(partner_vat) == 11 else 1
        
        # Datos de la empresa (remitente)
        company_vat = self.company_id.vat.replace('PE', '') if self.company_id.vat else ''
        
        # Separar nombre y apellidos del conductor (si es posible)
        conductor_nombre = self.driver_id.name or ''
        conductor_apellidos = ''
        if conductor_nombre:
            partes = conductor_nombre.split(' ', 1)
            conductor_nombre = partes[0]
            conductor_apellidos = partes[1] if len(partes) > 1 else ''
        
        # Estructura de datos según documentación oficial de NubeFact para GRE Remitente
        # Referencia: https://docs.google.com/document/d/1pU_1nJ_9QU4I385tvz9_bD6DaFXwXVnNZVFMm8rftOg
        gre_data = {
            "operacion": "generar_guia",
            "tipo_de_comprobante": 7,  # 7 = GRE Remitente (transporte privado)
            "serie": self.gre_serie or "T001",
            "numero": str(int(self.gre_number)) if self.gre_number else "1",
            
            # Datos del cliente (destinatario)
            "cliente_tipo_de_documento": cliente_tipo_doc,
            "cliente_numero_de_documento": partner_vat,
            "cliente_denominacion": self.partner_id.name or '',
            "cliente_direccion": self.destination_address or self.partner_id.street or '',
            "cliente_email": self.partner_id.email or '',
            
            # Fechas
            "fecha_de_emision": fields.Date.today().strftime('%d-%m-%Y'),
            "fecha_de_inicio_de_traslado": fields.Date.today().strftime('%d-%m-%Y'),
            
            # Observaciones
            "observaciones": self.note or '',
            
            # Motivo de traslado
            "motivo_de_traslado": self.transfer_reason,
            
            # Peso y bultos
            "peso_bruto_total": str(self.total_weight),
            "peso_bruto_unidad_de_medida": "KGM",  # Kilogramos
            "numero_de_bultos": str(self.total_packages or 1),
            
            # Tipo de transporte: 01=Transporte público, 02=Transporte privado
            "tipo_de_transporte": "01" if self.transport_mode == 'public' else "02",
            
            # Datos del transportista (la empresa en transporte privado)
            "transportista_documento_tipo": 6,  # RUC
            "transportista_documento_numero": company_vat,
            "transportista_denominacion": self.company_id.name or '',
            "transportista_placa_numero": self.vehicle_id.license_plate or '',
            
            # Datos del conductor
            "conductor_documento_tipo": 1,  # DNI
            "conductor_documento_numero": self.driver_id.document_number or '',
            "conductor_nombre": conductor_nombre,
            "conductor_apellidos": conductor_apellidos,
            "conductor_numero_licencia": self.driver_id.license_number or '',
            
            # Puntos de partida y llegada
            "punto_de_partida_ubigeo": self.origin_ubigeo or '150101',
            "punto_de_partida_direccion": self.origin_address or '',
            "punto_de_partida_codigo_establecimiento_sunat": "0000",
            
            "punto_de_llegada_ubigeo": self.destination_ubigeo or '150101',
            "punto_de_llegada_direccion": self.destination_address or '',
            "punto_de_llegada_codigo_establecimiento_sunat": "0000",
            
            # Items (productos)
            "items": items,
            
            # Configuración de envío
            "enviar_automaticamente_al_cliente": "false",
            "formato_de_pdf": "",
        }
        
        return gre_data
    
    def action_send_gre_to_sunat(self):
        """
        Envía la guía de remisión electrónica a SUNAT mediante NubeFact.
        """
        self.ensure_one()
        
        # Validaciones previas
        if not self.is_electronic_guide:
            raise UserError(_('Este picking no está marcado como guía electrónica.'))
        
        if self.gre_state not in ['ready', 'rejected']:
            raise UserError(_(
                'Solo se pueden enviar guías en estado "Listo para Enviar" o "Rechazado". '
                'Estado actual: %s'
            ) % dict(self._fields['gre_state'].selection).get(self.gre_state))
        
        # Obtener configuración de NubeFact
        try:
            config = self.env['nubefact.config'].search([
                ('company_id', '=', self.company_id.id),
                ('active', '=', True)
            ], limit=1)
        except KeyError:
            raise UserError(_(
                'No se encontró el módulo nubefact_sunat. '
                'Por favor, instale el módulo de integración con NubeFact.'
            ))
        
        if not config:
            raise UserError(_(
                'No se ha configurado la conexión con NubeFact. '
                'Por favor, configure las credenciales en Contabilidad > Configuración > NubeFact.'
            ))
        
        try:
            # Preparar datos de la guía
            gre_data = self._prepare_nubefact_gre_data()
            
            # URL de la API de NubeFact
            # Nota: NubeFact usa el mismo endpoint base pero con operacion "generar_guia"
            url = config.get_api_url()
            
            # Headers según documentación de NubeFact
            headers = {
                'Authorization': config.token,
                'Content-Type': 'application/json'
            }
            
            _logger.info(f"📤 Enviando GRE {self.name} a NubeFact/SUNAT")
            _logger.info(f"URL: {url}")
            _logger.info(f"📋 Datos GRE enviados:\n{json.dumps(gre_data, indent=2, ensure_ascii=False)}")
            
            # Realizar petición POST a NubeFact
            response = requests.post(
                url,
                headers=headers,
                json=gre_data,
                timeout=30
            )
            
            _logger.info(f"Respuesta de NubeFact: Status {response.status_code}, Body: {response.text}")
            
            # Procesar respuesta
            if response.status_code == 200:
                response_data = response.json()
                
                # Actualizar campos
                self.write({
                    'gre_sent_date': fields.Datetime.now(),
                    'gre_response': json.dumps(response_data, indent=2),
                })
                
                # Verificar si SUNAT aceptó la guía
                if response_data.get('aceptada_por_sunat'):
                    self.write({
                        'gre_state': 'accepted',
                        'gre_pdf_url': response_data.get('enlace_del_pdf', ''),
                        'gre_xml_url': response_data.get('enlace_del_xml', ''),
                        'gre_cdr_url': response_data.get('enlace_del_cdr', ''),
                        'gre_hash_code': response_data.get('codigo_hash', ''),
                        'gre_ticket_number': response_data.get('numero_ticket', ''),
                    })
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Éxito'),
                            'message': _('La guía de remisión fue aceptada por SUNAT correctamente.'),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    # SUNAT rechazó la guía
                    error_msg = response_data.get('sunat_description', '') or response_data.get('errors', '')
                    self.write({
                        'gre_state': 'rejected',
                        'gre_error_message': error_msg,
                    })
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Rechazado por SUNAT'),
                            'message': f"{_('La guía fue rechazada')}: {error_msg}",
                            'type': 'warning',
                            'sticky': True,
                        }
                    }
            else:
                # Error en la API
                error_msg = response.text
                self.write({
                    'gre_state': 'rejected',
                    'gre_error_message': error_msg,
                    'gre_response': error_msg,
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': f"{_('Error al enviar a NubeFact')}: {error_msg}",
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                
        except Exception as e:
            _logger.error(f"Error al enviar GRE a SUNAT: {str(e)}", exc_info=True)
            self.write({
                'gre_state': 'rejected',
                'gre_error_message': str(e),
            })
            
            raise UserError(_('Error al enviar GRE a SUNAT: %s') % str(e))
    
    def action_query_gre_status(self):
        """Consulta el estado de una guía en SUNAT"""
        self.ensure_one()
        
        if not self.is_electronic_guide:
            raise UserError(_('Este picking no es una guía electrónica.'))
        
        # Obtener configuración
        try:
            config = self.env['nubefact.config'].search([
                ('company_id', '=', self.company_id.id),
                ('active', '=', True)
            ], limit=1)
        except KeyError:
            raise UserError(_('No se encontró el módulo nubefact_sunat.'))
        
        if not config:
            raise UserError(_('No se ha configurado la conexión con NubeFact.'))
        
        try:
            # Preparar datos de consulta
            consulta_data = {
                "operacion": "consultar_guia",
                "tipo_de_comprobante": "09",
                "serie": self.gre_serie or "T001",
                "numero": int(self.gre_number) if self.gre_number else 1,
            }
            
            url = config.get_api_url()
            headers = {
                'Authorization': config.token,
                'Content-Type': 'application/json'
            }
            
            _logger.info(f"🔍 Consultando estado de GRE {self.name}")
            
            response = requests.post(
                url,
                headers=headers,
                json=consulta_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Actualizar estado si es necesario
                if response_data.get('aceptada_por_sunat'):
                    self.write({'gre_state': 'accepted'})
                    message = _('La guía está aceptada por SUNAT.')
                else:
                    message = _('Estado: %s') % response_data.get('sunat_description', 'Desconocido')
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Consulta de Estado'),
                        'message': message,
                        'type': 'info',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_('Error al consultar: %s') % response.text)
                
        except Exception as e:
            _logger.error(f"Error al consultar estado GRE: {str(e)}", exc_info=True)
            raise UserError(_('Error al consultar estado: %s') % str(e))
    
    # ========== LÓGICA DE RECOJO EN LOCAL ==========
    
    @api.model
    def create(self, vals):
        """
        Override create para configurar ubicación de destino si es recojo en local.
        """
        picking = super(StockPicking, self).create(vals)
        
        # Si el picking está relacionado a una venta con recojo en local
        if picking.sale_id and picking.sale_id.delivery_type == 'pickup':
            # Obtener ubicación "Para Recoger"
            pickup_location = picking.sale_id.pickup_location_id
            
            if not pickup_location:
                pickup_location = self.env['stock.location'].search([
                    ('name', '=', 'Para Recoger'),
                    ('usage', '=', 'internal')
                ], limit=1)
            
            if pickup_location and picking.location_dest_id.usage == 'customer':
                # Cambiar la ubicación de destino a "Para Recoger"
                picking.write({'location_dest_id': pickup_location.id})
        
        return picking
    
    def button_validate(self):
        """
        Override button_validate para notificar al cliente cuando el pedido
        está listo para recoger.
        """
        res = super(StockPicking, self).button_validate()
        
        for picking in self:
            # Si es un picking de venta con recojo en local
            if picking.sale_id and picking.sale_id.delivery_type == 'pickup':
                # Si el picking está validado y el pedido está reservado
                if picking.state == 'done' and picking.sale_id.pickup_state == 'reserved':
                    # Marcar automáticamente como listo para recoger
                    try:
                        picking.sale_id.action_mark_ready_for_pickup()
                    except Exception as e:
                        _logger.warning(
                            f"No se pudo marcar pedido {picking.sale_id.name} como listo: {str(e)}"
                        )
        
        return res

