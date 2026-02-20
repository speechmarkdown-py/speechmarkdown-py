from typing import List, Optional

from speechmarkdown.formatters.ssml_base import SsmlFormatterBase, TagsObject
from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode


class SamsungBixbySsmlFormatter(SsmlFormatterBase):
    def __init__(self, options: SpeechOptions) -> None:
        super().__init__(options)

        self.modifier_key_to_ssml_tag_mappings.update(
            {
                "emphasis": None,
                "address": None,
                "number": "say-as",
                "characters": "say-as",
                "expletive": None,
                "fraction": "say-as",
                "interjection": None,
                "ordinal": "say-as",
                "telephone": None,
                "unit": None,
                "time": None,
                "date": None,
                "sub": "sub",
                "ipa": None,
                "rate": "prosody",
                "pitch": "prosody",
                "volume": "prosody",
                "whisper": "prosody",
            }
        )

    def get_text_modifier_object(self, ast: ASTNode) -> TagsObject:
        tmo = TagsObject(self)

        for child in ast.children:
            if child.name in (
                "plainText",
                "plainTextSpecialChars",
                "plainTextEmphasis",
                "plainTextPhone",
                "plainTextModifier",
            ):
                tmo.text = child.allText
            elif child.name == "textModifierKeyOptionalValue":
                key = child.children[0].allText
                key = self.modifier_key_mappings.get(key, key)
                value = child.children[1].allText if len(child.children) == 2 else ""
                ssml_tag = self.modifier_key_to_ssml_tag_mappings.get(key)

                if key in ("fraction", "ordinal"):
                    tmo.tag(ssml_tag, {"interpret-as": key})
                elif key == "number":
                    tmo.tag(ssml_tag, {"interpret-as": "cardinal"})
                elif key == "characters":
                    try:
                        float(tmo.text)
                        attr_value = "digits"
                    except ValueError:
                        attr_value = "spell-out"
                    tmo.tag(ssml_tag, {"interpret-as": attr_value})
                elif key == "whisper":
                    tmo.tag(ssml_tag, {"volume": "x-soft", "rate": "slow"})
                elif key == "sub":
                    tmo.tag(ssml_tag, {"alias": value})
                elif key in ("volume", "rate", "pitch"):
                    tmo.tag(ssml_tag, {key: value or "medium"}, True)

        return tmo

    def formatFromAst(
        self, ast: ASTNode, lines: Optional[List[str]] = None
    ) -> List[str]:
        if lines is None:
            lines = []
        if not hasattr(ast, "name"):
            return lines

        if ast.name == "document":
            if getattr(self.options, "includeFormatterComment", False):
                self.add_comment(
                    "Converted from Speech Markdown to SSML for Samsung Bixby", lines
                )
            if getattr(self.options, "includeSpeakTag", True):
                return self.add_speak_tag(ast.children, True, False, None, lines)
            self.processAst(ast.children, lines)
            return lines
        elif ast.name == "paragraph":
            if getattr(self.options, "includeParagraphTag", False):
                return self.add_tag("p", ast.children, True, False, None, lines)
            self.processAst(ast.children, lines)
            return lines
        elif ast.name == "shortBreak":
            time = ast.children[0].allText
            return self.add_tag_with_attrs(lines, None, "break", {"time": time})
        elif ast.name == "break":
            val = ast.children[0].allText
            attrs = {}
            if ast.children[0].children[0].name == "breakStrengthValue":
                attrs = {"strength": val}
            elif ast.children[0].children[0].name == "time":
                attrs = {"time": val}
            return self.add_tag_with_attrs(lines, None, "break", attrs)
        elif ast.name in (
            "shortEmphasisModerate",
            "shortEmphasisStrong",
            "shortEmphasisNone",
            "shortEmphasisReduced",
        ):
            text = ast.children[0].allText
            if text:
                lines.append(text)
            return lines
        elif ast.name == "textModifier":
            tmo = self.get_text_modifier_object(ast)
            if getattr(tmo, "textOnly", False):
                lines.append(tmo.text)
                return lines
            return self.apply_tags_object(tmo, lines)
        elif ast.name == "shortIpa":
            tmo = self.get_short_ipa_object(ast)
            return self.apply_tags_object(tmo, lines)
        elif ast.name == "bareIpa":
            tmo = self.get_short_ipa_object(ast, "ipa")
            return self.apply_tags_object(tmo, lines)
        elif ast.name == "shortSub":
            tmo = self.get_short_sub_object(ast)
            return self.apply_tags_object(tmo, lines)
        elif ast.name == "audio":
            index = 1 if len(ast.children) == 2 else 0
            url = ast.children[index].allText.replace("&", "&amp;")
            return self.add_tag_with_attrs(lines, None, "audio", {"src": url}, True)
        elif ast.name == "simpleLine":
            self.processAst(ast.children, lines)
            return lines
        elif ast.name == "lineEnd":
            lines.append(ast.allText)
            return lines
        elif ast.name == "emptyLine":
            if getattr(self.options, "preserveEmptyLines", True):
                lines.append(ast.allText)
            return lines
        elif ast.name in (
            "plainText",
            "plainTextSpecialChars",
            "plainTextEmphasis",
            "plainTextPhone",
            "plainTextModifier",
        ):
            lines.append(ast.allText)
            return lines
        else:
            self.processAst(ast.children, lines)
            return lines
