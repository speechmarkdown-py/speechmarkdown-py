import re
from typing import List, Optional

from speechmarkdown.options import SpeechOptions
from speechmarkdown.formatters.base import FormatterBase
from speechmarkdown.parser import ASTNode

class TextFormatter(FormatterBase):
    def __init__(self, options: SpeechOptions):
        super().__init__(options)

    def format(self, ast: ASTNode) -> str:
        lines = self.formatFromAst(ast, [])
        txt = "".join(lines).strip()
        # replace multiple whitespace with a single space
        txt = re.sub(r'  +', ' ', txt)
        return txt

    def formatFromAst(self, ast: ASTNode, lines: Optional[List[str]] = None) -> List[str]:
        if lines is None:
            lines = []

        if not hasattr(ast, 'name'):
            return lines

        if ast.name in ('document', 'paragraph', 'simpleLine'):
            self.processAst(ast.children, lines)
            return lines

        elif ast.name == 'lineEnd':
            lines.append(ast.allText)
            return lines

        elif ast.name == 'emptyLine':
            if getattr(self.options, 'preserveEmptyLines', True):
                lines.append(ast.allText)
            return lines

        elif ast.name in ('plainText', 'plainTextSpecialChars', 'plainTextEmphasis', 'plainTextPhone', 'plainTextModifier'):
            lines.append(ast.allText)
            return lines

        elif ast.name in ('shortIpa', 'shortSub'):
            text_node = next((c for c in ast.children if c.name in ('parenthesized', 'plainTextModifier')), None)
            text = self.extractParenthesizedText(text_node) if text_node and text_node.name == 'parenthesized' else getattr(text_node, 'allText', '')
            if text:
                lines.append(text)
            return lines

        elif ast.name == 'bareIpa':
            phoneme_node = next((c for c in ast.children if c.name == 'shortIpaValue'), None)
            phoneme = getattr(phoneme_node, 'allText', '')
            if phoneme:
                lines.append(phoneme)
            return lines

        elif ast.name == 'audio':
            return lines

        else:
            self.processAst(ast.children, lines)
            return lines

    def extractParenthesizedText(self, node: ASTNode) -> str:
        if not node or not getattr(node, 'allText', None) or len(node.allText) < 2:
            return ''
        content = node.allText[1:-1]
        return content.strip()
