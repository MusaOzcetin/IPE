import os
import re
import time

def repair_encoding(text):
    """
    Repariert typische Encoding-Fehler, OCR-Artefakte und Sonderzeichen.
    """
    safe_replacements = {
        "ƒ": "Ä", "¸": "ü", "‰": "ä", "ˆ": "ö", "ñ": "–",
        "ì": '"', "Ñ": '"', "flodul": "Modul", "flediale": "Mediale",
        "Fresentation": "Präsentation", "fräsentation": "Präsentation",
        "idediale": "Mediale", "iktzeichnen": "Aktzeichnen",
        "isualisierung": "Visualisierung", "iräsentation": "Präsentation",
        "//ediale": "Mediale", "//isualisierung": "Visualisierung",
        "÷": "Ö", "¾": "ü", "¼": "ß",
        "gemäfl": "gemäß", "aufler": "außer",
        "Auflerkrafttreten": "Außerkrafttreten", "Auflerkrafttretens": "Außerkrafttretens",
        "schliefl": "schließ", "Schliefl": "Schließ",
        "maflgeblich": "maßgeblich", "Maflnahmen": "Maßnahmen",
        "grofl": "groß", "Grofl": "Groß", "stöfle": "stöße",
        "regelmäfl": "regelmäß", "mäflig": "mäßig",
        "mufi": "muss", "biw": "bzw",
        "Maflgabe": "Maßgabe", "maflgabe": "Maßgabe",
        "Gieflen": "Gießen", # NEU V32
        "ï": "", # NEU V32: Entfernt Geister-Bulletpoints
        "Fehler! Textmarke nicht definiert.": "" # NEU V32: Word-Artefakt
    }
    for bad, good in safe_replacements.items():
        text = text.replace(bad, good)

    word_replacements = {
        "Prüfung": "Prüfung", "gemäß": "gemäß",
        "Außerkrafttreten": "Außerkrafttreten", "außer": "außer",
        "groß": "groß", "maßgeblich": "maßgeblich",
        "Einflusspotenziale": "Einflusspotenziale", "schließlich": "schließlich",
        "anschließend": "anschließend", "Fakultäten": "Fakultäten",
        "Ökologie": "Ökologie", "Tätigkeit": "Tätigkeit",
        "Maßnahmen": "Maßnahmen"
    }
    for bad, good in word_replacements.items():
        text = text.replace(bad, good)

    # NEU V32: Entfernt LaTeX-Reste wie $label{...} textbf{...}$
    text = re.sub(r"\$label\{.*?\}\s*textbf\{(.*?)\}\$", r"## \1", text)

    # Paragraphen überall korrigieren
    text = re.sub(r"ß\s+(\d+)", r"§ \1", text) 
    text = re.sub(r"(?m)^(#+\s*)ß\s+(\d+)", r"\1§ \2", text)
    text = re.sub(r"-\s*ß\s+(\d+)", r"- § \1", text)
    text = re.sub(r"(?m)^\d{2,3}(\.\s+[A-Z])", r"\1", text)
    
    return text

def repair_tables(text):
    """
    Repariert zerrissene Markdown-Tabellen und entfernt reine Zahlen-Tabellen (Artefakte).
    """
    # Tabellen-Trennlinien reparieren
    text = re.sub(r"^\s*-+\|.*$", "|---|", text, flags=re.MULTILINE)
    text = re.sub(r"^.*\|-+\s*$", "|---|", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*-+\|", "|---|", text, flags=re.MULTILINE)
    
    # Entfernt Zeilen, die nur aus Zahlen, Leerzeichen und Pipes bestehen (z.B. "| 1 | 4 | 8 |")
    text = re.sub(r"(?m)^\|[\s\d\|]+\|$", "", text)

    for _ in range(3):
        text = re.sub(r"(\|.*\|)\n\s*\n(\|.*\|)", r"\1\n\2", text)
    return text

def remove_repetitive_content(text):
    """
    Entfernt Zeilen mit OCR-Wiederholungsfehlern (Spam-Filter).
    NEU V32: Verbesserte Logik, die auch Wiederholungen in der Mitte der Zeile findet.
    """
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if len(line) > 100:
            words = line.split()
            if not words: 
                cleaned_lines.append(line)
                continue
            
            # Zähle Worthäufigkeiten (nur Wörter > 3 Zeichen)
            word_counts = {}
            for w in words:
                w_lower = w.lower()
                if len(w_lower) > 3:
                    word_counts[w_lower] = word_counts.get(w_lower, 0) + 1
            
            # Wenn ein Wort extrem oft vorkommt (>10 mal) oder >50% der Zeile ausmacht
            is_spam = False
            for w, count in word_counts.items():
                if count > 10 or (count > 5 and count > len(words) * 0.5):
                    is_spam = True
                    break
            
            if is_spam:
                continue
                
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def parse_metadata(filename):
    base = filename.replace(".md", "")
    parts = base.split("_")
    
    program = parts[0]
    degree = "Unbekannt"
    year = "Unbekannt"

    if len(parts) >= 2:
        for part in parts:
            if any(x in part for x in ["B.Sc", "M.Sc", "B.A", "M.A", "M.Ed", "MBA", "Staatsexamen", "Diplom", "LL.M", "LL.B"]):
                degree = part
            if part.isdigit() and len(part) == 4:
                year = part
                
    if degree != "Unbekannt":
        try:
            degree_index = parts.index(degree)
            program = " ".join(parts[:degree_index])
        except ValueError:
            pass
    else:
        if "Lebensmittelchemie" in filename:
            program = "Lebensmittelchemie"
            degree = "Staatsexamen"

    return {
        "program": program,
        "degree": degree,
        "year": year,
        "original_filename": filename
    }

def clean_jurist_garbage_safely(text):
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    
    # Erkennt "Der", "Die" oder "Das" ... hat beschlossen
    garbage_pattern = re.compile(r"(?:Der|Die|Das)\s+.*?(?:rat|kommission|gremium).*?hat.*?am.*?beschlossen", re.IGNORECASE | re.DOTALL)
    
    for p in paragraphs:
        if "beschlossen" in p and any(x in p for x in ["rat", "Kommission", "Gremium"]):
            if len(p) < 2500: 
                if garbage_pattern.search(p):
                    continue
        cleaned_paragraphs.append(p)
        
    return "\n\n".join(cleaned_paragraphs)

def clean_content(content, metadata):
    # 0. PRE-CLEANING
    content = repair_encoding(content)
    content = repair_tables(content)
    content = remove_repetitive_content(content)

    header_block = (
        f"# STUDIENGANG: {metadata['program']}\n"
        f"**Abschluss:** {metadata['degree']} | **Jahr:** {metadata['year']}\n"
        f"**Datei:** {metadata['original_filename']}\n\n"
        "---\n\n"
    )

    # --- PHASE 1: ZEILENBASIERTE BEREINIGUNG ---
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
    content = re.sub(r"\[image:.*?\]", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<[^>]+>", "", content)
    content = content.replace("\\", "") 
    
    content = re.sub(r"\|.*AMBl.*\|", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\|-+\|", "", content)
    content = re.sub(r"_{3,}", "", content) 
    
    content = re.sub(r"^\s*AMBl\.*.*$", "", content, flags=re.MULTILINE | re.IGNORECASE)
    content = re.sub(r"^\s*Seite\s*\d+.*$", "", content, flags=re.MULTILINE | re.IGNORECASE)
    
    content = re.sub(r"^\s*(Studien-?|Zugangs-?)\s*(und)?\s*(Prüfungs|Zulassungs)ordnung\s*\d+/\d+.*$", "", content, flags=re.MULTILINE | re.IGNORECASE)
    content = re.sub(r"^[-| ]+$", "", content, flags=re.MULTILINE)

    line_patterns = [
        r"Vom \d{1,2}\.\s*[A-Z][a-z]+\s*\d{4}",
        r"Herausgeber:.*",
        r"\*\) Bestätigt.*",
        r"^.*Rechts- und Verwaltungsvorschriften.*$", 
        r"^#+\s*Fakultäten.*$",
        r"^#+\s*Gemeinsame Kommissionen.*$",
        r"^#+\s*Akademischer Senat.*$",
        r"^#+\s*Artikel\s+[IVX\d]+.*$",
        r"^#+\s*Bekanntmachungen.*$",
        r"Aufgrund von §.*?(GVBl\.|BerlHG).*?erlassen",
        r"^#+\s*[IVX]+\.?\s*Allgemeiner Teil.*$",
        r"^#+\s*[IVX]+\.?\s*Ziele und Ausgestaltung.*$",
        r"^#+\s*[IVX]+\.?\s*Anforderung und Durchführung.*$",
        r"^#+\s*[IVX]+\.?\s*Anlage(n)?.*$",
        r"^#*\s*I\s+n\s+h\s+a\s+l\s+t.*$",
        r"^Anlage \d+.*Studienverlaufsplan.*$",
        r"^\s*\d{1,3}\s*$" # Einsame Seitenzahlen
    ]
    
    for pattern in line_patterns:
        content = re.sub(pattern, "", content, flags=re.IGNORECASE | re.MULTILINE)

    # --- PHASE 2: KOMPLEXE BEREINIGUNG ---
    content = clean_jurist_garbage_safely(content)

    # 2. STRUKTURIERUNG
    lines = content.split('\n')
    cleaned_lines = []
    
    h2_keywords = [
        "Modulliste", "Studienplan", "Anlage 1", "Anlage 2", "Anlage 3", 
        "Masterarbeit", "Bachelorarbeit", "Zeugnis", "Abschlussarbeit",
        "Ziele", "Prüfung", "Studienumfang",
        "Gliederung", "Akademischer Grad", "Zugangsvoraussetzungen", 
        "Zulassungsantrag", "Auswahlkriterien", "Auswahlverfahren", "Sprachkenntnisse",
        "Pflichtbereich", "Wahlpflichtbereich", "Wahlbereich", "Praktikum",
        "Modulbeschreibung", "Gebühren"
    ]

    target_degree = metadata['degree'].lower() if metadata['degree'] else ""
    
    skip_section = False
    last_line_content = ""
    seen_headers = set()

    sections_to_skip_strict = [
        "Inkrafttreten", "Außerkrafttreten", "Geltungsbereich", 
        "Exemplarischer Studienverlaufsplan", "Studienverlaufsplan",
        "Inhaltsverzeichnis", "Inhalt",
        "Bekanntmachungen", "Vereinigungen",
        "Formular zur Feststellung"
    ]

    doc_splitters = [
        "Zugangs- und Zulassungsordnung", "Neufassung", "Verordnung über die Ausbildung", 
        "Satzung zur Erhebung von Gebühren", "Zulassungsordnung", 
        "Studienordnung für", "Prüfungsordnung für"
    ]
    
    amendment_triggers = ["Änderungssatzung", "Änderung der Studien", "Berichtigung"]

    for line in lines:
        stripped = line.strip()
        
        if len(stripped) < 2 or stripped == last_line_content:
            continue
        last_line_content = stripped

        # --- HEADER LOGIK ---
        is_header = stripped.startswith("#") or (stripped.startswith("**") and stripped.endswith("**"))
        
        if is_header:
            header_text = stripped.replace("#", "").replace("*", "").strip()
            
            if len(header_text) < 3: 
                continue

            should_skip = any(bad_word.lower() in header_text.lower() for bad_word in sections_to_skip_strict)
            is_fakultaet = "fakultäten" in header_text.lower()
            is_module_list = "modul" in header_text.lower()
            
            if (should_skip or is_fakultaet) and not is_module_list:
                skip_section = True
                continue 
            else:
                skip_section = False
            
            if header_text in seen_headers:
                 continue 
            seen_headers.add(header_text)

            is_keyword = any(kw.lower() in header_text.lower() for kw in h2_keywords)
            if is_keyword:
                cleaned_lines.append(f"## {header_text}")
            else:
                cleaned_lines.append(f"### {header_text}")
            
            continue

        if skip_section:
            continue

        # --- TOC HEURISTIK ---
        if re.match(r"^§\s*\d+.*(\.{3,}|\d+\s*$)", stripped):
             continue
             
        if (stripped.startswith("-") or stripped.startswith("*")) and "§" in stripped:
            if len(stripped) < 100 and not stripped.endswith(".") and not stripped.endswith(":"):
                if re.search(r"[-*]\s*(?:(?:\*\*|__)?§(?:\*\*|__)?)\s*\d+", stripped):
                    continue

        # --- NEUE DOKUMENTE / UPDATES ---
        is_splitter = any(x in stripped for x in doc_splitters)
        is_amendment = any(x in stripped for x in amendment_triggers)

        if (is_splitter or is_amendment) and len(stripped) < 150:
            cleaned_lines.append("\n\n" + "="*80)
            
            clean_title = stripped.replace("|", "").strip()
            
            if is_amendment:
                cleaned_lines.append(f"## UPDATE-DOKUMENT: {clean_title}")
                cleaned_lines.append("> ⚠️ ACHTUNG: DIES IST EINE ÄNDERUNGSSATZUNG ODER BERICHTIGUNG.")
                cleaned_lines.append("> DIESE INFORMATIONEN SIND NEUER UND ÜBERSCHREIBEN VORHERIGE TEILE.")
            else:
                cleaned_lines.append(f"## NEUES DOKUMENT: {clean_title}")
            
            cleaned_lines.append("="*80 + "\n")
            skip_section = False 
            seen_headers.clear()
            continue

        cleaned_lines.append(stripped)

    cleaned_content = "\n".join(cleaned_lines)
    cleaned_content = re.sub(r"\n{3,}", "\n\n", cleaned_content)

    return header_block + cleaned_content

def process_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f">>> Starte Verarbeitung in: {os.path.abspath(input_dir)}")
    print(f">>> Ausgabe nach: {output_dir}")

    files = [f for f in os.listdir(input_dir) if f.endswith(".md") and not f.startswith("merged_") and not f.startswith("Stupos_")]
    files.sort()

    if not files:
        print("!!! KEINE MARKDOWN-DATEIEN GEFUNDEN !!!")
        return

    print(f">>> Gefundene Dateien: {len(files)}")

    files_per_chunk = 15
    chunks = [files[i:i + files_per_chunk] for i in range(0, len(files), files_per_chunk)]
    
    for i, chunk in enumerate(chunks):
        merged_content = ""
        chunk_name = f"Stupos_Sammeldatei_{i+1:02d}.md"
        print(f">>> Erstelle Paket {i+1}: {chunk_name}")
        
        start_time = time.time()
        for filename in chunk:
            filepath = os.path.join(input_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    raw = f.read()
                
                meta = parse_metadata(filename)
                clean = clean_content(raw, meta)
                
                merged_content += clean
                merged_content += "\n\n" + ("-"*40) + "\n\n"
            except Exception as e:
                print(f"  ! Fehler bei {filename}: {e}")
        
        print(f"    -> Fertig in {time.time() - start_time:.2f} Sekunden.")

        with open(os.path.join(output_dir, chunk_name), "w", encoding="utf-8") as f:
            f.write(merged_content)
        
    print(">>> FERTIG!")

if __name__ == "__main__":
    process_files(".", "_CLEANED_FOR_GPT") 