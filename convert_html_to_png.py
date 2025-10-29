"""
Convert PyEcharts HTML files to PNG images
Requires: pip install selenium pillow
For headless Chrome: pip install webdriver-manager
"""

import os
import glob
import time
from pathlib import Path
from typing import Optional

# Configuration
PNG_OUTPUT_DIR = "chart_pngs"  # All PNGs will be saved here
CHART_WIDTH = 1280
CHART_HEIGHT = 720

# Check if selenium is available
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not installed. Install with: pip install selenium webdriver-manager")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow not installed. Install with: pip install pillow")


def setup_chrome_driver():
    """Setup Chrome driver in headless mode."""
    if not SELENIUM_AVAILABLE:
        return None
        
    try:
        # Try using webdriver_manager for automatic driver management
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Set a larger window to ensure full chart capture
        options.add_argument(f'--window-size={CHART_WIDTH+200},{CHART_HEIGHT+200}')
        # Force device scale factor to 1
        options.add_argument('--force-device-scale-factor=1')
        # Disable scrollbars
        options.add_argument('--hide-scrollbars')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
        
    except Exception as e:
        print(f"Using default Chrome driver: {e}")
        
        # Fallback to default Chrome
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Set a larger window to ensure full chart capture
        options.add_argument(f'--window-size={CHART_WIDTH+200},{CHART_HEIGHT+200}')
        # Force device scale factor to 1
        options.add_argument('--force-device-scale-factor=1')
        # Disable scrollbars
        options.add_argument('--hide-scrollbars')
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e2:
            print(f"❌ Failed to setup Chrome driver: {e2}")
            return None


def convert_html_to_png(html_file: str, output_file: Optional[str] = None) -> bool:
    """Convert a single HTML file to PNG in the centralized output directory."""
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available")
        return False
        
    # Ensure output directory exists
    os.makedirs(PNG_OUTPUT_DIR, exist_ok=True)
    
    if not output_file:
        # Generate output filename in the centralized directory
        # Extract the base name and any parent folder info
        base_name = os.path.basename(html_file).replace('.html', '.png')
        # Include parent folder name if it exists (e.g., Bar_chart1.png)
        parent_folder = os.path.basename(os.path.dirname(html_file))
        if parent_folder and parent_folder not in ['.', '', 'dump_generation']:
            output_file = os.path.join(PNG_OUTPUT_DIR, f"{parent_folder}_{base_name}")
        else:
            output_file = os.path.join(PNG_OUTPUT_DIR, base_name)
    
    driver = None
    try:
        driver = setup_chrome_driver()
        if not driver:
            return False
            
        # Load the HTML file
        file_url = f"file://{os.path.abspath(html_file)}"
        driver.get(file_url)
        
        # Wait for chart to render (PyEcharts uses canvas)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "canvas"))
            )
            time.sleep(2)  # Extra wait for animations
        except:
            time.sleep(3)  # Fallback wait
        
        # Inject JavaScript to ensure the chart is fully visible
        driver.execute_script("""
            // Find the chart container
            var chartContainers = document.querySelectorAll('.chart-container');
            if (chartContainers.length > 0) {
                var container = chartContainers[0];
                // Set container to exact dimensions
                container.style.width = '1280px';
                container.style.height = '720px';
                // Remove any margins or padding from body
                document.body.style.margin = '0';
                document.body.style.padding = '0';
                document.body.style.overflow = 'hidden';
                // Ensure chart is at top-left
                container.style.position = 'absolute';
                container.style.top = '0';
                container.style.left = '0';
            }
            
            // Also handle the main div with chart ID
            var divs = document.querySelectorAll('div[id]');
            for (var i = 0; i < divs.length; i++) {
                var div = divs[i];
                if (div.id && div.id.length === 32) {  // PyEcharts generates 32-char IDs
                    div.style.width = '1280px';
                    div.style.height = '720px';
                    div.style.position = 'absolute';
                    div.style.top = '0';
                    div.style.left = '0';
                }
            }
            
            // Force ECharts to resize
            if (window.echarts) {
                var charts = echarts.getInstanceByDom(document.querySelector('.chart-container') || document.querySelector('div[id]'));
                if (charts) {
                    charts.resize({width: 1280, height: 720});
                }
            }
        """)
        
        # Give it a moment to apply the styles
        time.sleep(1)
        
        # Set window to exact size needed (with small buffer for browser chrome)
        driver.set_window_size(CHART_WIDTH + 50, CHART_HEIGHT + 50)
        
        # Try to find and screenshot just the chart element
        try:
            # Try to find the chart container
            chart_element = driver.find_element(By.CLASS_NAME, "chart-container")
            chart_element.screenshot(output_file)
        except:
            # If no chart container, try to find the main chart div
            try:
                # Find div with 32-character ID (PyEcharts pattern)
                chart_divs = driver.find_elements(By.TAG_NAME, "div")
                for div in chart_divs:
                    div_id = div.get_attribute("id")
                    if div_id and len(div_id) == 32:
                        div.screenshot(output_file)
                        break
                else:
                    # Fallback to full page screenshot
                    driver.save_screenshot(output_file)
            except:
                # Final fallback to full page screenshot
                driver.save_screenshot(output_file)
        
        # Ensure exact dimensions using PIL
        if PIL_AVAILABLE:
            try:
                img = Image.open(output_file)
                
                # Get current dimensions
                width, height = img.size
                
                # If not exactly 1280x720, resize or crop
                if width != CHART_WIDTH or height != CHART_HEIGHT:
                    # Option 1: Crop to exact size (preserves quality)
                    if width >= CHART_WIDTH and height >= CHART_HEIGHT:
                        # Center crop
                        left = (width - CHART_WIDTH) // 2
                        top = (height - CHART_HEIGHT) // 2
                        right = left + CHART_WIDTH
                        bottom = top + CHART_HEIGHT
                        img = img.crop((left, top, right, bottom))
                    else:
                        # Option 2: Resize to fit (may stretch slightly)
                        img = img.resize((CHART_WIDTH, CHART_HEIGHT), Image.Resampling.LANCZOS)
                
                # Save with high quality
                img.save(output_file, 'PNG', quality=95, optimize=True)
                
            except Exception as e:
                print(f"Warning: Could not optimize image: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting {html_file}: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()


def convert_folder(folder_path: str, pattern: str = "*.html") -> tuple:
    """Convert all HTML files in a folder to PNG in centralized directory."""
    html_files = glob.glob(os.path.join(folder_path, pattern))
    if not html_files:
        html_files = glob.glob(os.path.join(folder_path, "**", pattern), recursive=True)
    
    success_count = 0
    failed_count = 0
    
    print(f"\n📁 Processing {len(html_files)} HTML files from {folder_path}")
    print(f"📂 Saving PNGs to: {os.path.abspath(PNG_OUTPUT_DIR)}")
    
    for i, html_file in enumerate(html_files, 1):
        # Show relative path for clarity
        rel_path = os.path.relpath(html_file, folder_path) if folder_path != "." else os.path.basename(html_file)
        print(f"  [{i}/{len(html_files)}] Converting {rel_path}...", end=" ")
        
        if convert_html_to_png(html_file):
            print("✅")
            success_count += 1
        else:
            print("❌")
            failed_count += 1
    
    return success_count, failed_count


def simple_html_to_png_converter():
    """Alternative converter using simpler approach with requests and imgkit."""
    print("\n" + "=" * 60)
    print("Alternative: Simple HTML to PNG Converter")
    print("=" * 60)
    print(f"""
    For a simpler approach without Selenium, you can use:
    
    1. Install wkhtmltopdf:
       - Ubuntu/Debian: sudo apt-get install wkhtmltopdf
       - macOS: brew install wkhtmltopdf
       - Windows: Download from https://wkhtmltopdf.org/
    
    2. Install Python package:
       pip install imgkit
    
    3. Use this code:
    
    import imgkit
    import os
    
    os.makedirs('{PNG_OUTPUT_DIR}', exist_ok=True)
    
    options = {{
        'width': {CHART_WIDTH},
        'height': {CHART_HEIGHT},
        'quality': 100
    }}
    
    imgkit.from_file('chart.html', '{PNG_OUTPUT_DIR}/chart.png', options=options)
    """)


def main():
    """Main conversion pipeline."""
    print("🖼️ HTML to PNG Converter for PyEcharts")
    print("=" * 60)
    print(f"📐 Target dimensions: {CHART_WIDTH}×{CHART_HEIGHT} pixels")
    print(f"📂 Output directory: {os.path.abspath(PNG_OUTPUT_DIR)}")
    print("=" * 60)
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium is required for conversion")
        print("Install with: pip install selenium webdriver-manager")
        simple_html_to_png_converter()
        return
    
    # Ensure output directory exists
    os.makedirs(PNG_OUTPUT_DIR, exist_ok=True)
    
    # Default folder to convert
    dump_folder = "./dump_generation"
    
    if os.path.exists(dump_folder):
        print(f"📂 Converting charts from: {dump_folder}")
        
        total_success = 0
        total_failed = 0
        
        # Convert each subfolder
        for chart_type in os.listdir(dump_folder):
            folder_path = os.path.join(dump_folder, chart_type)
            if os.path.isdir(folder_path):
                success, failed = convert_folder(folder_path)
                total_success += success
                total_failed += failed
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Conversion Complete!")
        print(f"✅ Successfully converted: {total_success} files")
        print(f"❌ Failed conversions: {total_failed} files")
        print(f"📂 All PNGs saved to: {os.path.abspath(PNG_OUTPUT_DIR)}")
        print(f"📐 All images: {CHART_WIDTH}×{CHART_HEIGHT} pixels")
        print("=" * 60)
        
    else:
        print(f"❌ Folder not found: {dump_folder}")
        print("Run generate_chart_pipeline.py first to generate charts")
        
        # Try current directory as fallback
        print("\nTrying current directory...")
        success, failed = convert_folder(".", "*.html")
        
        if success > 0:
            print(f"\n✅ Converted {success} files")
            print(f"📂 Saved to: {os.path.abspath(PNG_OUTPUT_DIR)}")


if __name__ == "__main__":
    # Check command line arguments
    import sys
    if len(sys.argv) > 1:
        # Convert specific file or folder
        path = sys.argv[1]
        
        # Ensure output directory exists
        os.makedirs(PNG_OUTPUT_DIR, exist_ok=True)
        
        if os.path.isfile(path) and path.endswith('.html'):
            print(f"📄 Converting single file: {path}")
            print(f"📂 Output directory: {os.path.abspath(PNG_OUTPUT_DIR)}")
            print(f"📐 Target size: {CHART_WIDTH}×{CHART_HEIGHT} pixels")
            if convert_html_to_png(path):
                output_name = os.path.basename(path).replace('.html', '.png')
                print(f"✅ Saved as: {PNG_OUTPUT_DIR}/{output_name}")
            else:
                print("❌ Conversion failed")
        elif os.path.isdir(path):
            print(f"📁 Converting folder: {path}")
            print(f"📂 Output directory: {os.path.abspath(PNG_OUTPUT_DIR)}")
            print(f"📐 Target size: {CHART_WIDTH}×{CHART_HEIGHT} pixels")
            success, failed = convert_folder(path)
            print(f"\n✅ Converted {success}/{success+failed} files")
            print(f"📂 All PNGs saved to: {os.path.abspath(PNG_OUTPUT_DIR)}")
        else:
            print(f"❌ Invalid path: {path}")
    else:
        main()
