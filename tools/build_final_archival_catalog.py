from pathlib import Path

from record_catalog.final_exporter import (
    build_final_archival_catalog,
    build_final_total_catalog,
    write_catalog_validation_report,
)


if __name__ == '__main__':
    workspace = Path(r'C:/Users/ghendrick/PhotoProject')
    input_csv = workspace / 'dev_data' / 'record_catalog' / 'data' / 'outputs' / 'enriched_resolved.csv'
    output_csv = workspace / 'dev_data' / 'record_catalog' / 'data' / 'outputs' / 'final_archival_catalog_consolidated.csv'
    build_final_archival_catalog(str(input_csv), str(output_csv), consolidate=True)
    print(f'Wrote final archival catalog to {output_csv}')
    total_csv = workspace / 'dev_data' / 'record_catalog' / 'data' / 'outputs' / 'final_total_catalog.csv'
    build_final_total_catalog(str(input_csv), str(total_csv))
    print(f'Wrote final total catalog to {total_csv}')
    report_csv = workspace / 'dev_data' / 'record_catalog' / 'data' / 'outputs' / 'catalog_validation_report.csv'
    write_catalog_validation_report(str(output_csv), str(report_csv))
    print(f'Wrote catalog validation report to {report_csv}')
