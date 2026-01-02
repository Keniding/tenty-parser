import typer
import json
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.tree import Tree

from .parsers.json_parser import JSONParser
from .transformers.to_structure import StructureTransformer
from .parsers.yaml_parser import YAMLParser
from .transformers.to_toon import TOONTransformer
from .parsers.toon_parser import TOONParser
from .transformers.to_schema import SchemaTransformer

app = typer.Typer(
    name="tenty-parser",
    help="Parse and transform structured data formats (JSON, YAML, TOON)"
)
console = Console()


@app.command()
def parse(
        file: Path = typer.Argument(..., help="Input file to parse (JSON or YAML)"),
        output: Path = typer.Option(None, "--output", "-o", help="Output file (optional)"),
        format: str = typer.Option("tree", "--format", "-f", help="Output format: tree, json, schema, toon"),
        show_examples: bool = typer.Option(True, "--examples/--no-examples", help="Show example values")
):
    """
    Parse a JSON/YAML file and display its structure
    """

    if not file.exists():
        console.print(f"[red]Error:[/red] File '{file}' not found")
        raise typer.Exit(1)

    # Detectar tipo de archivo
    file_ext = file.suffix.lower()

    console.print(f"[cyan]Parsing:[/cyan] {file}")

    try:
        if file_ext in ['.yaml', '.yml']:
            structure = YAMLParser.parse_file(str(file))
        elif file_ext == '.json':
            structure = JSONParser.parse_file(str(file))
        elif file_ext == '.toon':
            structure = TOONParser.parse_file(str(file))
        else:
            console.print(f"[yellow]Warning:[/yellow] Unknown extension, trying JSON parser")
            structure = JSONParser.parse_file(str(file))
    except Exception as e:
        console.print(f"[red]Error parsing file:[/red] {e}")
        raise typer.Exit(1)

    # Generar output según formato
    if format == "tree":
        tree = _build_tree(structure.root)
        console.print(tree)

    elif format == "json":
        simple = StructureTransformer.to_simple_dict(structure)
        syntax = Syntax(json.dumps(simple, indent=2), "json", theme="monokai")
        console.print(syntax)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(simple, f, indent=2)
            console.print(f"[green]✓[/green] Saved to {output}")

    elif format == "schema":
        schema = StructureTransformer.to_schema_like(structure)
        syntax = Syntax(json.dumps(schema, indent=2), "json", theme="monokai")
        console.print(syntax)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2)
            console.print(f"[green]✓[/green] Saved to {output}")

    elif format == "toon":
        # utf-8-sig para manejar BOM
        with open(file, 'r', encoding='utf-8-sig') as f:
            if file_ext in ['.yaml', '.yml']:
                import yaml
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        toon_output = TOONTransformer.to_toon(data)
        syntax = Syntax(toon_output, "yaml", theme="monokai")
        console.print(syntax)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(toon_output)

            console.print(f"[green]✓[/green] Saved to {output}")

    console.print(f"\n[green]✓[/green] Parsing complete!")


def _build_tree(node, name: str = "root") -> Tree:
    """Construye un árbol visual de la estructura"""

    if node.type == "object" and node.children:
        tree = Tree(f"[bold cyan]{name}[/bold cyan] [dim](object)[/dim]")
        for key, child in node.children.items():
            child_tree = _build_tree(child, key)
            tree.add(child_tree)
        return tree

    elif node.type == "array" and node.items:
        tree = Tree(f"[bold cyan]{name}[/bold cyan] [dim](array)[/dim]")
        item_tree = _build_tree(node.items, "items")
        tree.add(item_tree)
        return tree

    else:
        example_str = f" = {node.example}" if node.example is not None else ""
        return Tree(f"[bold cyan]{name}[/bold cyan]: [yellow]{node.type}[/yellow][dim]{example_str}[/dim]")


@app.command()
def convert(
        input_file: Path = typer.Argument(..., help="Input file"),
        output_file: Path = typer.Argument(..., help="Output file"),
        to_format: str = typer.Option("json", "--to", "-t", help="Target format: json, yaml, toon")
):
    """
    Convert between different formats (JSON, YAML, TOON)
    """

    if not input_file.exists():
        console.print(f"[red]Error:[/red] File '{input_file}' not found")
        raise typer.Exit(1)

    console.print(f"[cyan]Converting:[/cyan] {input_file} → {output_file}")

    # Leer archivo de entrada
    try:
        file_ext = input_file.suffix.lower()
        # utf-8-sig para manejar BOM
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            if file_ext in ['.yaml', '.yml']:
                import yaml
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        raise typer.Exit(1)

    # Convertir al formato de salida
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if to_format == "json":
                json.dump(data, f, indent=2)
            elif to_format == "yaml":
                import yaml
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            elif to_format == "toon":
                toon_output = TOONTransformer.to_toon(data)
                f.write(toon_output)
            else:
                console.print(f"[red]Error:[/red] Unknown format '{to_format}'")
                raise typer.Exit(1)

        console.print(f"[green]✓[/green] Converted successfully to {to_format.upper()}")
    except Exception as e:
        console.print(f"[red]Error writing file:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def schema(
        file: Path = typer.Argument(..., help="Input file to generate schema from"),
        output: Path = typer.Option(None, "--output", "-o", help="Output file (optional)"),
        title: str = typer.Option("Generated Schema", "--title", "-t", help="Schema title"),
        format: str = typer.Option("jsonschema", "--format", "-f", help="Schema format: jsonschema, openapi")
):
    """
    Generate JSON Schema or OpenAPI Schema from a file
    """
    if not file.exists():
        console.print(f"[red]Error:[/red] File '{file}' not found")
        raise typer.Exit(1)

    console.print(f"[cyan]Generating schema from:[/cyan] {file}")

    # Parse file
    file_ext = file.suffix.lower()
    try:
        if file_ext in ['.yaml', '.yml']:
            structure = YAMLParser.parse_file(str(file))
        elif file_ext == '.json':
            structure = JSONParser.parse_file(str(file))
        elif file_ext == '.toon':
            structure = TOONParser.parse_file(str(file))
        else:
            structure = JSONParser.parse_file(str(file))
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Generate schema
    if format == "jsonschema":
        schema = SchemaTransformer.to_json_schema(structure, title)
    elif format == "openapi":
        schema = SchemaTransformer.to_openapi_schema(structure, title)
    else:
        console.print(f"[red]Error:[/red] Unknown format '{format}'")
        raise typer.Exit(1)

    # Display
    syntax = Syntax(json.dumps(schema, indent=2), "json", theme="monokai")
    console.print(syntax)

    # Save
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        console.print(f"[green]✓[/green] Saved to {output}")

@app.command()
def version():
    """Show version information"""
    console.print("[cyan]tenty-parser[/cyan] version [green]0.1.1[/green]")


if __name__ == "__main__":
    app()
