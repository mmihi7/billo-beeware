"""
Main entry point for the Billo mobile application.
"""
import os
import sys
import logging
from pathlib import Path

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Launch the Billo mobile application."""
    try:
        # Set up paths
        app_dir = Path(__file__).parent.absolute()
        sys.path = [str(app_dir)] + sys.path
        
        logger.info(f"Python path: {sys.path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        
        # Import toga first to ensure it's available
        try:
            import toga
            from toga.style import Pack
            from toga.style.pack import COLUMN, ROW, CENTER
            logger.info(f"Toga version: {getattr(toga, '__version__', 'N/A')}")
        except ImportError as e:
            logger.error("Failed to import Toga. Please ensure it's installed in your environment.")
            logger.error(f"Error details: {str(e)}")
            raise
            
        # Import app after Toga is confirmed available
        from .app import Billo
        
        # Create and run the app
        logger.info("Creating Billo app instance...")
        app = Billo(
            formal_name="Billo",
            app_id="com.billo.mobile"
        )
        logger.info("Starting main loop...")
        return app.main_loop()
        
    except Exception as e:
        logger.exception("Fatal error in main()")
        raise

if __name__ == "__main__":
    main()
