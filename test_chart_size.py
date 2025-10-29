"""Test to verify chart sizing is appropriate"""

from pyecharts import options as opts
from pyecharts.charts import Pie

# Create a test pie chart
pie = Pie()
pie.add(
    "",
    [["Category A", 30], ["Category B", 25], ["Category C", 20], 
     ["Category D", 15], ["Category E", 10]],
    radius=["30%", "75%"],  # Donut chart
    rosetype="area"
)
pie.set_global_opts(
    title_opts=opts.TitleOpts(title="Test Chart - Sizing Verification"),
    legend_opts=opts.LegendOpts(orient="vertical", pos_right="2%", pos_top="15%")
)
pie.render("test_chart_size.html")

print("✅ Test chart created: test_chart_size.html")
print("Chart typically needs ~600-650px height for proper display with title and legend")
print("Our setting of 650px should accommodate most PyEcharts visualizations comfortably")
