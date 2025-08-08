import re
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    def action_mass_link_documents_by_name(self):
        """
        Acción para abrir el wizard de vinculación masiva de documentos
        basándose en el vehicle_id en el nombre del documento
        """
        return {
            'name': _('Vinculación Masiva de Documentos'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.mass.link.documents.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_vehicle_ids': [(6, 0, self.ids)],
                'active_model': 'fleet.vehicle',
                'active_ids': self.ids,
            }
        }
    
    def action_check_documents_module(self):
        """
        Verificar si el módulo documents está instalado
        """
        documents_module = self.env['ir.module.module'].search([
            ('name', '=', 'documents'),
            ('state', '=', 'installed')
        ])
        
        if not documents_module:
            raise UserError(_(
                'El módulo Documents no está instalado. '
                'Por favor, instale el módulo Documents para usar esta funcionalidad.'
            ))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Módulo Documents'),
                'message': _('El módulo Documents está correctamente instalado.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_test_linking_logic(self):
        """
        Probar la lógica de vinculación para debugging
        """
        if not self:
            raise UserError(_('Seleccione al menos un vehículo.'))
        
        # Buscar documentos que podrían coincidir
        documents = self.env['documents.document'].search([])
        matches = []
        
        for vehicle in self:
            vehicle_id = vehicle.vehicle_id or ''
            if not vehicle_id:
                continue
                
            # Buscar documentos que contengan el vehicle_id antes del primer guión bajo
            for doc in documents:
                if not doc.name:
                    continue
                
                # Extraer ID del nombre del documento
                if '_' in doc.name:
                    extracted_id = doc.name.split('_')[0].upper()
                else:
                    extracted_id = doc.name.split('.')[0].upper()
                
                # Comparar con el vehicle_id
                if extracted_id == vehicle_id.upper():
                    matches.append({
                        'vehicle': vehicle.name,
                        'vehicle_id': vehicle_id,
                        'document': doc.name,
                        'document_id': doc.id
                    })
        
        message = _('Coincidencias encontradas:\n')
        for match in matches[:10]:  # Limitar a 10 para no sobrecargar
            message += f"• {match['vehicle']} ({match['vehicle_id']}) → {match['document']}\n"
        
        if not matches:
            message = _('No se encontraron documentos que coincidan con el patrón vehicle_id_archivo.extensión')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Prueba de Lógica de Vinculación'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def action_advanced_mass_link(self):
        """
        Acción avanzada para vinculación masiva con más opciones
        """
        return {
            'name': _('Vinculación Masiva Avanzada'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.mass.link.documents.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_vehicle_ids': [(6, 0, self.ids)],
                'default_advanced_mode': True,
                'active_model': 'fleet.vehicle',
                'active_ids': self.ids,
            }
        }