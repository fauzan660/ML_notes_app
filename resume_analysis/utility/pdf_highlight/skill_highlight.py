from .highlight import process_file

def pdf_highlight(simple_pdf_path, search_terms_list):
    try:
        output_path = process_file(
            input_file=simple_pdf_path,
            output_file=None,
            search_str=search_terms_list,
            action="Highlight"
        )
        return output_path
    except Exception as e:
        print(f"Error highlighting PDF: {e}")
        return None