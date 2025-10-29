"""Test the simplified pipeline with a few chart types"""

import os
import sys
sys.path.append('.')

from generate_chart_pipeline import (
    generate_synthetic_data,
    generate_chart_code,
    load_example_codes,
    ensure_output_structure
)

def test_chart_generation():
    """Test generating a few different chart types."""
    
    # Test a few different types
    test_types = ['Bar', 'Pie', 'WordCloud', 'Radar', 'Heatmap']
    
    print("🧪 Testing Simplified Pipeline")
    print("=" * 60)
    
    ensure_output_structure()
    success_count = 0
    
    for chart_type in test_types:
        print(f"\n📊 Testing {chart_type}...")
        
        try:
            # Load example
            examples = load_example_codes(chart_type)
            example = examples[0] if examples else "# No example"
            print(f"  ✅ Loaded example ({len(example)} chars)")
            
            # Generate data
            data = generate_synthetic_data(
                topic="test metrics",
                chart_type=chart_type,
                num_points=10
            )
            print(f"  ✅ Generated data with {len(data)} fields")
            
            # Generate code
            output_file = f"./dump_generation/{chart_type}/test_{chart_type.lower()}.html"
            code = generate_chart_code(
                data=data,
                chart_type=chart_type,
                example_code=example,
                theme="ThemeType.ROMANTIC",
                variation_num=1,
                output_file=output_file
            )
            print(f"  ✅ Generated code ({len(code)} chars)")
            
            # Save and try to execute
            code_file = output_file.replace('.html', '.py')
            with open(code_file, 'w') as f:
                f.write(code)
            
            import subprocess
            result = subprocess.run(
                [sys.executable, code_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                if os.path.exists(output_file):
                    print(f"  ✅ Chart generated successfully!")
                    success_count += 1
                else:
                    print(f"  ⚠️ Code ran but no HTML output")
            else:
                print(f"  ❌ Execution failed: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    print(f"Results: {success_count}/{len(test_types)} charts generated successfully")
    
    if success_count == len(test_types):
        print("🎉 All test charts generated successfully!")
    else:
        print(f"⚠️ {len(test_types) - success_count} charts failed")
        print("Note: Complex charts may need API keys or special setup")

if __name__ == "__main__":
    test_chart_generation()
