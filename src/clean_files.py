import os
import re
from tqdm import tqdm

DATA_RAW_DIR = 'data/raw/'
DATA_PROCESSED_DIR = 'data/processed/'
SPLITTER_PATTERN = re.compile(r'//-+')
SPLITTER_MARKER = '#------------------------------------------------------------------------------'
COMMENT_PATTERN = re.compile(r'//.*')
DEFINE_PATTERN = re.compile(r'\(define\s+"(.*?)"\s*\((.*?)\)\)', re.DOTALL)

def clean_lud_file(input_path, output_path, progress_bar):
    with open(input_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    cleaned_sections = re.split(SPLITTER_PATTERN, content)
    content = SPLITTER_MARKER.join(cleaned_sections)
    
    cleaned_lines = [re.sub(COMMENT_PATTERN, '', line) for line in content.splitlines()]
    cleaned_content = '\n'.join(cleaned_lines)
    
    with open(os.path.join(output_path, f"{os.path.splitext(os.path.basename(input_path))[0]}.txt"), 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

    if progress_bar:
        progress_bar.update(1)


def main(file="all"):

    if file == "all":

        if not os.path.exists(DATA_PROCESSED_DIR):
            os.makedirs(DATA_PROCESSED_DIR)
        
        lud_files = [f for f in os.listdir(DATA_RAW_DIR) if f.endswith('.lud')]
        
        with tqdm(total=len(lud_files), desc="Cleaning .lud files") as progress_bar:
            for filename in lud_files:
                input_path = os.path.join(DATA_RAW_DIR, filename)
                clean_lud_file(input_path, DATA_PROCESSED_DIR, progress_bar)
    else:
        print(f"Cleaning file: {file}.lud...")
        input_path = os.path.join(DATA_RAW_DIR, f"{file}.lud")
        clean_lud_file(input_path, DATA_PROCESSED_DIR, None)
        print("Cleaning completed.")

if __name__ == "__main__":
    main()
