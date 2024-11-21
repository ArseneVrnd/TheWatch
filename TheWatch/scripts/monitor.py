#!/usr/bin/env python3
import asyncio
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def main():
    """Main entry point"""
    # Your main logic here
    pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("
Script terminated by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        raise
