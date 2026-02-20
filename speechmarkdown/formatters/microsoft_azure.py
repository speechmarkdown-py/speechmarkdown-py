import re
from speechmarkdown.options import SpeechOptions
from speechmarkdown.formatters.ssml_base import SsmlFormatterBase, TagsObject
from speechmarkdown.formatters.data.microsoft_azure_voices import MICROSOFT_AZURE_ALL_VOICES
from speechmarkdown.parser import ASTNode

class MicrosoftAzureSsmlFormatter(SsmlFormatterBase):
    def __init__(self, options: SpeechOptions):
        super().__init__(options)
        self.valid_voices = MICROSOFT_AZURE_ALL_VOICES

        self.min_style_degree = 0.01
        self.max_style_degree = 2.0

        self.valid_roles = [
            'Girl', 'Boy', 'YoungAdultFemale', 'YoungAdultMale',
            'OlderAdultFemale', 'OlderAdultMale', 'SeniorFemale', 'SeniorMale'
        ]

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
            'unit': None,
            'time': 'say-as',
            'date': 'say-as',
            'sub': 'sub',
            'ipa': 'phoneme',
            'rate': 'prosody',
            'pitch': 'prosody',
            'volume': 'prosody',
            'whisper': 'prosody',
            'voice': 'voice',
            'lang': 'lang',
            'style': 'mstts:express-as',
            'role': 'mstts:express-as',
            'newscaster': 'mstts:express-as',
            'excited': 'mstts:express-as',
            'disappointed': 'mstts:express-as',
            'friendly': 'mstts:express-as',
            'cheerful': 'mstts:express-as',
            'sad': 'mstts:express-as',
            'angry': 'mstts:express-as',
            'fearful': 'mstts:express-as',
            'empathetic': 'mstts:express-as',
            'calm': 'mstts:express-as',
            'lyrical': 'mstts:express-as',
            'hopeful': 'mstts:express-as',
            'terrified': 'mstts:express-as',
            'shouting': 'mstts:express-as',
            'whispering': 'mstts:express-as',
            'unfriendly': 'mstts:express-as',
            'gentle': 'mstts:express-as',
            'serious': 'mstts:express-as',
            'depressed': 'mstts:express-as',
            'embarrassed': 'mstts:express-as',
            'disgruntled': 'mstts:express-as',
            'envious': 'mstts:express-as',
            'affectionate': 'mstts:express-as',
            'assistant': 'mstts:express-as',
            'chat': 'mstts:express-as',
            'customerservice': 'mstts:express-as',
            'poetry-reading': 'mstts:express-as',
            'narration-professional': 'mstts:express-as',
            'narration-relaxed': 'mstts:express-as',
            'newscast-casual': 'mstts:express-as',
            'newscast-formal': 'mstts:express-as',
            'documentary-narration': 'mstts:express-as',
            'advertisement_upbeat': 'mstts:express-as',
            'sports_commentary': 'mstts:express-as',
            'sports_commentary_excited': 'mstts:express-as'
        })

        self.ssml_tag_sort_order = [
            'emphasis', 'mstts:express-as', 'say-as', 'prosody', 'voice', 'lang', 'sub', 'phoneme'
        ]

    def get_voice_tag_fallback(self, name: str) -> dict:
        if name.lower() == 'device':
            return None
        return {'name': name}

    def contains_mstts_tag(self, lines: list) -> bool:
        mstts_prefix_regex = re.compile(r'</?mstts:')
        return any(mstts_prefix_regex.search(line) for line in lines)

    def add_speak_tag(self, ast: ASTNode, new_line: bool, new_line_after_end: bool, attr: dict, lines: list) -> list:
        content_lines = []
        self.processAst(ast, content_lines)
        self.add_section_end_tag(content_lines)

        has_mstts_tag = self.contains_mstts_tag(content_lines)
        speak_attrs = attr or {}
        if has_mstts_tag:
            speak_attrs['xmlns:mstts'] = 'https://www.w3.org/2001/mstts'

        lines.append(self.start_tag('speak', speak_attrs, new_line))
        lines.extend(content_lines)
        lines.append(self.end_tag('speak', new_line))

        if new_line_after_end:
            lines.append('\n')

        return lines

    def get_text_modifier_object(self, ast: ASTNode) -> TagsObject:
        tmo = TagsObject(self)
        express_as_attrs = {}

        for child in ast.children:
            if child.name in ('plainText', 'plainTextSpecialChars', 'plainTextEmphasis', 'plainTextPhone', 'plainTextModifier'):
                tmo.text = child.allText
            elif child.name == 'textModifierKeyOptionalValue':
                key = child.children[0].allText
                key = self.modifier_key_mappings.get(key, key)
                value = child.children[1].allText if len(child.children) == 2 else ''
                ssml_tag = self.modifier_key_to_ssml_tag_mappings.get(key)

                if key in ('address', 'fraction', 'ordinal', 'telephone'):
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
                elif key == 'whisper':
                    tmo.tag(ssml_tag, {'volume': 'x-soft', 'rate': 'slow'})
                elif key == 'ipa':
                    tmo.tag(ssml_tag, {'alphabet': key, 'ph': value})
                elif key == 'sub':
                    tmo.tag(ssml_tag, {'alias': value})
                elif key in ('volume', 'rate', 'pitch'):
                    tmo.tag(ssml_tag, {key: value or 'medium'}, True)
                elif key == 'voice':
                    tmo.voice_tag(value)
                elif key == 'style':
                    express_as_attrs['style'] = value
                elif key == 'role':
                    express_as_attrs['role'] = value
                elif key in [
                    'excited', 'disappointed', 'friendly', 'cheerful', 'sad', 'angry', 'fearful', 'empathetic',
                    'calm', 'lyrical', 'hopeful', 'terrified', 'shouting', 'whispering', 'unfriendly', 'gentle',
                    'serious', 'depressed', 'embarrassed', 'disgruntled', 'envious', 'affectionate', 'assistant',
                    'chat', 'customerservice', 'poetry-reading', 'narration-professional', 'narration-relaxed',
                    'newscast-casual', 'newscast-formal', 'newscaster', 'documentary-narration',
                    'advertisement_upbeat', 'sports_commentary', 'sports_commentary_excited'
                ]:
                    express_as_attrs['style'] = 'newscast' if key == 'newscaster' else key
                    if value:
                        try:
                            style_degree = float(value)
                            if self.min_style_degree <= style_degree <= self.max_style_degree:
                                express_as_attrs['styledegree'] = value
                        except ValueError:
                            pass
                elif key == 'lang':
                    tmo.tag(ssml_tag, {'xml:lang': value})
                
        if express_as_attrs.get('style'):
            ssml_tag = self.modifier_key_to_ssml_tag_mappings['excited']
            tmo.tag(ssml_tag, express_as_attrs)

        return tmo

    def get_section_object(self, ast: ASTNode) -> TagsObject:
        so = TagsObject(self)

        for child in ast.children:
            if child.name == 'sectionModifierKeyOptionalValue':
                key = child.children[0].allText
                value = child.children[1].allText if len(child.children) == 2 else ''
                ssml_tag = self.modifier_key_to_ssml_tag_mappings.get(key)

                if key == 'voice':
                    so.voice_tag(value)
                elif key == 'defaults':
                    pass
                elif key in [
                    'excited', 'disappointed', 'friendly', 'cheerful', 'sad', 'angry', 'fearful', 'empathetic',
                    'calm', 'lyrical', 'hopeful', 'terrified', 'shouting', 'whispering', 'unfriendly', 'gentle',
                    'serious', 'depressed', 'embarrassed', 'disgruntled', 'envious', 'affectionate', 'assistant',
                    'chat', 'customerservice', 'poetry-reading', 'narration-professional', 'narration-relaxed',
                    'newscast-casual', 'newscast-formal', 'newscaster', 'documentary-narration',
                    'advertisement_upbeat', 'sports_commentary', 'sports_commentary_excited'
                ]:
                    attrs = {'style': 'newscast' if key == 'newscaster' else key}
                    if value:
                        try:
                            style_degree = float(value)
                            if self.min_style_degree <= style_degree <= self.max_style_degree:
                                attrs['styledegree'] = value
                        except ValueError:
                            pass
                    so.tag(ssml_tag, attrs)
                elif key == 'lang':
                    so.tag(ssml_tag, {'xml:lang': value})

        return so

    def formatFromAst(self, ast: ASTNode, lines: list = None) -> list:
        if lines is None:
            lines = []
        if not hasattr(ast, 'name'):
            return lines

        if ast.name == 'document':
            if getattr(self.options, 'includeFormatterComment', False):
                self.add_comment('Converted from Speech Markdown to SSML for Microsoft Azure', lines)
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
        elif ast.name == 'markTag':
            name = ast.children[0].allText
            return self.add_tag_with_attrs(lines, None, 'bookmark', {'mark': name}, False)
        elif ast.name == 'shortEmphasisModerate':
            text = ast.children[0].allText
            return self.add_tag_with_attrs(lines, text, 'emphasis', {'level': 'moderate'})
        elif ast.name == 'shortEmphasisStrong':
            text = ast.children[0].allText
            return self.add_tag_with_attrs(lines, text, 'emphasis', {'level': 'strong'})
        elif ast.name == 'shortEmphasisNone':
            text = ast.children[0].allText
            return self.add_tag_with_attrs(lines, text, 'emphasis', {'level': 'none'})
        elif ast.name == 'shortEmphasisReduced':
            text = ast.children[0].allText
            return self.add_tag_with_attrs(lines, text, 'emphasis', {'level': 'reduced'})
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
