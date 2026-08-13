# 🎯 Tenty Parser

**Tenty Parser** es una herramienta CLI moderna para parsear, transformar y convertir entre diferentes formatos de datos estructurados: **JSON**, **YAML** y **TOON** (Token-Oriented Object Notation).

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-Custom-orange.svg)
![PyPI](https://img.shields.io/pypi/v/tenty-parser)

## ✨ Características

- 🔍 **Parse múltiples formatos**: JSON, YAML, TOON
- 🌳 **Visualización en árbol** de estructuras de datos
- 📊 **Generación de schemas**: JSON Schema y OpenAPI
- 🔄 **Conversión entre formatos** con un solo comando
- 🎨 **Salida colorida** con Rich
- ⚡ **Optimizado para LLMs** con formato TOON (30-60% reducción de tokens)

## 📦 Instalación

### Requisitos previos

- Python 3.12+

### Con pip (uso normal)

```bash
pip install tenty-parser
```

Esto deja disponible el comando `tenty` directamente en tu shell — no hace falta clonar el repositorio ni usar `python -m` para nada:

```bash
tenty --help
```

Si estás desarrollando el proyecto en sí (no solo usándolo), ve a [Desarrollo](#-desarrollo) más abajo para instalar desde el código fuente con `uv`.

## 🚀 Uso

### Comandos principales

#### 1. Parse - Analizar archivos

```bash
# Visualizar estructura en árbol
tenty parse data.json

# Mostrar como JSON estructurado
tenty parse data.json --format json

# Generar schema
tenty parse data.json --format schema

# Convertir a TOON
tenty parse data.json --format toon

# Guardar resultado
tenty parse data.json --format toon -o output.toon
```

#### 2. Convert - Convertir entre formatos

```bash
# JSON a TOON
tenty convert input.json output.toon --to toon

# YAML a JSON
tenty convert config.yaml config.json --to json

# JSON a YAML
tenty convert data.json data.yaml --to yaml

# TOON a JSON
tenty convert data.toon data.json --to json
```

#### 3. Schema - Generar schemas

```bash
# Generar JSON Schema
tenty schema data.json -o schema.json

# Generar OpenAPI Schema
tenty schema data.json --format openapi -o openapi.json

# Con título personalizado
tenty schema data.json --title "User API Schema"
```

#### 4. Version - Ver versión

```bash
tenty version
```

## 📖 Formato TOON

TOON (Token-Oriented Object Notation) es un formato optimizado para modelos de lenguaje que reduce el uso de tokens en 30-60%.

### Características de TOON

- ✅ **Arrays con tamaño explícito**: `users[2]:`
- ✅ **Formato tabular para objetos**: `users[2]{id,name,role}:`
- ✅ **Indentación en lugar de llaves**
- ✅ **Sin comillas innecesarias**

### Ejemplo de conversión

**JSON original:**
```json
{
  "user": {
    "name": "John Doe",
    "age": 30,
    "tags": ["developer", "python", "rust"]
  },
  "posts": [
    {
      "id": 1,
      "title": "Hello World",
      "published": true
    }
  ]
}
```

**TOON equivalente:**
```toon
user:
  name: "John Doe"
  age: 30
  tags[3]: developer, python, rust
posts[1]{id,title,published}:
  1,"Hello World",true
```

**Reducción de tokens**: ~45% menos tokens que JSON

## 🏗️ Estructura del proyecto

```
tenty-parser/
├── tenty_parser/
│   ├── models/
│   │   └── structure.py          # Modelos Pydantic
│   ├── parsers/
│   │   ├── json_parser.py        # Parser JSON
│   │   ├── yaml_parser.py        # Parser YAML
│   │   └── toon_parser.py        # Parser TOON
│   ├── transformers/
│   │   ├── to_structure.py       # Transformador a estructura
│   │   ├── to_toon.py           # Transformador a TOON
│   │   └── to_schema.py         # Generador de schemas
│   └── cli.py                    # Interfaz CLI
├── tests/                        # Suite de tests (pytest, cobertura mínima 90%)
├── docs/
│   ├── functionality.md          # Arquitectura y comandos del CLI
│   ├── deployment.md             # Flujo de release y publicación a PyPI
│   ├── dependency-research.md    # Hand-written vs. librerías mantenidas
│   └── testing.md                # Ejemplos reales de entrada/salida por comando
├── pyproject.toml               # Configuración del proyecto
├── README.md                    # Este archivo
├── LICENSE                      # Licencia personalizada
└── .gitignore                   # Archivos ignorados
```

Documentación detallada: [docs/functionality.md](docs/functionality.md) y [docs/deployment.md](docs/deployment.md).

## 🔧 Desarrollo

Si vas a modificar el código del proyecto (no solo usarlo), instala desde el código fuente con [uv](https://github.com/astral-sh/uv):

```bash
# Clonar repositorio
git clone https://github.com/Keniding/tenty-parser.git
cd tenty-parser

# Instalar en modo desarrollo (crea el venv e instala el comando `tenty` en él)
uv sync

# Ejecutar el CLI desde el código fuente
uv run tenty --help

# Ejecutar tests con cobertura
uv run pytest --cov=tenty_parser --cov-report=term-missing
```

### Agregar nuevas características

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-caracteristica`
3. Commit cambios: `git commit -am 'Agregar nueva característica'`
4. Push a la rama: `git push origin feature/nueva-caracteristica`
5. Crea un Pull Request

## 📚 Ejemplos

### Ejemplo 1: Analizar API Response

```bash
# Descargar respuesta de API
curl https://api.example.com/users > users.json

# Visualizar estructura
tenty parse users.json

# Generar schema para documentación
tenty schema users.json -o users-schema.json

# Convertir a TOON para usar con LLMs
tenty convert users.json users.toon --to toon
```

### Ejemplo 2: Convertir configuración

```bash
# Convertir YAML a JSON
tenty convert config.yaml config.json --to json

# Ver estructura
tenty parse config.json --format tree
```

### Ejemplo 3: Workflow completo

```bash
# 1. Parse archivo original
tenty parse data.json --format tree

# 2. Generar schema
tenty schema data.json -o schema.json

# 3. Convertir a TOON para LLM
tenty convert data.json data.toon --to toon

# 4. Convertir de vuelta a JSON
tenty convert data.toon data-restored.json --to json
```

## 🎯 Casos de uso

### Para desarrolladores

- 📝 Generar schemas automáticamente desde ejemplos
- 🔄 Convertir entre formatos de configuración
- 🔍 Explorar estructuras de datos complejas
- 📊 Documentar APIs

### Para trabajar con LLMs

- ⚡ Reducir tokens en prompts (formato TOON)
- 📦 Estructurar datos de forma eficiente
- 🎯 Mejorar comprensión de estructuras por LLMs

### Para análisis de datos

- 🌳 Visualizar jerarquías de datos
- 📋 Validar estructuras
- 🔄 Normalizar formatos

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Lee las guías de contribución
2. Abre un issue para discutir cambios grandes
3. Escribe tests para nuevas características
4. Mantén el estilo de código consistente

**Nota**: Al contribuir, aceptas que tus contribuciones se licencien bajo los mismos términos que este proyecto.

## 📄 Licencia

Este proyecto está bajo una **Licencia Personalizada** con los siguientes términos:

### ✅ Uso Personal y No Comercial
- **LIBRE**: Puedes usar, modificar y distribuir el software gratuitamente
- **Requisito**: Debes dar crédito al autor original (Keniding)

### ⚠️ Uso Comercial
- **REQUIERE AUTORIZACIÓN**: Contacta para obtener una licencia comercial
- **Incluye**: Compensación acordada y/o reconocimiento

### 📝 Reconocimiento Obligatorio
En cualquier uso del software, debes incluir:
```
Powered by Tenty Parser - Created by Keniding
https://github.com/Keniding/tenty-parser
```

Para más detalles, consulta el archivo [LICENSE](LICENSE).

**Para licencias comerciales**, contacta a través de:
- GitHub: [@Keniding](https://github.com/Keniding)
- Issues: [tenty-parser/issues](https://github.com/Keniding/tenty-parser/issues)

## 🙏 Agradecimientos

- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Typer](https://github.com/tiangolo/typer) - CLI framework
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation
- [TOON Format](https://www.palentino.es/blog/toon-el-nuevo-formato-optimizado-para-modelos-de-lenguaje/) - Inspiration

## 📞 Contacto

- **Autor**: Keniding
- **GitHub**: [@Keniding](https://github.com/Keniding)
- **Repositorio**: [tenty-parser](https://github.com/Keniding/tenty-parser)

## 🗺️ Roadmap

- [x] Tests unitarios completos
- [x] Parser TOON más robusto
- [ ] Soporte para más formatos (XML, TOML)
- [ ] Validación de schemas
- [ ] API Python para uso programático
- [ ] Plugins para editores (VSCode)
- [ ] Documentación interactiva

---

**⭐ Si te gusta este proyecto, dale una estrella en [GitHub](https://github.com/Keniding/tenty-parser)!**

---

*Powered by Tenty Parser - Created by Keniding*