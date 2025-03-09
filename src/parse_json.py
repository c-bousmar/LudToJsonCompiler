import os
import re
import json
from tqdm import tqdm

DATA_PROCESSED_DIR = 'data/processed/'
DATA_JSON_DIR = 'data/json/'

METADATA_MARKER = '(metadata'
DEFINE_MARKER = '(define'
GAME_MARKER = '(game'
OPTION_MARKER = '(option'
RULESETS_MARKER = '(rulesets'
RULESET_MARKER = '(ruleset'
ITEM_MARKER = '(item'
SPLITTER_MARKER = '#------------------------------------------------------------------------------'

COMMENT_PATTERN = re.compile(r'//.*')
DEFINE_PATTERN = re.compile(r'\(define\s+"(.*?)"\s*', re.DOTALL)
RULESET_PATTERN = re.compile(r'\(ruleset\s+"(.*?)"\s*\{(.*?)\}\)', re.DOTALL)
OPTION_HEADER_PATTERN = re.compile(r'"([^"]+)"\s*<([^>]+)>')
ITEM_PATTERN = re.compile(r'\(item\s+"(.*?)"\s*<(.*?)>\s*"(.*?)"\)', re.DOTALL)


def extract_balanced_parentheses(text, start_index):
    stack = []
    index = start_index

    while index < len(text) and text[index].isspace():
        index += 1

    if text[index] != "(":
        return None, start_index

    start_body = index
    stack.append("(")
    index += 1

    while index < len(text):
        char = text[index]
        if char == "(":
            stack.append("(")
        elif char == ")":
            stack.pop()
            if not stack:
                return text[start_body:index + 1].strip(), index + 1
        index += 1
    return None, start_index

def handle_define_section(stripped_section, json_structure):
    define_sections = [DEFINE_MARKER + part for part in stripped_section.split(DEFINE_MARKER) if part.strip()]
    
    for define_section in define_sections:
        name_match = DEFINE_PATTERN.search(define_section)
        if name_match:
            name = name_match.group(1).strip()
            start_index = name_match.end()

            if start_index >= len(define_section):
                continue

            body, _ = extract_balanced_parentheses(define_section, start_index)
            if body:
                json_structure["define"][name] = body.strip()



def handle_items(section, json_structure):
    items = [ITEM_MARKER + part for part in section.split(ITEM_MARKER) if part.strip()]
    for item in items:
        item_match = ITEM_PATTERN.match(item.strip())
        if item_match:
            name, content, description = item_match.groups()
            json_structure["items"][name] = {
                "content": content.strip(),
                "description": description.strip()
            }

def handle_option_section(stripped_section, json_structure):
    option_sections = [OPTION_MARKER + part for part in stripped_section.split(OPTION_MARKER) if part.strip()]
    for opt in option_sections:
        opt_cleaned = opt[len(OPTION_MARKER):].rstrip(')').strip()
        parts = opt_cleaned.split('args:', 1)
        
        header_part, body_part = parts
        header_match = OPTION_HEADER_PATTERN.search(header_part.strip())
        
        title, _ = header_match.groups()
        body_part = body_part.strip()
        
        arg_start = body_part.find('{')
        arg_end = body_part.find('}')
        
        arguments = body_part[arg_start + 1:arg_end].lstrip('{').rstrip('}').strip()
        items_part = body_part[arg_end + 1:].strip().lstrip('{').rstrip('}').strip()

        json_structure["option"][title.strip()] = {
            "arguments": arguments,
            "items": {}
        }
        handle_items(items_part, json_structure["option"][title.strip()])

def handle_rulesets_section(stripped_section, json_structure):
    rulesets_content = stripped_section[len(RULESETS_MARKER):-1].strip()[1:-1].strip()
    ruleset_sections = [RULESET_MARKER + part for part in rulesets_content.split(RULESET_MARKER) if part.strip()]
    
    for ruleset_section in ruleset_sections:
        ruleset_match = RULESET_PATTERN.match(ruleset_section.rstrip(')'))
        if ruleset_match:
            raw_name, raw_content = ruleset_match.groups()
            
            name = raw_name.replace("Ruleset/", "").strip()
            
            key_value_pairs = [pair.strip().strip('"').split("/") for pair in raw_content.split('" ') if "/" in pair]
            
            parsed_content = {kv[0].strip(): kv[1].strip() for kv in key_value_pairs}
            
            json_structure["rulesets"][name] = parsed_content



def handle_game_section(stripped_section, json_structure):
    json_structure["game"] = stripped_section[len(GAME_MARKER):].rstrip(')').strip()

def handle_metadata_section(stripped_section, json_structure):
    json_structure["metadata"] = stripped_section[len(METADATA_MARKER):].rstrip(')').strip()

def parse_to_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    sections = re.split(SPLITTER_MARKER, content)
    
    json_structure = {
        "define": {},
        "game": {},
        "option": {},
        "rulesets": {},
        "metadata": {}
    }
    
    for section in sections:
        stripped_section = re.sub(r'\s+', ' ', section).strip()
        
        if re.sub(r'\s+', '', stripped_section).startswith(DEFINE_MARKER):
            handle_define_section(stripped_section, json_structure)
        elif re.sub(r'\s+', '', stripped_section).startswith(OPTION_MARKER):
            handle_option_section(stripped_section, json_structure)
        elif re.sub(r'\s+', '', stripped_section).startswith(RULESETS_MARKER):
            handle_rulesets_section(stripped_section, json_structure)
        elif re.sub(r'\s+', '', stripped_section).startswith(GAME_MARKER):
            handle_game_section(stripped_section, json_structure)
        elif re.sub(r'\s+', '', stripped_section).startswith(METADATA_MARKER):
            handle_metadata_section(stripped_section, json_structure)
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_file = os.path.join(output_path, f"{base_name}.json")
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(json_structure, file, indent=4)

def main(file="all"):

    if file == "all":
        if not os.path.exists(DATA_JSON_DIR):
            os.makedirs(DATA_JSON_DIR)
        
        txt_files = [f for f in os.listdir(DATA_PROCESSED_DIR) if f.endswith('.txt')]
        
        with tqdm(total=len(txt_files), desc="Generating JSON files") as progress_bar:
            for filename in txt_files:
                input_path = os.path.join(DATA_PROCESSED_DIR, filename)
                parse_to_json(input_path, DATA_JSON_DIR)
                progress_bar.update(1)
    else:
        if not os.path.exists(DATA_JSON_DIR):
            os.makedirs(DATA_JSON_DIR)

        print(f"Parsing file: {file}.txt...")
        input_path = os.path.join(DATA_PROCESSED_DIR, f"{file}.txt")
        parse_to_json(input_path, DATA_JSON_DIR)
        print("Parsing completed.")

if __name__ == "__main__":
    main()
