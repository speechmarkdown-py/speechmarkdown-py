import re
from typing import Any, Dict, List, Optional, Union

from speechmarkdown.formatters.base import FormatterBase
from speechmarkdown.options import SpeechOptions
from speechmarkdown.parser import ASTNode


class TagsObject:
    """Helper representing a tag object structure resolving nested values."""

    def __init__(self, base: "SsmlFormatterBase") -> None:
        self.base = base
        self.tags: Dict[str, Any] = {}
        self.text: str = ""

    def tag(
        self,
        tag_name: Optional[str],
        attrs: Optional[Dict[str, Any]],
        augment: bool = False,
    ) -> None:
        if tag_name is None:
            return
        sort_id = (
            self.base.ssml_tag_sort_order.index(tag_name)
            if tag_name in self.base.ssml_tag_sort_order
            else 999
        )
        if tag_name not in self.tags:
            self.tags[tag_name] = {"sortId": sort_id, "attrs": None}

        if augment:
            current_attrs = self.tags[tag_name]["attrs"] or {}
            combined = {**current_attrs}
            if attrs:
                combined.update(attrs)
            self.tags[tag_name]["attrs"] = combined
        else:
            self.tags[tag_name]["attrs"] = attrs

    def voice_tag_named(self, voices: Optional[Dict[str, Any]], name: str) -> bool:
        if voices and name in voices:
            info = voices[name]
            if not isinstance(info, dict):
                info = {"voice": {"name": name}}

            metadata_keys = [
                "id",
                "displayName",
                "languages",
                "language",
                "locale",
                "isHD",
            ]
            for tag, attributes in info.items():
                if tag not in metadata_keys:
                    self.tag(tag, attributes)
            return True
        return False

    def voice_tag(self, value: Optional[str]) -> None:
        raw_name = (value or "").strip()
        normalized_name = raw_name.lower()
        default_name = raw_name or "device"
        sentence_case_name = self.base.sentence_case(normalized_name or default_name)

        option_candidates = [raw_name]
        if normalized_name and normalized_name != raw_name:
            option_candidates.append(normalized_name)
        if sentence_case_name and sentence_case_name not in option_candidates:
            option_candidates.append(sentence_case_name)

        voices_opts = getattr(self.base.options, "voices", None)
        for candidate in option_candidates:
            if candidate and self.voice_tag_named(voices_opts, candidate):
                return

        valid_candidates = []
        if normalized_name:
            valid_candidates.append(normalized_name)
        if raw_name and raw_name != normalized_name:
            valid_candidates.append(raw_name)
        if sentence_case_name and sentence_case_name not in valid_candidates:
            valid_candidates.append(sentence_case_name)

        for candidate in valid_candidates:
            if self.voice_tag_named(self.base.valid_voices, candidate):
                return

        fallback = self.base.get_voice_tag_fallback(sentence_case_name or default_name)
        if fallback:
            self.tag("voice", fallback)


class SsmlFormatterBase(FormatterBase):
    XML_ESCAPE_MAPPING: Dict[str, str] = {
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
    }
    XML_UNESCAPE_MAPPING: Dict[str, str] = {
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&quot;": '"',
        "&apos;": "'",
    }

    def __init__(self, options: SpeechOptions) -> None:
        super().__init__(options)
        self.valid_voices: Dict[str, Any] = {}
        self.section_tags: List[str] = []

        self.modifier_key_mappings = {
            "chars": "characters",
            "cardinal": "number",
            "digits": "characters",
            "bleep": "expletive",
            "phone": "telephone",
            "vol": "volume",
        }

        self.ssml_tag_sort_order = [
            "emphasis",
            "say-as",
            "prosody",
            "amazon:domain",
            "amazon:effect",
            "amazon:emotion",
            "voice",
            "lang",
            "sub",
            "phoneme",
        ]

        self.modifier_key_to_ssml_tag_mappings = {
            "emphasis": "emphasis",
            "address": "say-as",
            "number": "say-as",
            "characters": "say-as",
            "expletive": "say-as",
            "fraction": "say-as",
            "interjection": "say-as",
            "ordinal": "say-as",
            "telephone": "say-as",
            "unit": "say-as",
            "time": "say-as",
            "date": "say-as",
            "whisper": None,
            "sub": "sub",
            "ipa": "phoneme",
            "rate": "prosody",
            "pitch": "prosody",
            "volume": "prosody",
            "drc": None,
            "timbre": None,
            "lang": None,
            "voice": None,
            "dj": None,
            "defaults": None,
            "newscaster": None,
            "excited": None,
            "disappointed": None,
        }

    def format(self, ast: Union[ASTNode, List[ASTNode]]) -> str:
        lines: List[str] = []
        if isinstance(ast, list):
            self.addArray(ast, lines)
        else:
            self.formatFromAst(ast, lines)
        return "".join(lines)

    def add_section_start_tag(
        self, tags_sorted_asc: List[str], so: TagsObject, lines: List[str]
    ) -> None:
        self.section_tags = tags_sorted_asc[::-1]
        for tag in tags_sorted_asc:
            attrs = so.tags[tag]["attrs"]
            lines.append("\n")
            lines.append(self.start_tag(tag, attrs, False))

    def add_section_end_tag(self, lines: List[str]) -> None:
        if self.section_tags:
            for tag in self.section_tags:
                lines.append(self.end_tag(tag, False))
                lines.append("\n")

    def add_tag(
        self,
        tag: str,
        ast: Union[ASTNode, List[ASTNode]],
        new_line: bool,
        new_line_after_end: bool,
        attr: Optional[Dict[str, Any]],
        lines: List[str],
    ) -> List[str]:
        lines.append(self.start_tag(tag, attr, new_line))
        self.processAst(ast, lines)
        lines.append(self.end_tag(tag, new_line))
        if new_line_after_end:
            lines.append("\n")
        return lines

    def apply_tags_object(self, tmo: TagsObject, lines: List[str]) -> List[str]:
        tags_sorted_desc = sorted(
            tmo.tags.keys(), key=lambda t: tmo.tags[t]["sortId"], reverse=True
        )
        inner = tmo.text
        for tag in tags_sorted_desc:
            attrs = tmo.tags[tag]["attrs"]
            inner = self.get_tag_with_attrs(inner, tag, attrs)
        lines.append(inner)
        return lines

    def extract_parenthesized_text(self, node: ASTNode) -> str:
        if not node or not getattr(node, "allText", None) or len(node.allText) < 2:
            return ""
        return node.allText[1:-1].strip()

    def get_short_ipa_object(self, ast: ASTNode, fallback_text: str = "") -> TagsObject:
        tmo = TagsObject(self)
        text_node = next(
            (
                c
                for c in ast.children
                if c.name in ("parenthesized", "plainTextModifier")
            ),
            None,
        )
        extracted_text = (
            self.extract_parenthesized_text(text_node)
            if text_node and text_node.name == "parenthesized"
            else getattr(text_node, "allText", "")
        )
        tmo.text = extracted_text or fallback_text or ""
        phoneme_node = next(
            (c for c in ast.children if c.name == "shortIpaValue"), None
        )
        phoneme = getattr(phoneme_node, "allText", "")
        if phoneme:
            tmo.tag("phoneme", {"alphabet": "ipa", "ph": phoneme})
        return tmo

    def get_short_sub_object(self, ast: ASTNode) -> TagsObject:
        tmo = TagsObject(self)
        text_node = next(
            (
                c
                for c in ast.children
                if c.name in ("parenthesized", "plainTextModifier")
            ),
            None,
        )
        tmo.text = (
            self.extract_parenthesized_text(text_node)
            if text_node and text_node.name == "parenthesized"
            else getattr(text_node, "allText", "")
        )
        alias_node = next((c for c in ast.children if c.name == "shortSubValue"), None)
        alias = getattr(alias_node, "allText", "").strip()
        if alias:
            tmo.tag("sub", {"alias": alias})
        return tmo

    def add_speak_tag(
        self,
        ast: Union[ASTNode, List[ASTNode]],
        new_line: bool,
        new_line_after_end: bool,
        attr: Optional[Dict[str, Any]],
        lines: List[str],
    ) -> List[str]:
        lines.append(self.start_tag("speak", attr, new_line))
        self.processAst(ast, lines)
        self.add_section_end_tag(lines)
        lines.append(self.end_tag("speak", new_line))
        if new_line_after_end:
            lines.append("\n")
        return lines

    def add_comment(self, comment_text: str, lines: List[str]) -> List[str]:
        lines.append(f"<!-- {comment_text} -->\n")
        return lines

    def start_tag(
        self, tag: str, attr: Optional[Dict[str, Any]], new_line: bool = False
    ) -> str:
        attr_str = ""
        if attr:
            attr_str = " " + " ".join(
                f'{k}="{self.escape_xml_characters(str(v))}"' for k, v in attr.items()
            )
        return f"<{tag}{attr_str}>" + ("\n" if new_line else "")

    def end_tag(self, tag: str, new_line: bool = False) -> str:
        return ("\n" if new_line else "") + f"</{tag}>"

    def void_tag(self, tag: str, attr: Optional[Dict[str, Any]]) -> str:
        attr_str = ""
        if attr:
            attr_str = " " + " ".join(
                f'{k}="{self.escape_xml_characters(str(v))}"' for k, v in attr.items()
            )
        return f"<{tag}{attr_str}/>"

    def add_tag_with_attrs(
        self,
        lines: List[str],
        text: Optional[str],
        tag: str,
        attrs: Optional[Dict[str, Any]],
        force_end_tag: bool = False,
    ) -> List[str]:
        if text or force_end_tag:
            lines.append(self.start_tag(tag, attrs))
            if text:
                lines.append(text)
            lines.append(self.end_tag(tag, False))
        else:
            lines.append(self.void_tag(tag, attrs))
        return lines

    def get_tag_with_attrs(
        self, text: Optional[str], tag: str, attrs: Optional[Dict[str, Any]]
    ) -> str:
        if text:
            return self.start_tag(tag, attrs) + text + self.end_tag(tag, False)
        return self.void_tag(tag, attrs)

    def sentence_case(self, text: str) -> str:
        if not text:
            return text

        def replacer(match: Any) -> str:
            return str(match.group(0).upper())

        return str(re.sub(r"[a-z]", replacer, text, count=1).strip())

    def escape_xml_characters(self, unescaped: str) -> str:
        rev_pattern = "|".join(re.escape(k) for k in self.XML_UNESCAPE_MAPPING.keys())
        reversed_str = re.sub(
            rev_pattern, lambda m: self.XML_UNESCAPE_MAPPING[m.group(0)], unescaped
        )
        pattern = "".join(re.escape(k) for k in self.XML_ESCAPE_MAPPING.keys())
        escaped = re.sub(
            f"[{pattern}]", lambda m: self.XML_ESCAPE_MAPPING[m.group(0)], reversed_str
        )
        return escaped

    def get_voice_tag_fallback(self, name: str) -> Optional[Dict[str, Any]]:
        return None
