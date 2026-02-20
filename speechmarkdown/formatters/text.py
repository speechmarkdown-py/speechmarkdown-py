import re
from typing import List, Optional, Union

from speechmarkdown.formatters.base import FormatterBase
from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode


class TextFormatter(FormatterBase):
    """
    Formatter for outputting plain text instead of SSML elements.
    """

    def __init__(self, options: SpeechOptions) -> None:
        """
        Initialize the TextFormatter.

        Args:
            options (SpeechOptions): Setup options for formatting output.
        """
        super().__init__(options)

    def format(self, ast: Union[ASTNode, List[ASTNode]]) -> str:
        """
        Format the AST to basic plain text strings without SSML tags.

        Args:
            ast (Union[ASTNode, List[ASTNode]]): The root node(s) to convert.

        Returns:
            str: Output formatted as plain text.
        """
        lines: List[str] = []
        if isinstance(ast, list):
            self.addArray(ast, lines)
        else:
            self.formatFromAst(ast, lines)

        txt = "".join(lines).strip()
        # replace multiple whitespace with a single space
        txt = re.sub(r"  +", " ", txt)
        return txt

    def formatFromAst(
        self, ast: ASTNode, lines: Optional[List[str]] = None
    ) -> List[str]:
        """
        Process single nodes handling text appending correctly.

        Args:
            ast (ASTNode): Focus AST element to render text.
            lines (Optional[List[str]]): The collector line list.

        Returns:
            List[str]: Refreshed output chunks.
        """
        out_lines: List[str] = lines if lines is not None else []

        if not hasattr(ast, "name"):
            return out_lines

        if ast.name in ("document", "paragraph", "simpleLine"):
            self.processAst(ast.children, out_lines)
            return out_lines

        elif ast.name == "lineEnd":
            out_lines.append(ast.allText)
            return out_lines

        elif ast.name == "emptyLine":
            if getattr(self.options, "preserveEmptyLines", True):
                out_lines.append(ast.allText)
            return out_lines

        elif ast.name in (
            "plainText",
            "plainTextSpecialChars",
            "plainTextEmphasis",
            "plainTextPhone",
            "plainTextModifier",
        ):
            out_lines.append(ast.allText)
            return out_lines

        elif ast.name in ("shortIpa", "shortSub"):
            text_node = next(
                (
                    c
                    for c in ast.children
                    if c.name in ("parenthesized", "plainTextModifier")
                ),
                None,
            )
            text = (
                self.extractParenthesizedText(text_node)
                if text_node and text_node.name == "parenthesized"
                else getattr(text_node, "allText", "")
            )
            if text:
                out_lines.append(text)
            return out_lines

        elif ast.name == "bareIpa":
            phoneme_node = next(
                (c for c in ast.children if c.name == "shortIpaValue"), None
            )
            phoneme = getattr(phoneme_node, "allText", "")
            if phoneme:
                out_lines.append(phoneme)
            return out_lines

        elif ast.name == "audio":
            return out_lines

        else:
            self.processAst(ast.children, out_lines)
            return out_lines

    def extractParenthesizedText(self, node: ASTNode) -> str:
        if not node or not getattr(node, "allText", None) or len(node.allText) < 2:
            return ""
        content = node.allText[1:-1]
        return content.strip()
