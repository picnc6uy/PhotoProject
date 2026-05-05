import os
import pandas as pd
import openai
import time

# Set OpenAI API key via environment variable or hardcode here (not recommended)
openai.api_key = os.getenv("OPENAI_API_KEY")

OCR_CSV_PATH = r"dev_data\record_catalog\data\inbox_photos_desc\image_descriptions_ocr.csv"
PARSED_OCR_CSV_PATH = r"dev_data\record_catalog\data\outputs\parsed_ocr_openai.csv"

def parse_ocr_with_openai(ocr_text):
    prompt = f\"\"\"Extract the following info from the record label OCR text below.

Fields to extract: Title, Artist, Label, Catalog Number, Format, Year, Notes.

OCR Text:
\"\"\"{ocr_text}

\"\"\"Provide JSON output with these fields. If a field cannot be found, set it to null.\"\"\"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.0,
        )
        content = response.choices[0].message['content']
        return content  # JSON text as string, parse later
    except Exception as e:
        print(f\"OpenAI API error: {e}\")
        return None

def main():
    df = pd.read_csv(OCR_CSV_PATH)
    results = []

    for idx, row in df.iterrows():
        filename = row['filename']
        ocr_text = row['ocr_text']

        print(f\"Processing OCR for: {filename} ({idx + 1}/{len(df)})\")

        json_text = parse_ocr_with_openai(ocr_text if isinstance(ocr_text, str) else "")
        if json_text is None:
            json_text = '{}'

        results.append({
            "filename": filename,
            "parsed_json": json_text,
            "ocr_text": ocr_text,
        })

        time.sleep(1)  # rate limiting

    parsed_df = pd.DataFrame(results)
    parsed_df.to_csv(PARSED_OCR_CSV_PATH, index=False)
    print(f\"Saved parsed OCR metadata to {PARSED_OCR_CSV_PATH}\")

if __name__ == "__main__":
    main()