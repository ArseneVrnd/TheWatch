# TheWatch/ui/display.py
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from TheWatch.core.models import Sale, SalesAnalytics
from TheWatch.utils.logger import setup_logger

logger = setup_logger(__name__)


class SalesDisplay:
    """Handles terminal display of sales data"""

    def __init__(self):
        self.console = Console()

    def print_sale(self, sale: Sale) -> None:
        """Display a single sale in a formatted panel"""
        content = [
            Text(f"[bold]{sale.title}[/bold]"),
            Text(f"Price: [green]${sale.price:,.2f}[/green]"),
        ]

        if sale.discount_percentage:
            content.append(Text(
                f"Original: [red]${sale.original_price:,.2f}[/red] "
                f"([red]{sale.discount_percentage:.1f}% off[/red])"
            ))

        content.extend([
            Text(f"Designer: [cyan]{sale.designer_display}[/cyan]"),
            Text(f"Condition: [yellow]{sale.condition_display}[/yellow]"),
            Text(f"Location: {sale.location or 'Unknown'}"),
            Text(f"[link={sale.url}]View on Grailed[/link]")
        ])

        panel = Panel(
            "\n".join(str(line) for line in content),
            title=f"Sale from {sale.sold_date.strftime('%Y-%m-%d')}",
            border_style="blue"
        )
        self.console.print(panel)

    def print_results(self, sales: List[Sale], query: str) -> None:
        """Display complete sales results with analytics"""
        if not sales:
            self.console.print(f"[red]No sales found for query: {query}[/red]")
            return

        self.console.print(f"\n[green]Found {len(sales)} sales for '{query}'[/green]\n")

        # Print analytics if we have sales
        analytics = SalesAnalytics.from_sales(sales)
        if analytics:
            self.print_analytics(analytics)

        # Print most recent sales
        self.console.print("\n[bold]Most Recent Sales:[/bold]\n")
        for sale in sorted(sales, key=lambda x: x.sold_date, reverse=True)[:5]:
            self.print_sale(sale)

    def print_progress(self, description: str) -> Progress:
        """Create and return a progress indicator"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )

    def print_analytics(self, analytics: SalesAnalytics) -> None:
        """Display sales analytics in a formatted way"""
        # Overview Table
        overview = Table(title="Sales Overview", show_header=False)
        overview.add_column("Metric", style="cyan")
        overview.add_column("Value", justify="right")

        overview.add_row("Total Sales", str(analytics.total_sales))
        overview.add_row("Total Value", f"${analytics.total_value:,.2f}")
        overview.add_row("Average Price", f"${analytics.average_price:,.2f}")
        overview.add_row("Median Price", f"${analytics.median_price:,.2f}")
        overview.add_row("Price Range", f"${analytics.min_price:,.2f} - ${analytics.max_price:,.2f}")

        self.console.print(overview)
        self.console.print()

        # Create distribution tables
        tables = []

        # Price Ranges
        price_table = Table(title="Price Distribution", show_header=True)
        price_table.add_column("Range")
        price_table.add_column("Count", justify="right")
        price_table.add_column("%", justify="right")

        for range_name, count in analytics.price_ranges.items():
            percentage = (count / analytics.total_sales) * 100
            price_table.add_row(
                range_name,
                str(count),
                f"{percentage:.1f}%"
            )
        tables.append(price_table)

        # Conditions
        condition_table = Table(title="Condition Breakdown", show_header=True)
        condition_table.add_column("Condition")
        condition_table.add_column("Count", justify="right")
        condition_table.add_column("%", justify="right")

        for condition, count in analytics.condition_distribution.items():
            percentage = (count / analytics.total_sales) * 100
            condition_table.add_row(
                condition,
                str(count),
                f"{percentage:.1f}%"
            )
        tables.append(condition_table)

        # Display tables in columns
        self.console.print(Columns(tables))