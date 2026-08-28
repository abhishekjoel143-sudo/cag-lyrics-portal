#!/usr/bin/env python3
"""Kannada PPT Lyrics Converter

Reads PowerPoint (.pptx) files with Unicode Kannada or common legacy Nudi
encoding and writes UTF-8 lyric text files. No Python packages are required.

Usage:
  python kannada_ppt_lyrics_converter.py song1.pptx song2.pptx
  python kannada_ppt_lyrics_converter.py "C:\\path\\to\\folder"
  python kannada_ppt_lyrics_converter.py "C:\\path\\to\\folder" song2.pptx
  python kannada_ppt_lyrics_converter.py
      (with no arguments, processes every .pptx in the current folder)
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
VATT = "\x01"

# Nudi / Baraha-compatible legacy mappings.  The longest sequences are
# intentionally replaced first.
M = {
    "Pï":"ಕ್", "PÀ":"ಕ", "PÁ":"ಕಾ", "Q":"ಕಿ", "QÃ":"ಕೀ", "PÀÄ":"ಕು", "PÀÆ":"ಕೂ", "PÀÈ":"ಕೃ", "PÉ":"ಕೆ", "PÉÃ":"ಕೇ", "PÉÊ":"ಕೈ", "PÉÆ":"ಕೊ", "PÉÆÃ":"ಕೋ", "PË":"ಕೌ",
    "Sï":"ಖ್", "R":"ಖ", "SÁ":"ಖಾ", "T":"ಖಿ", "TÃ":"ಖೀ", "RÄ":"ಖು", "RÆ":"ಖೂ", "RÈ":"ಖೃ", "SÉ":"ಖೆ", "SÉÃ":"ಖೇ", "SÉÊ":"ಖೈ", "SÉÆ":"ಖೊ", "SÉÆÃ":"ಖೋ", "SË":"ಖೌ",
    "Uï":"ಗ್", "UÀ":"ಗ", "UÁ":"ಗಾ", "V":"ಗಿ", "VÃ":"ಗೀ", "UÀÄ":"ಗು", "UÀÆ":"ಗೂ", "UÀÈ":"ಗೃ", "UÉ":"ಗೆ", "UÉÃ":"ಗೇ", "UÉÊ":"ಗೈ", "UÉÆ":"ಗೊ", "UÉÆÃ":"ಗೋ", "UË":"ಗೌ",
    "Wï":"ಘ್", "WÀ":"ಘ", "WÁ":"ಘಾ", "X":"ಘಿ", "XÃ":"ಘೀ", "WÀÄ":"ಘು", "WÀÆ":"ಘೂ", "WÀÈ":"ಘೃ", "WÉ":"ಘೆ", "WÉÃ":"ಘೇ", "WÉÊ":"ಘೈ", "WÉÆ":"ಘೊ", "WÉÆÃ":"ಘೋ", "WË":"ಘೌ",
    "Yï":"ಙ್", "Y":"ಙ",
    "Zï":"ಚ್", "ZÀ":"ಚ", "ZÁ":"ಚಾ", "a":"ಚಿ", "aÃ":"ಚೀ", "ZÀÄ":"ಚು", "ZÀÆ":"ಚೂ", "ZÀÈ":"ಚೃ", "ZÉ":"ಚೆ", "ZÉÃ":"ಚೇ", "ZÉÊ":"ಚೈ", "ZÉÆ":"ಚೊ", "ZÉÆÃ":"ಚೋ", "ZË":"ಚೌ",
    "bï":"ಛ್", "bÀ":"ಛ", "bÁ":"ಛಾ", "c":"ಛಿ", "cÃ":"ಛೀ", "bÀÄ":"ಛು", "bÀÆ":"ಛೂ", "bÀÈ":"ಛೃ", "bÉ":"ಛೆ", "bÉÃ":"ಛೇ", "bÉÊ":"ಛೈ", "bÉÆ":"ಛೊ", "bÉÆÃ":"ಛೋ", "bË":"ಛೌ",
    "eï":"ಜ್", "d":"ಜ", "eÁ":"ಜಾ", "f":"ಜಿ", "fÃ":"ಜೀ", "dÄ":"ಜು", "dÆ":"ಜೂ", "dÈ":"ಜೃ", "eÉ":"ಜೆ", "eÉÃ":"ಜೇ", "eÉÊ":"ಜೈ", "eÉÆ":"ಜೊ", "eÉÆÃ":"ಜೋ", "eË":"ಜೌ",
    "kï":"ಞ್", "k":"ಞ",
    "mï":"ಟ್", "l":"ಟ", "mÁ":"ಟಾ", "n":"ಟಿ", "nÃ":"ಟೀ", "lÄ":"ಟು", "lÆ":"ಟೂ", "lÈ":"ಟೃ", "mÉ":"ಟೆ", "mÉÃ":"ಟೇ", "mÉÊ":"ಟೈ", "mÉÆ":"ಟೊ", "mÉÆÃ":"ಟೋ", "mË":"ಟೌ",
    "oï":"ಠ್", "oÀ":"ಠ", "oÁ":"ಠಾ", "p":"ಠಿ", "pÃ":"ಠೀ", "oÀÄ":"ಠು", "oÀÆ":"ಠೂ", "oÀÈ":"ಠೃ", "oÉ":"ಠೆ", "oÉÃ":"ಠೇ", "oÉÊ":"ಠೈ", "oÉÆ":"ಠೊ", "oÉÆÃ":"ಠೋ", "oË":"ಠೌ",
    "qï":"ಡ್", "qÀ":"ಡ", "qÁ":"ಡಾ", "r":"ಡಿ", "rÃ":"ಡೀ", "qÀÄ":"ಡು", "qÀÆ":"ಡೂ", "qÀÈ":"ಡೃ", "qÉ":"ಡೆ", "qÉÃ":"ಡೇ", "qÉÊ":"ಡೈ", "qÉÆ":"ಡೊ", "qÉÆÃ":"ಡೋ", "qË":"ಡೌ",
    "uï":"ಣ್", "t":"ಣ", "uÁ":"ಣಾ", "tÂ":"ಣಿ", "tÂÃ":"ಣೀ", "tÄ":"ಣು", "tÆ":"ಣೂ", "tÈ":"ಣೃ", "uÉ":"ಣೆ", "uÉÃ":"ಣೇ", "uÉÊ":"ಣೈ", "uÉÆ":"ಣೊ", "uÉÆÃ":"ಣೋ", "uË":"ಣೌ",
    "vï":"ತ್", "vÀ":"ತ", "vÁ":"ತಾ", "w":"ತಿ", "wÃ":"ತೀ", "vÀÄ":"ತು", "vÀÆ":"ತೂ", "vÀÈ":"ತೃ", "vÉ":"ತೆ", "vÉÃ":"ತೇ", "vÉÊ":"ತೈ", "vÉÆ":"ತೊ", "vÉÆÃ":"ತೋ", "vË":"ತೌ",
    "xï":"ಥ್", "xÀ":"ಥ", "xÁ":"ಥಾ", "y":"ಥಿ", "yÃ":"ಥೀ", "xÀÄ":"ಥು", "xÀÆ":"ಥೂ", "xÀÈ":"ಥೃ", "xÉ":"ಥೆ", "xÉÃ":"ಥೇ", "xÉÊ":"ಥೈ", "xÉÆ":"ಥೊ", "xÉÆÃ":"ಥೋ", "xË":"ಥೌ",
    "zï":"ದ್", "zÀ":"ದ", "zÁ":"ದಾ", "¢":"ದಿ", "¢Ã":"ದೀ", "zÀÄ":"ದು", "zÀÆ":"ದೂ", "zÀÈ":"ದೃ", "zÉ":"ದೆ", "zÉÃ":"ದೇ", "zÉÊ":"ದೈ", "zÉÆ":"ದೊ", "zÉÆÃ":"ದೋ", "zË":"ದೌ",
    "zsï":"ಧ್", "zsÀ":"ಧ", "zsÁ":"ಧಾ", "¢ü":"ಧಿ", "¢üÃ":"ಧೀ", "zsÀÄ":"ಧು", "zsÀÆ":"ಧೂ", "zsÀÈ":"ಧೃ", "zsÉ":"ಧೆ", "zsÉÃ":"ಧೇ", "zsÉÊ":"ಧೈ", "zsÉÆ":"ಧೊ", "zsÉÆÃ":"ಧೋ", "zsË":"ಧೌ",
    "£ï":"ನ್", "£À":"ನ", "£Á":"ನಾ", "¤":"ನಿ", "¤Ã":"ನೀ", "£ÀÄ":"ನು", "£ÀÆ":"ನೂ", "£ÀÈ":"ನೃ", "£É":"ನೆ", "£ÉÃ":"ನೇ", "£ÉÊ":"ನೈ", "£ÉÆ":"ನೊ", "£ÉÆÃ":"ನೋ", "£Ë":"ನೌ",
    "¥ï":"ಪ್", "¥À":"ಪ", "¥Á":"ಪಾ", "¦":"ಪಿ", "¦Ã":"ಪೀ", "¥ÀÄ":"ಪು", "¥ÀÅ":"ಪು", "¥ÀÆ":"ಪೂ", "¥ÀÇ":"ಪೂ", "¥ÀÈ":"ಪೃ", "¥É":"ಪೆ", "¥ÉÃ":"ಪೇ", "¥ÉÊ":"ಪೈ", "¥ÉÆ":"ಪೊ", "¥ÉÇ":"ಪೊ", "¥ÉÆÃ":"ಪೋ", "¥ÉÇÃ":"ಪೋ", "¥Ë":"ಪೌ",
    "¨ï":"ಬ್", "§":"ಬ", "¨Á":"ಬಾ", "©":"ಬಿ", "©Ã":"ಬೀ", "§Ä":"ಬು", "§Æ":"ಬೂ", "§È":"ಬೃ", "¨É":"ಬೆ", "¨ÉÃ":"ಬೇ", "¨ÉÊ":"ಬೈ", "¨ÉÆ":"ಬೊ", "¨ÉÆÃ":"ಬೋ", "¨Ë":"ಬೌ",
    "¨sï":"ಭ್", "¨sÀ":"ಭ", "¨sÁ":"ಭಾ", "©ü":"ಭಿ", "©üÃ":"ಭೀ", "¨sÀÄ":"ಭು", "¨sÀÆ":"ಭೂ", "¨sÀÈ":"ಭೃ", "¨sÉ":"ಭೆ", "¨sÉÃ":"ಭೇ", "¨sÉÊ":"ಭೈ", "¨sÉÆ":"ಭೊ", "¨sÉÆÃ":"ಭೋ", "¨sË":"ಭೌ",
    "ªÀiï":"ಮ್", "ªÀÄ":"ಮ", "ªÀiÁ":"ಮಾ", "«Ä":"ಮಿ", "«ÄÃ":"ಮೀ", "ªÀÄÄ":"ಮು", "ªÀÄÆ":"ಮೂ", "ªÀÄÈ":"ಮೃ", "ªÉÄ":"ಮೆ", "ªÉÄÃ":"ಮೇ", "ªÉÄÊ":"ಮೈ", "ªÉÆ":"ಮೊ", "ªÉÆÃ":"ಮೋ", "ªÀiË":"ಮೌ",
    "AiÀiï":"ಯ್", "AiÀÄ":"ಯ", "AiÀiÁ":"ಯಾ", "¬Ä":"ಯಿ", "¬ÄÃ":"ಯೀ", "AiÀÄÄ":"ಯು", "AiÀÄÆ":"ಯೂ", "AiÀÄÈ":"ಯೃ", "AiÉÄ":"ಯೆ", "AiÉÄÃ":"ಯೇ", "AiÉÄÊ":"ಯೈ", "AiÉÆ":"ಯೊ", "AiÉÆÃ":"ಯೋ", "AiÀiË":"ಯೌ",
    "gï":"ರ್", "gÀ":"ರ", "gÁ":"ರಾ", "j":"ರಿ", "jÃ":"ರೀ", "gÀÄ":"ರು", "gÀÆ":"ರೂ", "gÀÈ":"ರೃ", "gÉ":"ರೆ", "gÉÃ":"ರೇ", "gÉÊ":"ರೈ", "gÉÆ":"ರೊ", "gÉÆÃ":"ರೋ", "gË":"ರೌ",
    "¯ï":"ಲ್", "®":"ಲ", "¯Á":"ಲಾ", "°":"ಲಿ", "°Ã":"ಲೀ", "®Ä":"ಲು", "®Æ":"ಲೂ", "®È":"ಲೃ", "¯É":"ಲೆ", "¯ÉÃ":"ಲೇ", "¯ÉÊ":"ಲೈ", "¯ÉÆ":"ಲೊ", "¯ÉÆÃ":"ಲೋ", "¯Ë":"ಲೌ",
    "ªï":"ವ್", "ªÀ":"ವ", "ªÁ":"ವಾ", "«":"ವಿ", "«Ã":"ವೀ", "ªÀÅ":"ವು", "ªÀÇ":"ವೂ", "ªÀÈ":"ವೃ", "ªÉ":"ವೆ", "ªÉÃ":"ವೇ", "ªÉÊ":"ವೈ", "ªÉÇ":"ವೊ", "ªÉÇÃ":"ವೋ", "ªË":"ವೌ",
    "±ï":"ಶ್", "±À":"ಶ", "±Á":"ಶಾ", "²":"ಶಿ", "²Ã":"ಶೀ", "±ÀÄ":"ಶು", "±ÀÆ":"ಶೂ", "±ÀÈ":"ಶೃ", "±É":"ಶೆ", "±ÉÃ":"ಶೇ", "±ÉÊ":"ಶೈ", "±ÉÆ":"ಶೊ", "±ÉÆÃ":"ಶೋ", "±Ë":"ಶೌ",
    "μï":"ಷ್", "μÀ":"ಷ", "μÁ":"ಷಾ", "¶":"ಷಿ", "¶Ã":"ಷೀ", "μÀÄ":"ಷು", "μÀÆ":"ಷೂ", "μÀÈ":"ಷೃ", "μÉ":"ಷೆ", "μÉÃ":"ಷೇ", "μÉÊ":"ಷೈ", "μÉÆ":"ಷೊ", "μÉÆÃ":"ಷೋ", "μË":"ಷೌ",
    "¸ï":"ಸ್", "¸À":"ಸ", "¸Á":"ಸಾ", "¹":"ಸಿ", "¹Ã":"ಸೀ", "¸ÀÄ":"ಸು", "¸ÀÆ":"ಸೂ", "¸ÀÈ":"ಸೃ", "¸É":"ಸೆ", "¸ÉÃ":"ಸೇ", "¸ÉÊ":"ಸೈ", "¸ÉÆ":"ಸೊ", "¸ÉÆÃ":"ಸೋ", "¸Ë":"ಸೌ",
    "ºï":"ಹ್", "ºÀ":"ಹ", "ºÁ":"ಹಾ", "»":"ಹಿ", "»Ã":"ಹೀ", "ºÀÄ":"ಹು", "ºÀÆ":"ಹೂ", "ºÀÈ":"ಹೃ", "ºÉ":"ಹೆ", "ºÉÃ":"ಹೇ", "ºÉÊ":"ಹೈ", "ºÉÆ":"ಹೊ", "ºÉÆÃ":"ಹೋ", "ºË":"ಹೌ",
    "¼ï":"ಳ್", "¼À":"ಳ", "¼Á":"ಳಾ", "½":"ಳಿ", "½Ã":"ಳೀ", "¼ÀÄ":"ಳು", "¼ÀÆ":"ಳೂ", "¼ÀÈ":"ಳೃ", "¼É":"ಳೆ", "¼ÉÃ":"ಳೇ", "¼ÉÊ":"ಳೈ", "¼ÉÆ":"ಳೊ", "¼ÉÆÃ":"ಳೋ", "¼Ë":"ಳೌ",
    "A":"ಂ", "B":"ಃ", "C":"ಅ", "D":"ಆ", "E":"ಇ", "F":"ಈ", "G":"ಉ", "H":"ಊ", "IÄ":"ಋ", "IÆ":"ೠ", "J":"ಎ", "K":"ಏ", "L":"ಐ", "M":"ಒ", "N":"ಓ", "O":"ಔ", "x":"ಕ್ಷ", "GY":"ಜ್ಞ",
}
VATT_MAP = dict(zip("ÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîö",
                    "ಕಖಗಘಙಚಛಜಝಞಟಠಡಢಣತಥದಧನಪಫಬಭಮಯರರಲವಶಷಸಹಳಯ"))
# Keep ð unconverted until the reph pass: in Nudi it means that "ರ್" is
# displayed before the preceding syllable, although it is typed afterward.
OTHER = {"µ":"ಷ", "ø":"ೃ", "ñ":"ೄ", "„":"ಽ", "ó":"಼", "ï":"್"}
ROMAN = {
    "ಅ":"a","ಆ":"aa","ಇ":"i","ಈ":"ee","ಉ":"u","ಊ":"oo","ಋ":"ru","ಎ":"e","ಏ":"ee","ಐ":"ai","ಒ":"o","ಓ":"oo","ಔ":"au",
    "ಕ":"ka","ಖ":"kha","ಗ":"ga","ಘ":"gha","ಙ":"nga","ಚ":"cha","ಛ":"chha","ಜ":"ja","ಝ":"jha","ಞ":"nya","ಟ":"ta","ಠ":"tha","ಡ":"da","ಢ":"dha","ಣ":"na","ತ":"ta","ಥ":"tha","ದ":"da","ಧ":"dha","ನ":"na","ಪ":"pa","ಫ":"pha","ಬ":"ba","ಭ":"bha","ಮ":"ma","ಯ":"ya","ರ":"ra","ಲ":"la","ವ":"va","ಶ":"sha","ಷ":"sha","ಸ":"sa","ಹ":"ha","ಳ":"la","ೞ":"la",
    "ಾ":"a","ಿ":"i","ೀ":"ee","ು":"u","ೂ":"oo","ೃ":"ru","ೆ":"e","ೇ":"ee","ೈ":"ai","ೊ":"o","ೋ":"oo","ೌ":"au","ಂ":"m","ಃ":"h","್":"", "ೄ":"ru",
}

def legacy_to_unicode(text: str) -> str:
    if not any(ord(c) > 127 for c in text) and not re.search(r"[A-Za-z][À-ÿ]", text):
        return text
    text = re.sub("É{2,}", "É", text)
    for key in sorted(M, key=len, reverse=True):
        text = text.replace(key, M[key])
    text = text.replace("À", "")
    # Fix legacy subscript consonants and the common post-vowel fragments.
    # Move a Nudi reph (e.g. ಷಿð) to its Unicode reading position (ರ್ಷಿ).
    text = re.sub(r"([ಕ-ಹೞ])([ಾಿೀುೂೃೄೆೇೈೊೋೌ]?)ð", r"ರ್\1\2", text)
    text = text.replace("ð", "ರ")
    for key, val in VATT_MAP.items():
        text = text.replace(key, VATT + val)
    for key, val in OTHER.items():
        text = text.replace(key, val)
    text = (text.replace("ÉÆÃ", "ೋ").replace("ÉÆ", "ೊ").replace("ÉÊ", "ೈ")
                .replace("ÉÃ", "ೇ").replace("É", "ೆ").replace("Æ", "ೂ"))
    pattern = re.compile(r"([ಕ-ಹೞ])([ಾಿೀುೂೃೄೆೇೈೊೋೌ]?)" + VATT + r"([ಕ-ಹೞ])")
    while pattern.search(text):
        text = pattern.sub(r"\1್\3\2", text)
    text = re.sub(VATT, "್", text)
    # Long-vowel byte left behind after a conjunct is reordered (ಶಿ + ರ್ + Ã).
    text = (text.replace("ಿÃ", "ೀ").replace("ೆÃ", "ೇ").replace("ೊÃ", "ೋ")
                .replace("ುÆ", "ೂ").replace("Ã", "ೀ"))
    return text

def romanise(text: str) -> str:
    out = []
    for c in text:
        out.append(ROMAN.get(c, c))
    # A consonant's default "a" must disappear when a vowel sign follows.
    result = "".join(out)
    for vowel in ("i", "ee", "u", "oo", "e", "ai", "o", "au", "ru"):
        result = result.replace("a" + vowel, vowel)
    return result

def slide_texts(pptx: Path):
    with zipfile.ZipFile(pptx) as z:
        names = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=lambda n: int(re.search(r"\d+", n).group()))
        for number, name in enumerate(names, 1):
            root = ET.fromstring(z.read(name))
            lines = []
            for paragraph in root.findall(".//a:p", NS):
                text = "".join(t.text or "" for t in paragraph.findall(".//a:t", NS)).strip()
                if text:
                    lines.append(text)
            yield number, lines

def convert_ppt(pptx: Path) -> Path:
    kannada_blocks = [f"{pptx.stem}\n{'=' * len(pptx.stem)}\n"]
    english_blocks = [f"{pptx.stem} — English-letter pronunciation\n{'=' * (len(pptx.stem) + 31)}\n"]
    for slide, raw_lines in slide_texts(pptx):
        unicode_lines = [legacy_to_unicode(line) for line in raw_lines]
        kannada_blocks.append(f"Slide {slide}\n" + "\n".join(unicode_lines))
        english_blocks.append(f"Slide {slide}\n" + "\n".join(romanise(line) for line in unicode_lines))
    kannada_output = pptx.with_name(pptx.stem + "_Kannada.txt")
    english_output = pptx.with_name(pptx.stem + "_English_Pronunciation.txt")
    kannada_output.write_text("\n\n".join(kannada_blocks) + "\n", encoding="utf-8")
    english_output.write_text("\n\n".join(english_blocks) + "\n", encoding="utf-8")
    return kannada_output, english_output

def collect_pptx_files(args: list[str]) -> list[Path]:
    """Turn CLI args (files and/or folders) into a flat, de-duplicated list
    of .pptx files. Folders are scanned non-recursively for *.pptx.
    If no args are given, scan the current working directory."""
    inputs = [Path(a) for a in args] if args else [Path(".")]
    files: list[Path] = []
    seen = set()
    for item in inputs:
        if item.is_dir():
            found = sorted(item.glob("*.pptx"))
            if not found:
                print(f"No .pptx files found in folder: {item}")
            for f in found:
                if f.resolve() not in seen:
                    seen.add(f.resolve())
                    files.append(f)
        elif item.is_file() and item.suffix.lower() == ".pptx":
            if item.resolve() not in seen:
                seen.add(item.resolve())
                files.append(item)
        else:
            print(f"Skipped (not a .pptx file or folder): {item}")
    return files

def main():
    files = collect_pptx_files(sys.argv[1:])
    if not files:
        print("No .pptx files to process.")
        print("Usage: python kannada_ppt_lyrics_converter.py <file.pptx | folder> ...")
        return 1
    print(f"Found {len(files)} .pptx file(s) to convert.\n")
    ok = 0
    for file in files:
        try:
            kannada_output, english_output = convert_ppt(file)
            print(f"Converted: {file.name}")
            print(f"  -> {kannada_output.name}")
            print(f"  -> {english_output.name}")
            ok += 1
        except Exception as e:
            print(f"FAILED: {file.name}  ({e})")
    print(f"\nDone. {ok}/{len(files)} file(s) converted successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())