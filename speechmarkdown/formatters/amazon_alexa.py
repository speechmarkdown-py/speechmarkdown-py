from typing import Any, Dict, List, Optional

from speechmarkdown.formatters.data.amazon_polly_voices import AMAZON_POLLY_ALL_VOICES
from speechmarkdown.formatters.ssml_base import SsmlFormatterBase, TagsObject
from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode


class AmazonAlexaSsmlFormatter(SsmlFormatterBase):
    def __init__(self, options: SpeechOptions) -> None:
        super().__init__(options)
        self.valid_voices = AMAZON_POLLY_ALL_VOICES
        self.valid_emotion_intensity = ["low", "medium", "high"]

        self.modifier_key_to_ssml_tag_mappings["whisper"] = "amazon:effect"
        self.modifier_key_to_ssml_tag_mappings["lang"] = "lang"
        self.modifier_key_to_ssml_tag_mappings["voice"] = "voice"
        self.modifier_key_to_ssml_tag_mappings["dj"] = "amazon:domain"
        self.modifier_key_to_ssml_tag_mappings["newscaster"] = "amazon:domain"
        self.modifier_key_to_ssml_tag_mappings["excited"] = "amazon:emotion"
        self.modifier_key_to_ssml_tag_mappings["disappointed"] = "amazon:emotion"

    def get_voice_tag_fallback(self, name: str) -> Optional[Dict[str, Any]]:
        if name.lower() == "device":
            return None
        return {"name": name}

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
                    "characters",
                    "expletive",
                    "fraction",
                    "interjection",
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
                elif key == "lang":
                    tmo.tag(ssml_tag, {"xml:lang": value})
                elif key == "voice":
                    tmo.voice_tag(value)
                elif key in ("excited", "disappointed"):
                    intensity = (value or "medium").lower()
                    if intensity in self.valid_emotion_intensity:
                        tmo.tag(ssml_tag, {"name": key, "intensity": intensity})

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
                elif key == "voice":
                    so.voice_tag(value)
                elif key == "dj":
                    so.tag(ssml_tag, {"name": "music"})
                elif key == "newscaster":
                    so.tag(ssml_tag, {"name": "news"})
                elif key == "defaults":
                    pass
                elif key in ("excited", "disappointed"):
                    intensity = (value or "medium").lower()
                    if intensity in self.valid_emotion_intensity:
                        so.tag(ssml_tag, {"name": key, "intensity": intensity})
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
        elif ast.name == "shortEmphasisModerate":
            text = ast.children[0].allText
            return self.add_tag_with_attrs(
                lines, text, "emphasis", {"level": "moderate"}
            )
        elif ast.name == "shortEmphasisStrong":
            text = ast.children[0].allText
            return self.add_tag_with_attrs(lines, text, "emphasis", {"level": "strong"})
        elif ast.name == "shortEmphasisNone":
            text = ast.children[0].allText
            return self.add_tag_with_attrs(lines, text, "emphasis", {"level": "none"})
        elif ast.name == "shortEmphasisReduced":
            text = ast.children[0].allText
            return self.add_tag_with_attrs(
                lines, text, "emphasis", {"level": "reduced"}
            )
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
        elif ast.name == "audio":
            index = 1 if len(ast.children) == 2 else 0
            url = ast.children[index].allText.replace("&", "&amp;")
            return self.add_tag_with_attrs(lines, None, "audio", {"src": url})
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
        elif ast.name in ("plainText", "plainTextSpecialChars"):
            text = (
                self.escape_xml_characters(ast.allText)
                if getattr(self.options, "escapeXmlSymbols", False)
                else ast.allText
            )
            lines.append(text)
            return lines
        else:
            self.processAst(ast.children, lines)
            return lines
