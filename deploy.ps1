# deploy.ps1 - Script automatizado para desplegar paquetes Python a PyPI
# Uso: .\deploy.ps1

$ErrorActionPreference = "Stop"

function Print-Step { param($msg) Write-Host "[STEP] $msg" -ForegroundColor Blue }
function Print-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Print-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Print-Warning { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }

Write-Host "================================================"
Write-Host "  Tenty Parser - Deployment Script"
Write-Host "================================================"
Write-Host ""

Print-Step "Verificando estructura del proyecto..."
if (-not (Test-Path "pyproject.toml")) {
    Print-Error "No se encontro pyproject.toml"
    exit 1
}
Print-Success "Estructura correcta"

Print-Step "Leyendo informacion del proyecto..."
$content = Get-Content "pyproject.toml" -Raw
$PROJECT_NAME = ([regex]::Match($content, 'name = "([^"]+)"')).Groups[1].Value
$CURRENT_VERSION = ([regex]::Match($content, 'version = "([^"]+)"')).Groups[1].Value
Write-Host "   Proyecto: $PROJECT_NAME"
Write-Host "   Version actual: $CURRENT_VERSION"

Write-Host ""
Write-Host "Que deseas hacer?"
Write-Host "1) Build local (solo construir)"
Write-Host "2) Deploy a TestPyPI (prueba)"
Write-Host "3) Deploy a PyPI (produccion)"
Write-Host "4) Actualizar version y deploy completo"
$OPTION = Read-Host "Selecciona una opcion [1-4]"

if ($OPTION -eq "4") {
    Write-Host ""
    Print-Step "Actualizacion de version"
    Write-Host "   Version actual: $CURRENT_VERSION"
    $NEW_VERSION = Read-Host "   Nueva version"
    
    if ([string]::IsNullOrWhiteSpace($NEW_VERSION)) {
        Print-Error "Version no puede estar vacia"
        exit 1
    }
    
    (Get-Content "pyproject.toml") -replace "version = `"$CURRENT_VERSION`"", "version = `"$NEW_VERSION`"" | Set-Content "pyproject.toml"
    
    if (Test-Path "src\__init__.py") {
        (Get-Content "src\__init__.py") -replace "__version__ = `"$CURRENT_VERSION`"", "__version__ = `"$NEW_VERSION`"" | Set-Content "src\__init__.py"
    }
    
    Print-Success "Version actualizada a $NEW_VERSION"
    $CURRENT_VERSION = $NEW_VERSION
}

Print-Step "Limpiando builds anteriores..."
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
Print-Success "Limpieza completada"

Print-Step "Verificando archivos __init__.py..."
New-Item -ItemType Directory -Force -Path "src\models", "src\parsers", "src\transformers" | Out-Null

@"
__version__ = "$CURRENT_VERSION"
"@ | Out-File -FilePath "src\__init__.py" -Encoding UTF8

New-Item -ItemType File -Force -Path "src\models\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "src\parsers\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "src\transformers\__init__.py" | Out-Null

Print-Success "Archivos __init__.py creados"

Print-Step "Verificando dependencias de build..."
$hasTwine = Get-Command twine -ErrorAction SilentlyContinue
if (-not $hasTwine) {
    Print-Warning "Instalando build y twine..."
    pip install build twine
}
Print-Success "Dependencias listas"

Print-Step "Construyendo paquete..."
python -m build

if ($LASTEXITCODE -eq 0) {
    Print-Success "Build exitoso"
    Write-Host ""
    Get-ChildItem dist\ | Format-Table Name, Length
} else {
    Print-Error "Fallo el build"
    exit 1
}

if ($OPTION -eq "1") {
    Print-Success "Build completado"
    exit 0
}

if ($OPTION -eq "2" -or $OPTION -eq "4") {
    Write-Host ""
    Print-Step "Subiendo a TestPyPI..."
    Write-Host "Token en: https://test.pypi.org/manage/account/token/"
    $CONFIRM = Read-Host "Continuar? [y/N]"
    
    if ($CONFIRM -eq "y" -or $CONFIRM -eq "Y") {
        twine upload --repository testpypi dist/*
        
        if ($LASTEXITCODE -eq 0) {
            Print-Success "Subido a TestPyPI"
            Write-Host "pip install --index-url https://test.pypi.org/simple/ $PROJECT_NAME"
            
            if ($OPTION -eq "4") {
                $CONTINUE_PYPI = Read-Host "Continuar a PyPI? [y/N]"
                if ($CONTINUE_PYPI -ne "y" -and $CONTINUE_PYPI -ne "Y") {
                    exit 0
                }
            } else {
                exit 0
            }
        }
    } else {
        exit 0
    }
}

if ($OPTION -eq "3" -or $OPTION -eq "4") {
    Write-Host ""
    Print-Warning "PRODUCCION - PyPI"
    Write-Host "Token en: https://pypi.org/manage/account/token/"
    $CONFIRM = Read-Host "Estas seguro? [y/N]"
    
    if ($CONFIRM -eq "y" -or $CONFIRM -eq "Y") {
        twine upload dist/*
        
        if ($LASTEXITCODE -eq 0) {
            Print-Success "Publicado en PyPI"
            Write-Host "https://pypi.org/project/$PROJECT_NAME/"
            Write-Host "pip install $PROJECT_NAME"
            
            if (Test-Path ".git") {
                $CREATE_TAG = Read-Host "Crear tag v$CURRENT_VERSION? [y/N]"
                if ($CREATE_TAG -eq "y" -or $CREATE_TAG -eq "Y") {
                    git tag -a "v$CURRENT_VERSION" -m "Release v$CURRENT_VERSION"
                    Print-Success "Tag creado"
                }
            }
        }
    }
}

Print-Success "Completado"