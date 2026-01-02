from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal


class StructureNode(BaseModel):
    """Representa un nodo en la estructura del documento"""
    type: Literal["object", "array", "string", "number", "boolean", "null", "integer", "float"]
    description: Optional[str] = None
    children: Optional[Dict[str, "StructureNode"]] = None  # Para objects
    items: Optional["StructureNode"] = None  # Para arrays
    example: Optional[Any] = None
    required: bool = False
    nullable: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "type": "object",
                "children": {
                    "name": {"type": "string", "example": "John"},
                    "age": {"type": "integer", "example": 30}
                }
            }
        }


class DocumentStructure(BaseModel):
    """Estructura completa del documento"""
    root: StructureNode
    format: Literal["json", "yaml", "toon"] = "json"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convierte a diccionario simple"""
        return self.model_dump(exclude_none=True)

    def to_toon(self) -> str:
        """Convierte a formato TOON"""
        # Implementaremos esto después
        pass
