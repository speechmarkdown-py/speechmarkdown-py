from speechmarkdown.options import SpeechOptions
from speechmarkdown.formatters.ssml_base import SsmlFormatterBase, TagsObject
from speechmarkdown.formatters.data.ibm_watson_voices import IBM_WATSON_ALL_VOICES
from speechmarkdown.parser import ASTNode

class IbmWatsonSsmlFormatter(SsmlFormatterBase):
    def __init__(self, options: SpeechOptions):
        super().__init__(options)
        self.valid_voices = IBM_WATSON_ALL_VOICES

        self.modifier_key_to_ssml_tag_mappings.update({
            'emphasis': 'emphasis',
            'address': 'say-as',
            'number': 'say-as',
            'characters': 'say-as',
            'expletive': None,
            'fraction': 'say-as',
            'interjection': None,
            'ordinal': 'say-as',
            'telephone': 'say-as',
            'unit': 'say-as',
            'time': 'say-as',
            'date': 'say-as',
            'sub': 'sub',
            'ipa': 'phoneme',
            'rate': 'prosody',
            'pitch': 'prosody',
            'volume': 'prosody',
            'whisper': None,
            'voice': 'voice',
            'newscaster': None,
            'excited': None,
            'disappointed': None,
        })

        self.ssml_tag_sort_order = [
            'emphasis', 'say-as', 'prosody', 'voice', 'lang', 'sub', 'phoneme'
        ]

    def get_text_modifier_object(self, ast: ASTNode) -> TagsObject:
        tmo = TagsObject(self)

        for child in ast.children:
            if child.name in ('plainText', 'plainTextSpecialChars', 'plainTextEmphasis', 'plainTextPhone', 'plainTextModifier'):
                tmo.text = child.allText
            elif child.name == 'textModifierKeyOptionalValue':
                key = child.children[0].allText
                key = self.modifier_key_mappings.get(key, key)
                value = child.children[1].allText if len(child.children) == 2 else ''
                ssml_tag = self.modifier_key_to_ssml_tag_mappings.get(key)

                if not ssml_tag:
                    continue

                if key == 'emphasis':
                    tmo.tag(ssml_tag, {'level': value or 'moderate'})
                elif key in ('address', 'fraction', 'ordinal', 'telephone', 'unit'):
                    tmo.tag(ssml_tag, {'interpret-as': key})
                elif key == 'number':
                    tmo.tag(ssml_tag, {'interpret-as': 'cardinal'})
                elif key == 'characters':
                    try:
                        float(tmo.text)
                        attr_value = 'digits'
                    except ValueError:
                        attr_value = 'characters'
                    tmo.tag(ssml_tag, {'interpret-as': attr_value})
                elif key == 'date':
                    tmo.tag(ssml_tag, {'interpret-as': key, 'format': value or 'ymd'})
                elif key == 'time':
                    tmo.tag(ssml_tag, {'interpret-as': key, 'format': value or 'hms12'})
                elif key == 'ipa':
                    tmo.tag(ssml_tag, {'alphabet': key, 'ph': value})
                elif key == 'sub':
                    tmo.tag(ssml_tag, {'alias': value})
                elif key in ('volume', 'rate', 'pitch'):
                    tmo.tag(ssml_tag, {key: value or 'medium'}, True)
                elif key == 'voice':
                    name = self.sentence_case(value or 'device')
                    if name != 'Device':
                        tmo.tag(ssml_tag, {'name': name})

        return tmo

    def get_section_object(self, ast: ASTNode) -> TagsObject:
        so = TagsObject(self)

        for child in ast.children:
            if child.name == 'sectionModifierKeyOptionalValue':
                key = child.children[0].allText
                value = child.children[1].allText if len(child.children) == 2 else ''
                ssml_tag = self.modifier_key_to_ssml_tag_mappings.get(key)

                if not ssml_tag:
                    continue

                if key == 'voice':
                    name = self.sentence_case(value or 'device')
                    if name != 'Device':
                        so.tag(ssml_tag, {'name': name})
        return so

    def formatFromAst(self, ast: ASTNode, lines: list = None) -> list:
        if lines is None:
            lines = []
        if not hasattr(ast, 'name'):
            return lines

        if ast.name == 'document':
            if getattr(self.options, 'includeFormatterComment', False):
                self.add_comment('Converted from Speech Markdown to SSML for IBM Watson Text to Speech', lines)
            if getattr(self.options, 'includeSpeakTag', True):
                return self.add_speak_tag(ast.children, True, False, None, lines)
            self.processAst(ast.children, lines)
            return lines
        elif ast.name == 'paragraph':
            if getattr(self.options, 'includeParagraphTag', False):
                return self.add_tag('p', ast.children, True, False, None, lines)
            self.processAst(ast.children, lines)
            return lines
        elif ast.name == 'shortBreak':
            time = ast.children[0].allText
            return self.add_tag_with_attrs(lines, None, 'break', {'time': time})
        elif ast.name == 'break':
            val = ast.children[0].allText
            attrs = {}
            if ast.children[0].children[0].name == 'breakStrengthValue':
                attrs = {'strength': val}
            elif ast.children[0].children[0].name == 'time':
                attrs = {'time': val}
            return self.add_tag_with_attrs(lines, None, 'break', attrs)
        elif ast.name in ('shortEmphasisModerate', 'shortEmphasisStrong', 'shortEmphasisNone', 'shortEmphasisReduced'):
            text = ast.children[0].allText
            if text:
                lines.append(text)
            return lines
        elif ast.name == 'textModifier':
            tmo = self.get_text_modifier_object(ast)
            return self.apply_tags_object(tmo, lines)
        elif ast.name == 'shortIpa':
            tmo = self.get_short_ipa_object(ast)
            return self.apply_tags_object(tmo, lines)
        elif ast.name == 'bareIpa':
            tmo = self.get_short_ipa_object(ast, 'ipa')
            return self.apply_tags_object(tmo, lines)
        elif ast.name == 'shortSub':
            tmo = self.get_short_sub_object(ast)
            return self.apply_tags_object(tmo, lines)
        elif ast.name == 'audio':
            index = 1 if len(ast.children) == 2 else 0
            url = ast.children[index].allText.replace('&', '&amp;')
            return self.add_tag_with_attrs(lines, None, 'audio', {'src': url}, False)
        elif ast.name == 'simpleLine':
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
            text = self.escape_xml_characters(ast.allText) if getattr(self.options, 'escapeXmlSymbols', False) else ast.allText
            lines.append(text)
            return lines
        elif ast.name == 'section':
            so = self.get_section_object(ast)
            tags_sorted_asc = sorted(so.tags.keys(), key=lambda t: so.tags[t]['sortId'])
            self.add_section_end_tag(lines)
            self.add_section_start_tag(tags_sorted_asc, so, lines)
            return lines
        else:
            self.processAst(ast.children, lines)
            return lines
