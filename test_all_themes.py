"""Test all available PyEcharts themes"""

from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

# Test data
x_data = ["Mon", "Tue", "Wed", "Thu", "Fri"]
y_data = [120, 150, 180, 140, 190]

# All available themes
all_themes = [
    ("LIGHT", ThemeType.LIGHT, "Clean minimal light theme"),
    ("DARK", ThemeType.DARK, "Modern dark mode"),
    ("WHITE", ThemeType.WHITE, "Pure white background"),
    ("CHALK", ThemeType.CHALK, "Chalkboard style"),
    ("ESSOS", ThemeType.ESSOS, "Game of Thrones inspired"),
    ("INFOGRAPHIC", ThemeType.INFOGRAPHIC, "Bold infographic colors"),
    ("MACARONS", ThemeType.MACARONS, "Soft pastel colors"),
    ("PURPLE_PASSION", ThemeType.PURPLE_PASSION, "Purple-dominated elegant"),
    ("ROMA", ThemeType.ROMA, "Classic professional"),
    ("ROMANTIC", ThemeType.ROMANTIC, "Warm and inviting"),
    ("SHINE", ThemeType.SHINE, "Bright and vibrant"),
    ("VINTAGE", ThemeType.VINTAGE, "Retro-inspired"),
    ("WALDEN", ThemeType.WALDEN, "Natural earth tones"),
    ("WESTEROS", ThemeType.WESTEROS, "Game of Thrones inspired"),
    ("WONDERLAND", ThemeType.WONDERLAND, "Whimsical and colorful"),
    ("HALLOWEEN", ThemeType.HALLOWEEN, "Spooky Halloween theme")
]

print("🎨 Testing All PyEcharts Themes")
print("=" * 60)
print(f"Total themes available: {len(all_themes)}")
print("")

# Test each theme
success_count = 0
for name, theme_type, description in all_themes:
    try:
        # Create chart with theme
        chart = (
            Bar(init_opts=opts.InitOpts(theme=theme_type))
            .add_xaxis(x_data)
            .add_yaxis("Sales", y_data)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"Test - {name} Theme")
            )
        )
        # If no error, theme works
        print(f"✅ {name:15} - {description}")
        success_count += 1
    except Exception as e:
        print(f"❌ {name:15} - Error: {e}")

print("")
print("=" * 60)
print(f"Summary: {success_count}/{len(all_themes)} themes working correctly")

if success_count == len(all_themes):
    print("🎉 All themes are properly configured and working!")
else:
    print(f"⚠️ {len(all_themes) - success_count} themes had issues")

print("")
print("Theme configuration complete!")
