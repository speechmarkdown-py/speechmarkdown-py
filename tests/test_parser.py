from speechmarkdown.parser import SpeechMarkdownParser, ASTNode

def test_basic_plain_text():
    parser = SpeechMarkdownParser()
    ast = parser.parse("Hello world")
    
    assert ast.name == "document"
    assert len(ast.children) == 1
    p = ast.children[0]
    assert p.name == "paragraph"
    assert len(p.children) == 1
    sl = p.children[0]
    assert sl.name == "simpleLine"
    
    pt = sl.children[0]
    assert pt.name == "plainText"
    assert pt.allText == "Hello world"
