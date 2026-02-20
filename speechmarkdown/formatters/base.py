from abc import ABC, abstractmethod
from typing import List, Union

from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode

class FormatterBase(ABC):
    def __init__(self, options: SpeechOptions):
        self.options = options

    @abstractmethod
    def format(self, ast: Union[ASTNode, List[ASTNode]]) -> str:
        pass

    def addArray(self, ast_list: List[ASTNode], lines: List[str]) -> List[str]:
        for child in ast_list:
            self.formatFromAst(child, lines)
        return lines

    def processAst(self, ast: Union[ASTNode, List[ASTNode], None], lines: List[str]) -> None:
        if ast is None:
            return
        if isinstance(ast, list):
            self.addArray(ast, lines)
        else:
            self.formatFromAst(ast, lines)

    @abstractmethod
    def formatFromAst(self, ast: ASTNode, lines: List[str] = None) -> List[str]:
        pass
