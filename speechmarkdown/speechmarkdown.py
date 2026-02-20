from typing import Dict, Any, Optional
from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import SpeechMarkdownParser
from speechmarkdown.formatters.factory import FormatterFactory

class SpeechMarkdown:
    def __init__(self, **kwargs):
        defaults_dict = {
            "includeFormatterComment": False,
            "includeParagraphTag": False,
            "includeSpeakTag": True,
            "platform": "",
            "preserveEmptyLines": True
        }
        merged = {**defaults_dict, **kwargs}
        self.options = SpeechOptions(**merged)
        self._parser = None

    @property
    def parser(self):
        if self._parser is None:
            self._parser = SpeechMarkdownParser()
        return self._parser

    def _get_method_options(self, options: Optional[Dict[str, Any]] = None) -> SpeechOptions:
        if options is None:
            return self.options
        merged = {**self.options.__dict__, **options}
        return SpeechOptions(**merged)

    def to_text(self, speechmarkdown: str, options: Optional[Dict[str, Any]] = None) -> str:
        method_options = self._get_method_options(options)
        ast = self.parser.parse(speechmarkdown)
        formatter = FormatterFactory.create_text_formatter(method_options)
        return formatter.format(ast)

    def to_ssml(self, speechmarkdown: str, options: Optional[Dict[str, Any]] = None) -> str:
        method_options = self._get_method_options(options)
        ast = self.parser.parse(speechmarkdown)
        formatter = FormatterFactory.create_formatter(method_options)
        return formatter.format(ast)

    def to_ast(self, speechmarkdown: str):
        return self.parser.parse(speechmarkdown)

    def to_ast_string(self, speechmarkdown: str) -> str:
        return str(self.parser.parse(speechmarkdown))
