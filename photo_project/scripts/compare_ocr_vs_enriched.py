import pandas as pd
import os

OCR_CSV_PATH = os.path.abspath('dev_data/record_catalog/data/ocr_texts.csv')
ENRICHED_CSV_PATH = os.path.abspath('dev_data/record_catalog/data/enriched_metadata.csv')
OUTPUT_CSV_PATH = os.path.abspath('dev_data/record_catalog/data/ocr_enriched_comparison.csv')


def compare_ocr_vs_enriched(ocr_csv, enriched_csv, output_csv):
    ocr_df = pd.read_csv(ocr_csv)
    enriched_df = pd.read_csv(enriched_csv)

    if 'filename' not in ocr_df.columns:
        for col in ocr_df.columns:
            if 'filename' in col.lower():
                ocr_df.rename(columns={col: 'filename'}, inplace=True)
                break
    if 'filename' not in enriched_df.columns:
        for col in enriched_df.columns:
            if 'filename' in col.lower():
                enriched_df.rename(columns={col: 'filename'}, inplace=True)
                break

    merged_df = pd.merge(ocr_df, enriched_df, on='filename', suffixes=('_OCR', '_Enriched'))

    fields = ['Title', 'Artist', 'Label', 'Catalog Number', 'Year', 'Notes']

    selected_cols = ['filename']
    for f in fields:
        if f + '_OCR' in merged_df.columns and f + '_Enriched' in merged_df.columns:
            selected_cols.extend([f + '_OCR', f + '_Enriched'])

    print('Selected columns for comparison:', selected_cols)

    comparison_df = merged_df[selected_cols]

    print(comparison_df.info())
    print(comparison_df.head(20).to_string(index=False))

    comparison_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f'Comparison saved to {output_csv}')


if __name__ == '__main__':
    if not os.path.exists(OCR_CSV_PATH):
        print(f"OCR CSV not found at {OCR_CSV_PATH}. Please run OCR extraction step first.")
    elif not os.path.exists(ENRICHED_CSV_PATH):
        print(f"Enriched CSV not found at {ENRICHED_CSV_PATH}. Please run enrichment step first.")
    else:
        compare_ocr_vs_enriched(OCR_CSV_PATH, ENRICHED_CSV_PATH, OUTPUT_CSV_PATH)
