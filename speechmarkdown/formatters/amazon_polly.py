from typing import List, Optional

from speechmarkdown.formatters.data.amazon_polly_voices import (
    AMAZON_POLLY_STANDARD_VOICES,
)
from speechmarkdown.formatters.ssml_base import SsmlFormatterBase, TagsObject
from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode


class AmazonPollySsmlFormatter(SsmlFormatterBase):
    def __init__(self, options: SpeechOptions) -> None:
        super().__init__(options)
        self.valid_voices = AMAZON_POLLY_STANDARD_VOICES

        self.modifier_key_to_ssml_tag_mappings.update(
            {
                "whisper": "amazon:effect",
                "timbre": "amazon:effect",
                "cardinal": "say-as",
                "digits": "say-as",
                "drc": "amazon:effect",
                "lang": "lang",
            }
        )

        self.modifier_key_mappings["digits"] = "digits"
        self.modifier_key_mappings["cardinal"] = "cardinal"

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

                if key == "emphasis":
                    tmo.tag(ssml_tag, {"level": value or "moderate"})
                elif key in (
                    "address",
                    "cardinal",
                    "characters",
                    "digits",
                    "expletive",
                    "fraction",
                    "number",
                    "ordinal",
                    "telephone",
                    "unit",
                ):
                    tmo.tag(ssml_tag, {"interpret-as": key})
                elif key == "date":
                    tmo.tag(ssml_tag, {"interpret-as": key, "format": value or "ymd"})
                elif key == "time":
                    tmo.tag(ssml_tag, {"interpret-as": key, "format": value or "hms12"})
                elif key == "whisper":
                    tmo.tag(ssml_tag, {"name": "whispered"})
                elif key == "ipa":
                    tmo.tag(ssml_tag, {"alphabet": key, "ph": value})
                elif key == "sub":
                    tmo.tag(ssml_tag, {"alias": value})
                elif key in ("volume", "rate", "pitch"):
                    tmo.tag(ssml_tag, {key: value or "medium"}, True)
                elif key == "timbre":
                    tmo.tag(ssml_tag, {"vocal-tract-length": value})
                elif key == "lang":
                    tmo.tag(ssml_tag, {"xml:lang": value})
                elif key == "drc":
                    tmo.tag(ssml_tag, {"name": key})
                elif key == "voice":
                    tmo.voice_tag(value)
                elif key in ("excited", "disappointed"):
                    pass

        return tmo

    def get_section_object(self, ast: ASTNode) -> TagsObject:
        so = TagsObject(self)

        for child in ast.children:
            if child.name == "sectionModifierKeyOptionalValue":
                key = child.children[0].allText
                value = child.children[1].allText if len(child.children) == 2 else ""
                ssml_tag = self.modifier_key_to_ssml_tag_mappings.get(key)

                if key == "lang":
                    so.tag(ssml_tag, {"xml:lang": value})
                elif key == "defaults":
                    pass
                elif key == "voice":
                    so.voice_tag(value)
                elif key in ("dj", "newscaster", "excited", "disappointed"):
                    pass

        return so

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
                    "Converted from Speech Markdown to SSML for Amazon Alexa", lines
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
        elif ast.name == "markTag":
            name = ast.children[0].allText
            return self.add_tag_with_attrs(lines, None, "mark", {"name": name})
        elif ast.name == "textModifier":
            tmo = self.get_text_modifier_object(ast)
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
        elif ast.name == "section":
            so = self.get_section_object(ast)
            tags_sorted_asc = sorted(so.tags.keys(), key=lambda t: so.tags[t]["sortId"])
            self.add_section_end_tag(lines)
            self.add_section_start_tag(tags_sorted_asc, so, lines)
            return lines
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
            "shortEmphasisModerate",
            "shortEmphasisStrong",
            "shortEmphasisNone",
            "shortEmphasisReduced",
        ):
            lines.append(ast.allText.replace("+", ""))
            return lines
        elif ast.name in ("plainText", "plainTextSpecialChars"):
            lines.append(ast.allText)
            return lines
        else:
            self.processAst(ast.children, lines)
            return lines
