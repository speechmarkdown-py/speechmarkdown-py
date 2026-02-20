from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class SpeechOptions:
    platform: str = ""
    includeFormatterComment: bool = False
    includeParagraphTag: bool = False
    includeSpeakTag: bool = True
    preserveEmptyLines: bool = True
    escapeXmlSymbols: bool = False
    voices: Optional[Dict[str, Any]] = None
