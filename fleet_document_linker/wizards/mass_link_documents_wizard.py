import re
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class FleetMassLinkDocumentsLine(models.TransientModel):
    _name = 'fleet.mass.link.documents.line'
    _description = 'Línea de Documento para Vinculación Masiva'
    _table = 'fleet_mass_link_documents_line'
    _rec_name = 'document_name'
    _auto = True
    _check_company_auto = False
    _log_access = True
    
    wizard_id = fields.Many2one(
        'fleet.mass.link.documents.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    document_name = fields.Char(
        string='Nombre del Documento',
        required=True
    )
    
    document_path = fields.Char(
        string='Ruta del Documento',
        help='Ruta completa del archivo'
    )
    
    document_id = fields.Many2one(
        'documents.document',
        string='Documento',
        help='Referencia al documento en el módulo Documents'
    )
    
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehículo Coincidente'
    )
    
    matched = fields.Boolean(
        string='Coincide',
        default=False
    )
    
    linked = fields.Boolean(
        string='Vinculado',
        default=False
    )

class FleetMassLinkDocumentsWizard(models.TransientModel):
    _name = 'fleet.mass.link.documents.wizard'
    _description = 'Wizard para Vinculación Masiva de Documentos a Vehículos'
    _table = 'fleet_mass_link_documents_wizard'
    _rec_name = 'id'
    _auto = True
    _check_company_auto = False
    _log_access = True
    
    # Estados del wizard
    state = fields.Selection([
        ('step1', 'Configuración'),
        ('step2', 'Revisión'),
        ('step3', 'Resultados')
    ], default='step1', string='Estado')
    
    # Configuración
    vehicle_ids = fields.Many2many(
        'fleet.vehicle', 
        string='Vehículos',
        help='Vehículos a los que se vincularán los documentos'
    )
    
    search_path = fields.Char(
        string='Ruta de Búsqueda',
        help='Ruta del directorio donde buscar los documentos'
    )
    
    folder_id = fields.Many2one(
        'documents.folder',
        string='Carpeta de Documentos',
        help='Carpeta donde buscar los documentos'
    )
    
    pattern_type = fields.Selection([
        ('vehicle_id', 'Por Vehicle ID (ej: 0001_archivo.pdf)'),
        ('license_plate', 'Por Placa (ej: ABC123_archivo.pdf)'),
        ('custom', 'Patrón Personalizado')
    ], default='vehicle_id', string='Tipo de Patrón')
    
    custom_pattern = fields.Char(
        string='Patrón Personalizado',
        help='Expresión regular personalizada. Use {vehicle_field} como placeholder'
    )
    
    file_extensions = fields.Char(
        string='Extensiones de Archivo',
        default='pdf,jpg,jpeg,png,doc,docx',
        help='Extensiones de archivo separadas por comas'
    )
    
    advanced_mode = fields.Boolean(
        string='Modo Avanzado',
        default=False
    )
    
    # Resultados de búsqueda
    document_line_ids = fields.One2many(
        'fleet.mass.link.documents.line',
        'wizard_id',
        string='Documentos Encontrados'
    )
    
    # Estadísticas
    total_documents_found = fields.Integer(
        string='Total Documentos Encontrados',
        compute='_compute_statistics'
    )
    
    total_matches = fields.Integer(
        string='Total Coincidencias',
        compute='_compute_statistics'
    )
    
    total_vehicles = fields.Integer(
        string='Total Vehículos',
        compute='_compute_statistics'
    )
    
    @api.depends('document_line_ids', 'vehicle_ids')
    def _compute_statistics(self):
        for wizard in self:
            wizard.total_documents_found = len(wizard.document_line_ids)
            wizard.total_matches = len(wizard.document_line_ids.filtered('vehicle_id'))
            wizard.total_vehicles = len(wizard.vehicle_ids)
    
    def action_search_documents(self):
        """
        Buscar documentos que coincidan con el patrón
        """
        self.ensure_one()
        
        if not self.vehicle_ids:
            raise UserError(_('Debe seleccionar al menos un vehículo.'))
        
        # Limpiar líneas anteriores
        self.document_line_ids.unlink()
        
        # Buscar documentos
        domain = []
        if self.folder_id:
            domain.append(('folder_id', '=', self.folder_id.id))
        
        documents = self.env['documents.document'].search(domain)
        
        # Crear líneas para documentos encontrados
        lines_to_create = []
        
        for document in documents:
            if not document.name:
                continue
            
            # Buscar vehículo coincidente
            matching_vehicle = self._find_matching_vehicle(document.name)
            
            line_vals = {
                'wizard_id': self.id,
                'document_name': document.name,
                'document_id': document.id,
                'vehicle_id': matching_vehicle.id if matching_vehicle else False,
                'matched': bool(matching_vehicle),
            }
            lines_to_create.append(line_vals)
        
        if lines_to_create:
            self.env['fleet.mass.link.documents.line'].create(lines_to_create)
        
        self.state = 'step2'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.mass.link.documents.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def _find_matching_vehicle(self, document_name):
        """
        Encontrar el vehículo que coincide con el nombre del documento
        Extrae el ID antes del primer guión bajo (_)
        """
        # Extraer el ID del nombre del documento
        if '_' in document_name:
            extracted_id = document_name.split('_')[0].upper()
        else:
            # Si no hay guión bajo, tomar el nombre completo sin extensión
            extracted_id = document_name.split('.')[0].upper()
        
        # Buscar el vehículo que coincida con el ID extraído
        for vehicle in self.vehicle_ids:
            vehicle_value = self._get_vehicle_field_value(vehicle)
            if vehicle_value and vehicle_value.upper() == extracted_id:
                return vehicle
        
        return False
    
    def _get_search_pattern(self):
        """
        Obtener el patrón de búsqueda basado en la configuración
        """
        extensions = self.file_extensions.replace(' ', '').split(',')
        ext_pattern = '|'.join(extensions)
        
        if self.pattern_type == 'vehicle_id':
            return r'^{vehicle_field}_.*\.(' + ext_pattern + r')$'
        elif self.pattern_type == 'license_plate':
            return r'^{vehicle_field}_.*\.(' + ext_pattern + r')$'
        elif self.pattern_type == 'custom' and self.custom_pattern:
            return self.custom_pattern
        else:
            return r'^{vehicle_field}_.*\.(' + ext_pattern + r')$'
    
    def _get_vehicle_field_value(self, vehicle):
        """
        Obtener el valor del campo del vehículo según el tipo de patrón
        """
        if self.pattern_type == 'vehicle_id':
            return vehicle.vehicle_id
        elif self.pattern_type == 'license_plate':
            return vehicle.license_plate
        else:
            return vehicle.vehicle_id  # Por defecto
    
    def action_link_documents(self):
        """
        Vincular los documentos seleccionados a los vehículos
        """
        self.ensure_one()
        
        matched_lines = self.document_line_ids.filtered(lambda l: l.matched and l.vehicle_id)
        
        if not matched_lines:
            raise UserError(_('No hay documentos coincidentes para vincular.'))
        
        linked_count = 0
        errors = []
        
        for line in matched_lines:
            try:
                # Vincular documento al vehículo
                line.document_id.write({
                    'res_model': 'fleet.vehicle',
                    'res_id': line.vehicle_id.id,
                })
                linked_count += 1
                line.linked = True
            except Exception as e:
                errors.append(f"{line.document_id.name}: {str(e)}")
                _logger.error(f"Error vinculando documento {line.document_id.name}: {e}")
        
        # Crear wizard de resultados
        result_wizard = self.env['fleet.documents.link.result.wizard'].create({
            'linked_count': linked_count,
            'error_count': len(errors),
            'error_messages': '\n'.join(errors) if errors else False,
        })
        
        self.state = 'step3'
        
        return {
            'name': _('Resultados de Vinculación'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.documents.link.result.wizard',
            'res_id': result_wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_back_to_step1(self):
        """
        Volver al paso 1
        """
        self.state = 'step1'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.mass.link.documents.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

class FleetDocumentsLinkResultWizard(models.TransientModel):
    _name = 'fleet.documents.link.result.wizard'
    _description = 'Wizard de Resultados de Vinculación para Fleet'
    _table = 'fleet_documents_link_result_wizard'
    _rec_name = 'id'
    _auto = True
    _check_company_auto = False
    _log_access = True
    
    linked_count = fields.Integer(
        string='Documentos Vinculados',
        readonly=True
    )
    
    error_count = fields.Integer(
        string='Errores',
        readonly=True
    )
    
    error_messages = fields.Text(
        string='Mensajes de Error',
        readonly=True
    )
    
    def action_close(self):
        """
        Cerrar el wizard
        """
        return {'type': 'ir.actions.act_window_close'}