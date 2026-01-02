#!/bin/bash
# deploy.sh - Script automatizado para desplegar paquetes Python a PyPI

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo "================================================"
echo "  Tenty Parser - Deployment Script"
echo "================================================"
echo ""

print_step "Verificando estructura del proyecto..."
if [ ! -f "pyproject.toml" ]; then
    print_error "No se encontro pyproject.toml"
    exit 1
fi
print_success "Estructura correcta"

print_step "Leyendo informacion del proyecto..."
PROJECT_NAME=$(grep -m 1 'name = ' pyproject.toml | cut -d'"' -f2)
CURRENT_VERSION=$(grep -m 1 'version = ' pyproject.toml | cut -d'"' -f2)
echo "   Proyecto: $PROJECT_NAME"
echo "   Version actual: $CURRENT_VERSION"

echo ""
echo "Que deseas hacer?"
echo "1) Build local (solo construir)"
echo "2) Deploy a TestPyPI (prueba)"
echo "3) Deploy a PyPI (produccion)"
echo "4) Actualizar version y deploy completo"
read -p "Selecciona una opcion [1-4]: " OPTION

if [ "$OPTION" = "4" ]; then
    echo ""
    print_step "Actualizacion de version"
    echo "   Version actual: $CURRENT_VERSION"
    read -p "   Nueva version: " NEW_VERSION
    
    if [ -z "$NEW_VERSION" ]; then
        print_error "Version no puede estar vacia"
        exit 1
    fi
    
    sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    
    if [ -f "src/__init__.py" ]; then
        sed -i.bak "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" src/__init__.py
    fi
    
    print_success "Version actualizada a $NEW_VERSION"
    CURRENT_VERSION=$NEW_VERSION
fi

print_step "Limpiando builds anteriores..."
rm -rf dist/ build/ *.egg-info src/*.egg-info
print_success "Limpieza completada"

print_step "Verificando archivos __init__.py..."
mkdir -p src/models src/parsers src/transformers

echo '__version__ = "'$CURRENT_VERSION'"' > src/__init__.py
touch src/models/__init__.py
touch src/parsers/__init__.py
touch src/transformers/__init__.py

print_success "Archivos __init__.py creados"

print_step "Verificando dependencias de build..."
if ! command -v twine &> /dev/null; then
    print_warning "Instalando build y twine..."
    pip install build twine
fi
print_success "Dependencias listas"

print_step "Construyendo paquete..."
python -m build

if [ $? -eq 0 ]; then
    print_success "Build exitoso"
    echo ""
    ls -lh dist/
else
    print_error "Fallo el build"
    exit 1
fi

if [ "$OPTION" = "1" ]; then
    print_success "Build completado"
    exit 0
fi

if [ "$OPTION" = "2" ] || [ "$OPTION" = "4" ]; then
    echo ""
    print_step "Subiendo a TestPyPI..."
    echo "Token en: https://test.pypi.org/manage/account/token/"
    read -p "Continuar? [y/N]: " CONFIRM
    
    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        twine upload --repository testpypi dist/*
        
        if [ $? -eq 0 ]; then
            print_success "Subido a TestPyPI"
            echo "pip install --index-url https://test.pypi.org/simple/ $PROJECT_NAME"
            
            if [ "$OPTION" = "4" ]; then
                read -p "Continuar a PyPI? [y/N]: " CONTINUE_PYPI
                if [ "$CONTINUE_PYPI" != "y" ]; then
                    exit 0
                fi
            else
                exit 0
            fi
        fi
    else
        exit 0
    fi
fi

if [ "$OPTION" = "3" ] || [ "$OPTION" = "4" ]; then
    echo ""
    print_warning "PRODUCCION - PyPI"
    echo "Token en: https://pypi.org/manage/account/token/"
    read -p "Estas seguro? [y/N]: " CONFIRM
    
    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        twine upload dist/*
        
        if [ $? -eq 0 ]; then
            print_success "Publicado en PyPI"
            echo "https://pypi.org/project/$PROJECT_NAME/"
            echo "pip install $PROJECT_NAME"
            
            if [ -d ".git" ]; then
                read -p "Crear tag v$CURRENT_VERSION? [y/N]: " CREATE_TAG
                if [ "$CREATE_TAG" = "y" ]; then
                    git tag -a "v$CURRENT_VERSION" -m "Release v$CURRENT_VERSION"
                    print_success "Tag creado"
                fi
            fi
        fi
    fi
fi

print_success "Completado"