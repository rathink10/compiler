from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class Program:
    statements: List[Any]

@dataclass
class Block:
    statements: List[Any]

@dataclass
class VarDecl:
    type_name:   str
    name:        str
    initializer: Optional[Any] = None

@dataclass
class Assignment:
    name:  str
    value: Any

@dataclass
class UpdateStmt:
    """Represents i++ or i-- as a standalone statement."""
    name: str
    op:   str = "+"     # "+" for ++, "-" for --

@dataclass
class CoutStmt:
    """cout << expr1 << expr2 << ..."""
    values: List[Any]

@dataclass
class IfStmt:
    condition:  Any
    then_block: Block
    else_block: Optional[Block] = None

@dataclass
class WhileStmt:
    condition: Any
    body:      Block

@dataclass
class DoWhileStmt:
    body:      Block
    condition: Any

@dataclass
class ForStmt:
    init:      Any
    condition: Any
    update:    Any
    body:      Block

@dataclass
class BinaryOp:
    left:  Any
    op:    str
    right: Any

@dataclass
class UnaryOp:
    op:      str
    operand: Any

@dataclass
class Literal:
    value:     Any
    type_name: str

@dataclass
class Identifier:
    name: str
