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
- [uv](https://github.com/astral-sh/uv) (recomendado) o pip

### Con uv (recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/Keniding/tenty-parser.git
cd tenty-parser

# Instalar dependencias
uv sync

# Ejecutar
uv run python -m src.cli --help
```

### Con pip

```bash
# Clonar el repositorio
git clone https://github.com/Keniding/tenty-parser.git
cd tenty-parser

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -e .

# Ejecutar
python -m src.cli --help
```

## 🚀 Uso

### Comandos principales

#### 1. Parse - Analizar archivos

```bash
# Visualizar estructura en árbol
uv run python -m src.cli parse data.json

# Mostrar como JSON estructurado
uv run python -m src.cli parse data.json --format json

# Generar schema
uv run python -m src.cli parse data.json --format schema

# Convertir a TOON
uv run python -m src.cli parse data.json --format toon

# Guardar resultado
uv run python -m src.cli parse data.json --format toon -o output.toon
```

#### 2. Convert - Convertir entre formatos

```bash
# JSON a TOON
uv run python -m src.cli convert input.json output.toon --to toon

# YAML a JSON
uv run python -m src.cli convert config.yaml config.json --to json

# JSON a YAML
uv run python -m src.cli convert data.json data.yaml --to yaml

# TOON a JSON
uv run python -m src.cli convert data.toon data.json --to json
```

#### 3. Schema - Generar schemas

```bash
# Generar JSON Schema
uv run python -m src.cli schema data.json -o schema.json

# Generar OpenAPI Schema
uv run python -m src.cli schema data.json --format openapi -o openapi.json

# Con título personalizado
uv run python -m src.cli schema data.json --title "User API Schema"
```

#### 4. Version - Ver versión

```bash
uv run python -m src.cli version
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
├── src/
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
├── tests/                        # Tests (próximamente)
├── pyproject.toml               # Configuración del proyecto
├── README.md                    # Este archivo
├── LICENSE                      # Licencia personalizada
└── .gitignore                   # Archivos ignorados
```

## 🔧 Desarrollo

### Configurar entorno de desarrollo

```bash
# Clonar repositorio
git clone https://github.com/Keniding/tenty-parser.git
cd tenty-parser

# Instalar en modo desarrollo
uv sync

# Ejecutar tests (próximamente)
uv run pytest
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
uv run python -m src.cli parse users.json

# Generar schema para documentación
uv run python -m src.cli schema users.json -o users-schema.json

# Convertir a TOON para usar con LLMs
uv run python -m src.cli convert users.json users.toon --to toon
```

### Ejemplo 2: Convertir configuración

```bash
# Convertir YAML a JSON
uv run python -m src.cli convert config.yaml config.json --to json

# Ver estructura
uv run python -m src.cli parse config.json --format tree
```

### Ejemplo 3: Workflow completo

```bash
# 1. Parse archivo original
uv run python -m src.cli parse data.json --format tree

# 2. Generar schema
uv run python -m src.cli schema data.json -o schema.json

# 3. Convertir a TOON para LLM
uv run python -m src.cli convert data.json data.toon --to toon

# 4. Convertir de vuelta a JSON
uv run python -m src.cli convert data.toon data-restored.json --to json
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

- [ ] Tests unitarios completos
- [ ] Parser TOON más robusto
- [ ] Soporte para más formatos (XML, TOML)
- [ ] Validación de schemas
- [ ] API Python para uso programático
- [ ] Plugins para editores (VSCode)
- [ ] Documentación interactiva

---

**⭐ Si te gusta este proyecto, dale una estrella en [GitHub](https://github.com/Keniding/tenty-parser)!**

---

*Powered by Tenty Parser - Created by Keniding*