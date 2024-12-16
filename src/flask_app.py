from flask import Flask, render_template
from bertopic import BERTopic
import plotly.io as pio

app = Flask(__name__)

# # Load BERTopic model
topic_model = BERTopic.load("fitted_model") 


@app.route("/")
def index():
    # Generate visualizations
    visualize_topics = topic_model.visualize_topics()
    visualize_barchart = topic_model.visualize_barchart(top_n_topics=10)
    visualize_heatmap = topic_model.visualize_heatmap()
    visualize_hierarchy = topic_model.visualize_hierarchy()

    # Convert Plotly figures to HTML
    topics_html = pio.to_html(visualize_topics, full_html=False)
    barchart_html = pio.to_html(visualize_barchart, full_html=False)
    heatmap_html = pio.to_html(visualize_heatmap, full_html=False)
    hierarchy_html = pio.to_html(visualize_hierarchy, full_html=False)

    return render_template(
        "visualizations.html",
        topics_html=topics_html,
        barchart_html=barchart_html,
        heatmap_html=heatmap_html,
        hierarchy_html=hierarchy_html,
    )


if __name__ == "__main__":
    app.run(debug=True)
