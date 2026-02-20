from typing import Any, Dict, Optional

from speechmarkdown.formatters.factory import FormatterFactory
from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode, SpeechMarkdownParser


class SpeechMarkdown:
    """
    Main class for converting Speech Markdown to text, SSML, or AST.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the SpeechMarkdown instance.

        Args:
            **kwargs: Configuration options for formatting.
        """
        defaults_dict = {
            "includeFormatterComment": False,
            "includeParagraphTag": False,
            "includeSpeakTag": True,
            "platform": "",
            "preserveEmptyLines": True,
        }
        merged: Dict[str, Any] = {**defaults_dict, **kwargs}
        self.options = SpeechOptions(**merged)
        self._parser: Optional[SpeechMarkdownParser] = None

    @property
    def parser(self) -> SpeechMarkdownParser:
        """
        Lazily initialize and return the Speech Markdown parser.

        Returns:
            SpeechMarkdownParser: The parser instance.
        """
        if self._parser is None:
            self._parser = SpeechMarkdownParser()
        return self._parser

    def _get_method_options(
        self, options: Optional[Dict[str, Any]] = None
    ) -> SpeechOptions:
        """
        Get options merged with instance defaults.

        Args:
            options (Optional[Dict[str, Any]]): Method-specific options.

        Returns:
            SpeechOptions: The merged options.
        """
        if options is None:
            return self.options
        merged = {**self.options.__dict__, **options}
        return SpeechOptions(**merged)

    def to_text(
        self, speechmarkdown: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convert Speech Markdown to plain text.

        Args:
            speechmarkdown (str): The Speech Markdown input.
            options (Optional[Dict[str, Any]]): Specific formatting options.

        Returns:
            str: The converted plain text.
        """
        method_options = self._get_method_options(options)
        ast_obj = self.parser.parse(speechmarkdown)
        formatter = FormatterFactory.create_text_formatter(method_options)
        return str(formatter.format(ast_obj))

    def to_ssml(
        self, speechmarkdown: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convert Speech Markdown to SSML.

        Args:
            speechmarkdown (str): The Speech Markdown input.
            options (Optional[Dict[str, Any]]): Specific formatting options.

        Returns:
            str: The formatted SSML text.
        """
        method_options = self._get_method_options(options)
        ast_obj = self.parser.parse(speechmarkdown)
        formatter = FormatterFactory.create_formatter(method_options)
        return str(formatter.format(ast_obj))

    def to_ast(self, speechmarkdown: str) -> ASTNode:
        """
        Convert Speech Markdown into an Abstract Syntax Tree (AST).

        Args:
            speechmarkdown (str): The Speech Markdown input.

        Returns:
            ASTNode: The root node of the parsed AST.
        """
        return self.parser.parse(speechmarkdown)

    def to_ast_string(self, speechmarkdown: str) -> str:
        """
        Convert Speech Markdown to the string representation of its AST.

        Args:
            speechmarkdown (str): The Speech Markdown input.

        Returns:
            str: The string representation of the parsed AST.
        """
        return str(self.parser.parse(speechmarkdown))
