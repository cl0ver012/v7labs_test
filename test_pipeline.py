"""Quick test of the chart generation pipeline - generates 1 chart per type"""

import os
import sys
sys.path.append('.')

from generate_chart_pipeline import (
    TARGET_CHART_TYPES,
    generate_synthetic_data,
    generate_fallback_chart,
    ensure_output_structure
)

def test_pipeline():
    """Test the pipeline with 1 chart per type."""
    print("🧪 Testing Chart Generation Pipeline")
    print("=" * 60)
    print("Generating 1 chart per type for testing...")
    print("")
    
    # Ensure output structure
    ensure_output_structure()
    
    # Test first 3 chart types
    test_types = TARGET_CHART_TYPES[:3]
    
    for chart_type in test_types:
        print(f"Testing {chart_type}...")
        
        # Generate synthetic data
        data = generate_synthetic_data(
            topic="test metrics",
            chart_type=chart_type,
            num_points=10
        )
        print(f"  ✅ Generated data with {len(data)} fields")
        
        # Generate fallback chart (faster than LLM)
        output_file = f"./dump_generation/{chart_type}/test_{chart_type.lower()}.html"
        code = generate_fallback_chart(
            data=data,
            chart_type=chart_type,
            theme="ThemeType.MACARONS",
            output_file=output_file
        )
        
        # Save code
        code_file = output_file.replace('.html', '.py')
        with open(code_file, 'w') as f:
            f.write(code)
        print(f"  ✅ Saved code to {os.path.basename(code_file)}")
        
        # Execute code to generate HTML
        import subprocess
        result = subprocess.run(
            [sys.executable, code_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and os.path.exists(output_file):
            print(f"  ✅ Generated chart: {os.path.basename(output_file)}")
        else:
            print(f"  ❌ Failed to generate chart")
            if result.stderr:
                print(f"     Error: {result.stderr[:100]}")
    
    print("")
    print("=" * 60)
    print("✅ Pipeline test complete!")
    print("Check ./dump_generation/ for generated charts")
    
    # List generated files
    import glob
    html_files = glob.glob("./dump_generation/*/*.html")
    if html_files:
        print(f"\nGenerated {len(html_files)} test charts:")
        for f in html_files:
            print(f"  - {os.path.basename(f)}")

if __name__ == "__main__":
    test_pipeline()
