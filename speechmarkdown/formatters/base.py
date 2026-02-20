from abc import ABC, abstractmethod
from typing import List, Optional, Union

from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode


class FormatterBase(ABC):
    """
    Abstract base class for all Speech Markdown formatters.
    """

    def __init__(self, options: SpeechOptions) -> None:
        """
        Initialize the formatter.

        Args:
            options (SpeechOptions): The options for formatting.
        """
        self.options = options

    @abstractmethod
    def format(self, ast: Union[ASTNode, List[ASTNode]]) -> str:
        """
        Format the given AST into a string.

        Args:
            ast (Union[ASTNode, List[ASTNode]]): The parsed AST node(s).

        Returns:
            str: The formatted result.
        """
        pass

    def addArray(self, ast_list: List[ASTNode], lines: List[str]) -> List[str]:
        """
        Process a list of AST nodes and append output to lines.

        Args:
            ast_list (List[ASTNode]): List of nodes to format.
            lines (List[str]): In-progress output string list.

        Returns:
            List[str]: The updated lines list.
        """
        for child in ast_list:
            self.formatFromAst(child, lines)
        return lines

    def processAst(
        self, ast: Union[ASTNode, List[ASTNode], None], lines: List[str]
    ) -> None:
        """
        Recursively process an AST node or list of nodes.

        Args:
            ast (Union[ASTNode, List[ASTNode], None]): Next node(s) to process.
            lines (List[str]): Shared reference of output lines.
        """
        if ast is None:
            return
        if isinstance(ast, list):
            self.addArray(ast, lines)
        else:
            self.formatFromAst(ast, lines)

    @abstractmethod
    def formatFromAst(
        self, ast: ASTNode, lines: Optional[List[str]] = None
    ) -> List[str]:
        """
        Format a single AST node into output strings.

        Args:
            ast (ASTNode): Target formatting node.
            lines (Optional[List[str]]): Active output lines collection.

        Returns:
            List[str]: Updated output lines collection.
        """
        pass
