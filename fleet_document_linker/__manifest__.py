{
    'name': 'Fleet Document Linker',
    'version': '18.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Vinculación masiva de documentos a vehículos por vehicle_id',
    'description': """
        Módulo para vincular documentos masivamente a vehículos de la flota.
        
        Funcionalidades:
        - Vinculación automática basada en vehicle_id en el nombre del documento
        - Wizard similar a documents.link_to_record_wizard
        - Búsqueda de documentos por patrones como: 0001_archivo.pdf, 0001_foto.jpg
        - Vinculación masiva a registros de fleet.vehicle
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': [
        'fleet',
        'documents',
        'fleet_extension',
        'fleet_vehicle_id_compat'
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/fleet_vehicle_actions.xml',
        'data/fleet_documents_link_server_action.xml',
        'views/fleet_vehicle_views.xml',
        'views/mass_link_documents_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}