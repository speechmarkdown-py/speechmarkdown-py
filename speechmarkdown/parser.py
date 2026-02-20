import pyparsing as pp
import re

pp.ParserElement.enable_packrat()

class ASTNode:
    def __init__(self, name: str, allText: str, children: list):
        self.name = name
        self.allText = allText
        self.children = children

    def __repr__(self):
        return f"ASTNode({self.name}, {repr(self.allText)}, {self.children})"

    def to_dict(self):
        return {
            "name": self.name,
            "allText": self.allText,
            "children": [c.to_dict() if isinstance(c, ASTNode) else c for c in self.children]
        }

def ast(name: str, expr: pp.ParserElement) -> pp.ParserElement:
    marker = pp.Empty().set_parse_action(lambda s, l, t: l)
    seq = marker + expr + marker

    def pa(s, loc, toks):
        start = toks[0]
        end = toks[-1]
        allText = s[start:end]
        children = [t for t in toks[1:-1] if isinstance(t, ASTNode)]
        return ASTNode(name, allText, children)

    return seq.set_parse_action(pa).set_name(name)

def parenthesized(rule: pp.ParserElement) -> pp.ParserElement:
    return pp.Suppress('(') + pp.Optional(pp.Char(' \t')[1, ...]) + rule + pp.Optional(pp.Char(' \t')[1, ...]) + pp.Suppress(')')

class SpeechMarkdownParser:
    def __init__(self):
        self.grammar = self._build_grammar()

    def _build_grammar(self):
        ws = pp.Char(' \t')[1, ...]
        optWs = pp.Optional(ws)
        
        specialCharSet = '[]()'
        specialCharSetEmphasis = '[]()*~`@#\\_!+-/'

        nonSpecialChar = ~(pp.LineEnd()) + pp.Regex(f'[^{"".join(re.escape(c) for c in specialCharSetEmphasis)}]')
        nonSpecialCharEmphasis = ~(pp.LineEnd()) + pp.Regex(f'[^{"".join(re.escape(c) for c in specialCharSet)}]')

        digits = pp.Word(pp.nums)
        letters = pp.Word(pp.alphas)
        integer = pp.Word(pp.nums)
        hyphen = pp.Literal('-')
        space = pp.Literal(' ')

        xsdToken = ast('xsdToken', (digits | letters | pp.Char(specialCharSetEmphasis))[1, ...])

        plainText = ast('plainText', (digits | letters | ws | nonSpecialChar)[1, ...])
        plainTextEmphasis = ast('plainTextEmphasis', (digits | letters | ws | nonSpecialChar)[1, ...])
        plainTextChoice = digits | letters | ws | nonSpecialCharEmphasis
        plainTextModifier = ast('plainTextModifier', plainTextChoice[1, ...])
        
        plainTextPhone = ast('plainTextPhone', parenthesized(digits) + plainTextChoice[1, ...])

        plainTextSpecialChars = ast('plainTextSpecialChars', (
            (pp.Suppress('(') + plainTextChoice + pp.Suppress(') ')) |
            (pp.Suppress('[') + plainTextChoice + pp.Suppress('] ')) |
            pp.Char(specialCharSetEmphasis)[1, ...]
        )[1, ...])

        # Break
        timeUnit = ast('timeUnit', pp.Literal('ms') | pp.Literal('s'))
        fraction = pp.Literal('.') + pp.Word(pp.nums)[0, ...]
        number = ast('number', integer + pp.Optional(fraction))
        time = ast('time', number + timeUnit)
        shortBreak = ast('shortBreak', pp.Suppress('[') + time + pp.Suppress(']'))

        # Emphasis
        notLetterChar = ~(letters | digits)
        
        shortEmphasisModerate = ast('shortEmphasisModerate', notLetterChar + pp.Suppress('+') + plainTextEmphasis + pp.Suppress('+') + notLetterChar)
        shortEmphasisStrong = ast('shortEmphasisStrong', notLetterChar + pp.Suppress('++') + plainTextEmphasis + pp.Suppress('++') + notLetterChar)
        shortEmphasisNone = ast('shortEmphasisNone', notLetterChar + pp.Suppress('~') + plainTextEmphasis + pp.Suppress('~') + notLetterChar)
        shortEmphasisReduced = ast('shortEmphasisReduced', notLetterChar + pp.Suppress('-') + plainTextEmphasis + pp.Suppress('-') + notLetterChar)
        
        emphasis = shortEmphasisModerate | shortEmphasisStrong | shortEmphasisNone | shortEmphasisReduced

        colon = pp.Suppress(':') + optWs
        semicolon = pp.Suppress(';') + optWs

        modifier_keys = [
            'emphasis', 'address', 'number', 'cardinal', 'characters', 'chars',
            'digits', 'drc', 'expletive', 'bleep', 'fraction', 'interjection',
            'ordinal', 'telephone', 'phone', 'unit', 'time', 'date', 'whisper',
            'ipa', 'sub', 'vol', 'volume', 'rate', 'pitch', 'timbre', 'lang', 'voice',
            'style', 'role', 'excited', 'disappointed', 'friendly', 'cheerful',
            'sad', 'angry', 'fearful', 'empathetic', 'calm', 'lyrical', 'hopeful',
            'shouting', 'whispering', 'terrified', 'unfriendly', 'gentle', 'serious',
            'depressed', 'embarrassed', 'disgruntled', 'affectionate', 'envious',
            'chat', 'customerservice', 'assistant', 'poetry-reading',
            'narration-professional', 'narration-relaxed', 'newscast-casual',
            'newscast-formal', 'newscaster', 'documentary-narration',
            'advertisement_upbeat', 'sports_commentary', 'sports_commentary_excited'
        ]
        
        # Sort keys by length descending to match longest first (e.g. "whispering" before "whisper")
        modifier_keys.sort(key=len, reverse=True)
        textModifierKey = ast('textModifierKey', pp.MatchFirst([pp.Keyword(k) for k in modifier_keys]))

        ipaChars = [
            '.', "'", 'æ', '͡ʒ', 'ð', 'ʃ', '͡ʃ', 'θ', 'ʒ', 'ə', 'ɚ', 'aɪ', 'aʊ', 'ɑ',
            'eɪ', 'ɝ', 'ɛ', 'ɪ', 'oʊ', 'ɔ', 'ɔɪ', 'ʊ', 'ʌ', 'ɒ', 'ɛə', 'ɪə', 'ʊə', 'ˈ', 'ˌ', 'ŋ', 'ɹ'
        ]
        
        # Create a matching string for Regex (escape special regex chars)
        ipaCharsEscaped = "".join([re.escape(c) for c in (['.', ':', "'"] + ipaChars)])

        shortIpaValue = ast('shortIpaValue', pp.Regex(f"[a-zA-Z0-9- {ipaCharsEscaped}]+"))
        shortIpa = ast('shortIpa', parenthesized(plainTextModifier) + pp.Suppress('/') + shortIpaValue + pp.Suppress('/'))

        shortSubValue = ast('shortSubValue', ~(pp.LineEnd()) + pp.Regex(r'[^}]+'))
        shortSub = ast('shortSub', parenthesized(plainTextModifier) + pp.Suppress('{') + shortSubValue + pp.Suppress('}'))
        bareIpa = ast('bareIpa', pp.Suppress('/') + shortIpaValue + pp.Suppress('/'))

        percentChangeChars = r"\+\-\d\%"
        textModifierText = ast('textModifierText', pp.Regex(f"[a-zA-Z0-9- {ipaCharsEscaped}{percentChangeChars}]+"))
        textModifierTextDoubleQuote = ast('textModifierTextDoubleQuote', pp.Regex(f"[a-zA-Z0-9- '{ipaCharsEscaped}{percentChangeChars}]+"))

        singleQuotedStr = pp.Suppress("'") + textModifierText + pp.Suppress("'")
        doubleQuotedStr = pp.Suppress('"') + textModifierTextDoubleQuote + pp.Suppress('"')

        textModifierValue = colon + (singleQuotedStr | doubleQuotedStr)
        textModifierKeyOptionalValue = ast('textModifierKeyOptionalValue', textModifierKey + pp.Optional(textModifierValue))
        
        modifier = pp.Suppress('[') + pp.DelimitedList(textModifierKeyOptionalValue + optWs, delim=semicolon) + pp.Suppress(']')

        textText = parenthesized(plainTextModifier)
        textTextPhone = parenthesized(plainTextPhone)
        textModifier = ast('textModifier', (textTextPhone | textText) + modifier)

        urlSpecialChar = pp.Char(':/.-_~?#[]@!+,;%=()&')
        url = ast('url', (digits | letters | urlSpecialChar)[1, ...])
        audio = ast('audio', pp.Suppress('!') + pp.Optional(parenthesized(pp.Optional(plainTextModifier))) + pp.Suppress('[') + (pp.Suppress("'") + url + pp.Suppress("'") | pp.Suppress('"') + url + pp.Suppress('"')) + pp.Suppress(']'))

        # Section
        sectionModifierKey = ast('sectionModifierKey', textModifierKey) # Same keywords!
        sectionModifierText = ast('sectionModifierText', (digits | letters | hyphen)[1, ...])
        sectionModifierValue = colon + (pp.Suppress("'") + sectionModifierText + pp.Suppress("'") | pp.Suppress('"') + sectionModifierText + pp.Suppress('"'))
        sectionModifierKeyOptionalValue = ast('sectionModifierKeyOptionalValue', sectionModifierKey + pp.Optional(sectionModifierValue))
        sectionModifier = pp.Suppress('[') + pp.DelimitedList(sectionModifierKeyOptionalValue + optWs, delim=semicolon) + pp.Suppress(']')
        section = ast('section', pp.Suppress('#') + sectionModifier)

        # Breaks
        breakStrengthValue = ast('breakStrengthValue', pp.Keyword('none') | pp.Keyword('x-weak') | pp.Keyword('weak') | pp.Keyword('medium') | pp.Keyword('strong') | pp.Keyword('x-strong'))
        breakValue = ast('breakValue', breakStrengthValue | time)
        break_tag = ast('break', pp.Suppress('[break:') + (pp.Suppress("'") + breakValue + pp.Suppress("'") | pp.Suppress('"') + breakValue + pp.Suppress('"')) + pp.Suppress(']'))

        markTag = ast('markTag', pp.Suppress('[mark:') + (pp.Suppress("'") + xsdToken + pp.Suppress("'") | pp.Suppress('"') + xsdToken + pp.Suppress('"')) + pp.Suppress(']'))

        any_char = pp.Regex(r'.', flags=re.DOTALL)
        
        inline = ~(pp.LineEnd()) + (bareIpa | shortIpa | shortSub | textModifier | emphasis | shortBreak | break_tag | audio | markTag | plainTextSpecialChars | plainText | any_char)
        
        emptyLine = ast('emptyLine', pp.Regex(r'[ \t]*') + pp.LineEnd())
        lineEnd = pp.LineEnd() | pp.StringEnd()
        restOfLine = inline[0, ...] + lineEnd
        simpleLine = ast('simpleLine', ~emptyLine + ~pp.StringEnd() + restOfLine)
        paragraph = ast('paragraph', simpleLine[1, ...])
        
        content = section | paragraph | emptyLine
        document = ast('document', content[0, ...])

        return document

    def parse(self, text: str):
        try:
            return self.grammar.parse_string(text, parse_all=True)[0]
        except pp.ParseException as e:
            raise ValueError(f"Parse error: {e}")
