import asyncio
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..core.models import SearchFilters, Sale
from ..core.scraper import GrailedScraper

console = Console()


class CLI:
    def __init__(self):
        self.scraper = GrailedScraper()

    def _get_filters_from_input(self) -> SearchFilters:
        filters = SearchFilters()

        try:
            add_filters = console.input("Would you like to add search filters? [y/n] (n): ").lower()
            if add_filters != 'y':
                return filters

            min_price = console.input("Minimum price (press Enter to skip): ")
            if min_price:
                filters.min_price = float(min_price)

            max_price = console.input("Maximum price (press Enter to skip): ")
            if max_price:
                filters.max_price = float(max_price)

            designers = console.input("Designers (comma-separated, press Enter to skip): ")
            if designers:
                filters.designers = [d.strip() for d in designers.split(',') if d.strip()]

            conditions = console.input("Conditions (comma-separated, press Enter to skip): ")
            if conditions:
                filters.conditions = [c.strip() for c in conditions.split(',') if c.strip()]

            console.print(f"Searching with filters: {filters}")

        except ValueError as e:
            console.print(f"[red]Invalid input: {str(e)}[/red]")
            return SearchFilters()

        return filters

    def _format_sale(self, sale: Sale) -> str:
        lines = [
            f"\n[bold]{sale.title}[/bold]",
            f"Price: [green]${sale.price:.2f}[/green]"
        ]

        if sale.discount and sale.discount_percentage:
            lines.append(
                f"Original: [red]${sale.original_price:.2f}[/red] "
                f"([red]{sale.discount_percentage:.1f}% off[/red])"
            )

        lines.extend([
            f"Designer: [cyan]{sale.designer}[/cyan]",
            f"Size: {sale.size}",
            f"Condition: [yellow]{sale.condition}[/yellow]",
            f"Location: {sale.location}",
            f"Seller: {sale.seller}",
            f"[link={sale.url}]View on Grailed[/link]"
        ])

        return "\n".join(lines)

    async def run(self):
        console.print("[bold]Grailed Sales Monitor[/bold]")
        console.print("Enter search terms to monitor sales. Type 'quit' to exit.")

        try:
            while True:
                try:
                    query = console.input("\nEnter search term: ").strip()
                    if query.lower() in ('quit', 'exit', 'q'):
                        break

                    if not query:
                        console.print("[red]Search term cannot be empty[/red]")
                        continue

                    filters = self._get_filters_from_input()

                    with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            console=console
                    ) as progress:
                        progress.add_task("Fetching search URL...", total=None)
                        listings = await self.scraper.search_listings(query, filters)

                    if not listings:
                        console.print("\nNo sales found. Suggestions:")
                        console.print("• Try different search terms")
                        console.print("• Broaden your price range")
                        console.print("• Remove some filters")
                        console.print("• Check spelling of designer names")
                        continue

                    console.print(f"\nFound {len(listings)} listings:")

                    for listing in listings[:5]:
                        console.print(self._format_sale(listing))

                    continue_search = console.input("\nWould you like to search again? [y/n] (y): ").lower()
                    if continue_search == 'n':
                        break

                except Exception as e:
                    console.print(f"[red]Error during search: {str(e)}[/red]")
                    continue

        finally:
            await self.scraper.close()


def main():
    """Entry point for the CLI"""
    cli = CLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()