from typing import Tuple
from io import BytesIO
import os
import argparse
import re
import fitz
import json 

def extract_info(input_file: str):
    pdfDoc = fitz.open(input_file)
    output = {
        "File": input_file, "Encrypted": ("True" if pdfDoc.is_encrypted else "False")
    }

    if not pdfDoc.is_encrypted:
        for key, value in pdfDoc.metadata.items():
            output[key] = value

    print("File Information ##########################################")
    print("\n".join("{}:{}".format(i, j) for i, j in output.items()))
    print("###########################################################")

    return True, output

def search_for_text(lines, search_list):
    matched = []
    for search_str in search_list:
        for line in lines:
            results = re.findall(search_str, line, re.IGNORECASE)
            matched.extend(results)
    return matched


def redact_matching_data(page, matched_values):
    matches_found = 0
    for val in matched_values:
        matches_found += 1
        matching_val_area = page.search_for(val)
        [page.add_redact_annot(area, text=" ", fill=(0, 0, 0)) for area in matching_val_area]
        page.apply_redactions()
    return matches_found

def frame_matching_data(page, matched_values):
    matches_found = 0
    for val in matched_values:
        matches_found += 1
        matching_val_area = page.search_for(val)
        for area in matching_val_area:
            if isinstance(area, fitz.Rect):
                annot = page.add_rect_annot(area)
                annot.set_colors(stroke=fitz.utils.get_color('red'))
                annot.update()
    return matches_found

def highlight_matching_data(page, matched_values, type):
    matches_found = 0
    for val in matched_values:
        matches_found += 1
        matching_val_area = page.search_for(val)
        highlight = None
        if type == 'Highlight':
            highlight = page.add_highlight_annot(matching_val_area)
        elif type == 'Squiggly':
            highlight = page.add_squiggly_annot(matching_val_area)
        elif type == 'Underline':
            highlight = page.add_underline_annot(matching_val_area)
        elif type == 'Strikeout':
            highlight = page.add_strikeout_annot(matching_val_area)
        else:
            highlight = page.add_highlight_annot(matching_val_area)
        highlight.update()
    return matches_found

def process_data(input_file: str, output_file: str, search_str: str, pages: Tuple = None, action: str = 'Highlight'):
    pdfDoc = fitz.open(input_file)
    output_buffer = BytesIO()
    total_matches = 0

    for pg in range(pdfDoc.page_count):
        if pages and str(pg) not in pages:
            continue

        page = pdfDoc[pg]

        # 🧹 Remove all non-redaction annotations before applying new ones
        annot = page.first_annot
        while annot:
            next_annot = annot.next  # Save reference before deletion
            subtype = annot.type[0]
            if subtype != 12:  # 12 = Redact annotation type in PyMuPDF
                page.delete_annot(annot)
            annot = next_annot

        page_lines = page.get_text("text").split('\n')
        matched_values = list(search_for_text(page_lines, search_str))

        if matched_values:
            if action == 'Redact':
                matches_found = redact_matching_data(page, matched_values)
            elif action == 'Frame':
                matches_found = frame_matching_data(page, matched_values)
            elif action in ('Highlight', 'Squiggly', 'Underline', 'Strikeout'):
                matches_found = highlight_matching_data(page, matched_values, action)
            else:
                matches_found = highlight_matching_data(page, matched_values, 'Highlight')
            total_matches += matches_found

    print(f"{total_matches} Match(es) Found of Search String {search_str} In Input File")
    pdfDoc.save(output_buffer)
    pdfDoc.close()

    with open(output_file, mode='wb') as f:
        f.write(output_buffer.getbuffer())


def remove_highlight(input_file: str, output_file: str, pages: Tuple = None):
    pdfDoc = fitz.open(input_file)
    output_buffer = BytesIO()
    annot_found = 0
    for pg in range(pdfDoc.page_count):
        if pages and str(pg) not in pages:
            continue
        page = pdfDoc[pg]
        annot = page.first_annot
        while annot:
            annot_found += 1
            page.delete_annot(annot)
            annot = annot.next
    if annot_found > 0:
        print(f"Annotation(s) Found In The Input File: {input_file}")
    pdfDoc.save(output_buffer)
    pdfDoc.close()
    with open(output_file, mode='wb') as f:
        f.write(output_buffer.getbuffer())

def process_file(**kwargs):
    input_file = kwargs.get('input_file')
    output_file = kwargs.get('output_file')

    # If output file is not given, create a new one with _highlighted
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_highlighted{ext}"

    search_str = kwargs.get('search_str')
    pages = kwargs.get('pages')
    action = kwargs.get('action')

    if action == "Remove":
        remove_highlight(input_file=input_file, output_file=output_file, pages=pages)
    else:
        process_data(input_file=input_file, output_file=output_file, search_str=search_str, pages=pages, action=action)

    return output_file  # ✅ Important


def process_folder(**kwargs):
    input_folder = kwargs.get('input_folder')
    search_str = kwargs.get('search_str')
    recursive = kwargs.get('recursive')
    action = kwargs.get('action')
    pages = kwargs.get('pages')
    for foldername, dirs, filenames in os.walk(input_folder):
        for filename in filenames:
            if not filename.endswith('.pdf'):
                continue
            inp_pdf_file = os.path.join(foldername, filename)
            print("Processing file=", inp_pdf_file)
            process_file(input_file=inp_pdf_file, output_file=None, search_str=search_str, action=action, pages=pages)
        if not recursive:
            break

def is_valid_path(path):
    if not path:
        raise ValueError(f"Invalid Path")
    if os.path.isfile(path) or os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid Path {path}")

def parse_args():
    parser = argparse.ArgumentParser(description="Available Options")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path, required=True, help="Enter the path of the file or the folder")
    parser.add_argument('-a', '--action', dest='action', choices=['Redact', 'Frame', 'Highlight', 'Squiggly', 'Underline', 'Strikeout', 'Remove'], default='Highlight', help="Choose an action")
    parser.add_argument('-p', '--pages', dest='pages', type=tuple, help="Enter the pages to consider e.g.: [2,4]")
    action = parser.parse_known_args()[0].action
    if action != 'Remove':
        parser.add_argument('-s', '--search_str', dest='search_str', nargs='+', type=str, required=True,
                    help="Enter space-separated strings to highlight (e.g. 'Python Django API')")
    path = parser.parse_known_args()[0].input_path
    if os.path.isfile(path):
        parser.add_argument('-o', '--output_file', dest='output_file', type=str, help="Enter a valid output file")
    if os.path.isdir(path):
        parser.add_argument('-r', '--recursive', dest='recursive', default=False, type=lambda x: str(x).lower() in ['true', '1', 'yes'], help="Process Recursively or Not")
    args = vars(parser.parse_args())
    print("## Command Arguments ####################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    print("#########################################################################")
    return args


if __name__ == '__main__':
    args = parse_args()

    output_path = None
    if os.path.isfile(args['input_path']):
        extract_info(input_file=args['input_path'])
        output_path = process_file(
            input_file=args['input_path'],
            output_file=args.get('output_file'),
            search_str=args['search_str'] if 'search_str' in args else None,
            pages=args['pages'],
            action=args['action']
        )
    elif os.path.isdir(args['input_path']):
        process_folder(
            input_folder=args['input_path'],
            search_str=args['search_str'] if 'search_str' in args else None,
            action=args['action'],
            pages=args['pages'],
            recursive=args['recursive']
        )
        output_path = args['input_path']  # or skip printing anything

    # ✅ Correct output file path to be used in Django
    print(json.dumps({"output_file": output_path}))
