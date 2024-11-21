# TheWatch/data/exporters.py
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

from TheWatch.core.models import Sale
from TheWatch.utils.logger import setup_logger

logger = setup_logger(__name__)


class SalesExporter:
    """Handles exporting sales data to various formats"""

    def __init__(self, output_dir: str = "data/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_csv(self, sales: List[Sale], query: str) -> str:
        """Export sales to a CSV file with proper formatting"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"sales_{query.replace(' ', '_')}_{timestamp}.csv"

        headers = [
            'Title',
            'Designer',
            'Price ($)',
            'Original Price ($)',
            'Discount (%)',
            'Condition',
            'Location',
            'Size',
            'Sale Date',
            'URL',
            'Platform'
        ]

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for sale in sales:
                    # Calculate discount percentage
                    if sale.original_price > sale.price:
                        discount = f"{((sale.original_price - sale.price) / sale.original_price * 100):.1f}"
                    else:
                        discount = "0.0"

                    row = [
                        sale.title,
                        sale.designer_display,
                        f"{sale.price:.2f}",
                        f"{sale.original_price:.2f}",
                        discount,
                        sale.condition_display,
                        sale.location or 'Unknown',
                        sale.size,
                        sale.sold_date.strftime('%Y-%m-%d %H:%M:%S'),
                        sale.url,
                        sale.platform
                    ]
                    writer.writerow(row)

            logger.info(f"Successfully exported {len(sales)} sales to CSV: {filename}")
            return str(filename)

        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise

    def export_excel(self, sales: List[Sale], query: str) -> str:
        """Export sales to Excel with formatting"""
        try:
            import pandas as pd
            import openpyxl
            from openpyxl.styles import PatternFill, Font, Alignment

            # Convert sales to DataFrame
            data = []
            for sale in sales:
                # Calculate discount
                if sale.original_price > sale.price:
                    discount = ((sale.original_price - sale.price) / sale.original_price * 100)
                else:
                    discount = 0.0

                data.append({
                    'Title': sale.title,
                    'Designer': sale.designer_display,
                    'Price ($)': sale.price,
                    'Original Price ($)': sale.original_price,
                    'Discount (%)': discount,
                    'Condition': sale.condition_display,
                    'Location': sale.location or 'Unknown',
                    'Size': sale.size,
                    'Sale Date': sale.sold_date,
                    'URL': sale.url,
                    'Platform': sale.platform
                })

            df = pd.DataFrame(data)

            # Create Excel file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.output_dir / f"sales_{query.replace(' ', '_')}_{timestamp}.xlsx"

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sales Data')

                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Sales Data']

                # Format headers
                header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                header_font = Font(color='FFFFFF', bold=True)

                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')

                # Adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column = list(column)
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Cap width at 50
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

            logger.info(f"Successfully exported {len(sales)} sales to Excel: {filename}")
            return str(filename)

        except ImportError:
            logger.warning("Excel export requires pandas and openpyxl. Falling back to CSV.")
            return self.export_csv(sales, query)
        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            raise