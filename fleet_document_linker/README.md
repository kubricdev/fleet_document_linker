# Fleet Document Linker

Módulo para Odoo 18 que permite la vinculación masiva de documentos a vehículos de la flota.

## Funcionalidades

- Vinculación automática de documentos basada en el `vehicle_id` presente en el nombre del archivo
- Wizard de vinculación masiva con interfaz intuitiva de 3 pasos
- Búsqueda de documentos por patrones configurables (vehicle_id, placa, personalizado)
- Soporte para múltiples formatos de archivo (PDF, JPG, PNG, DOC, etc.)
- Acción de servidor disponible desde la vista de documentos
- Menú dedicado en Fleet para acceso directo

## Uso del Wizard

### Paso 1: Configuración
1. Seleccionar los vehículos objetivo (opcional, si no se selecciona busca en todos)
2. Elegir la carpeta de documentos donde buscar
3. Seleccionar el tipo de patrón:
   - **Por Vehicle ID**: Busca archivos como `0001_archivo.pdf` donde `0001` es el vehicle_id
   - **Por Placa**: Busca archivos como `ABC123_documento.jpg` donde `ABC123` es la placa
   - **Personalizado**: Usar expresión regular personalizada
4. Configurar extensiones de archivo permitidas

### Paso 2: Revisión
- Ver todos los documentos encontrados y sus coincidencias
- Verificar que las vinculaciones sean correctas
- Editar manualmente si es necesario

### Paso 3: Resultados
- Ver estadísticas de documentos vinculados exitosamente
- Revisar errores si los hay

## Patrones de Nombres de Archivo

Los documentos deben seguir estos patrones:

- **Vehicle ID**: `{vehicle_id}_{descripcion}.{extension}`
  - Ejemplos: `0001_manual.pdf`, `0001_foto.jpg`, `0001_seguro.png`
- **Placa**: `{placa}_{descripcion}.{extension}`
  - Ejemplos: `ABC123_tarjeta.pdf`, `XYZ789_revision.jpg`

**Importante**: El ID se extrae del texto **antes del primer guión bajo (_)**

## Acceso al Módulo

1. **Desde el menú Fleet**: Fleet > Vehículos > Vinculación Masiva de Documentos
2. **Desde documentos**: Seleccionar documentos > Acciones > Vincular a Vehículos Fleet

## Patrones Soportados

### Extracción Automática del ID
El módulo extrae automáticamente el ID del vehículo del nombre del documento:
- **Con guión bajo**: Toma todo lo que está antes del primer `_`
- **Sin guión bajo**: Toma el nombre completo sin la extensión

#### Ejemplos:
```
0001_archivo.pdf        → ID: 0001
ABC123_documento.docx   → ID: ABC123
XYZ789_foto_vehiculo.jpg → ID: XYZ789
DEF456.pdf              → ID: DEF456
```

### Compatibilidad
- Funciona con cualquier formato de ID (numérico, alfanumérico, mixto)
- No requiere patrones específicos
- Flexible para diferentes convenciones de nomenclatura

## Instalación

1. Copie el módulo a su directorio de addons
2. Actualice la lista de módulos
3. Instale `fleet_document_linker`

### Dependencias
- `fleet` - Gestión de vehículos
- `fleet_extension` - Extensiones de fleet
- `fleet_vehicle_id_compat` - Compatibilidad de vehicle_id

**Nota**: Este módulo ha sido modificado para no depender del módulo `documents` de Odoo, haciéndolo más compatible con diferentes instalaciones.

## Uso

### Desde Vehículos
1. Vaya a **Fleet → Vehículos**
2. Seleccione uno o más vehículos
3. Use **Acciones → Vincular Documentos Masivamente**

### Desde Documentos
1. Vaya a **Documentos**
2. Seleccione documentos a vincular
3. Use **Acciones → Vincular a Vehículos Fleet**

### Wizard Avanzado
1. Configure patrones de búsqueda
2. Seleccione carpetas específicas
3. Revise coincidencias encontradas
4. Confirme vinculación

## Botones en Vista de Vehículo

- **Vincular Documentos**: Abre wizard de vinculación masiva
- **Verificar Documents**: Verifica instalación del módulo documents
- **Probar Lógica**: Prueba patrones de coincidencia
- **Avanzado Masivo**: Wizard con opciones avanzadas

## Seguridad

- **fleet_group_manager**: Acceso completo a todas las funcionalidades
- **fleet_group_user**: Acceso de solo lectura a wizards

## Logs y Debugging

El módulo incluye logging detallado para debugging:
```python
_logger = logging.getLogger(__name__)
```

## Estructura del Módulo

```
fleet_document_linker/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── fleet_vehicle.py
├── wizards/
│   ├── __init__.py
│   └── mass_link_documents_wizard.py
├── views/
│   ├── fleet_vehicle_views.xml
│   └── mass_link_documents_wizard_views.xml
├── data/
│   ├── fleet_vehicle_actions.xml
│   └── fleet_documents_link_server_action.xml
└── security/
    └── ir.model.access.csv
```

## Contribución

Para contribuir al módulo:
1. Fork el repositorio
2. Cree una rama para su feature
3. Implemente cambios con tests
4. Envíe pull request

## Licencia

LGPL-3

## Soporte

Para soporte técnico, contacte al equipo de desarrollo.