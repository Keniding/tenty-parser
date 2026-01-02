import typer
import json
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.tree import Tree

from .parsers.json_parser import JSONParser
from .transformers.to_structure import StructureTransformer

app = typer.Typer(
    name="tenty-parser",
    help="Parse and transform structured data formats (JSON, YAML, TOON)"
)
console = Console()


@app.command()
def parse(
        file: Path = typer.Argument(..., help="Input file to parse"),
        output: Path = typer.Option(None, "--output", "-o", help="Output file (optional)"),
        format: str = typer.Option("tree", "--format", "-f", help="Output format: tree, json, schema")
):
    """
    Parse a JSON file and display its structure
    """

    if not file.exists():
        console.print(f"[red]Error:[/red] File '{file}' not found")
        raise typer.Exit(1)

    # Parse el archivo
    console.print(f"[cyan]Parsing:[/cyan] {file}")

    try:
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
            with open(output, 'w') as f:
                json.dump(simple, f, indent=2)
            console.print(f"[green]✓[/green] Saved to {output}")

    elif format == "schema":
        schema = StructureTransformer.to_schema_like(structure)
        syntax = Syntax(json.dumps(schema, indent=2), "json", theme="monokai")
        console.print(syntax)

        if output:
            with open(output, 'w') as f:
                json.dump(schema, f, indent=2)
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
def version():
    """Show version information"""
    console.print("[cyan]tenty-parser[/cyan] version [green]0.1.0[/green]")


if __name__ == "__main__":
    app()
