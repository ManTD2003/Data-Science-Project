from flask import Flask, render_template
from bertopic import BERTopic
import plotly.io as pio

app = Flask(__name__)

# # Load BERTopic model
topic_model = BERTopic.load("D://intro to data science//code//dataset//Data-Science-Project//src//thiet-bi-kts-phu-kien-so") 

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from io import BytesIO
import base64

def generate_evaluation_charts(json_file):
    with open(json_file, 'r') as file:
        results = json.load(file)

    nr_topics = [entry['Params']['nr_topics'] for entry in results]
    npmi_scores = [entry['Scores']['npmi'] for entry in results]
    diversity_scores = [entry['Scores']['diversity'] for entry in results]
    computation_times = [entry['Computation Time'] for entry in results]

    # Plot NPMI and Diversity
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(nr_topics, npmi_scores, marker='o', label='NPMI', color='blue')
    ax1.plot(nr_topics, diversity_scores, marker='s', label='Diversity', color='green')
    ax1.set_title('NPMI and Diversity vs Number of Topics', fontsize=14)
    ax1.set_xlabel('Number of Topics', fontsize=12)
    ax1.set_ylabel('Scores', fontsize=12)
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.7, label='Baseline (0)')
    ax1.legend()
    ax1.grid(alpha=0.3)
    plt.tight_layout()

    img1 = BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    chart1_url = base64.b64encode(img1.getvalue()).decode()
    plt.close(fig1)

    # Plot Computation Time
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(nr_topics, computation_times, color='orange', alpha=0.7)
    ax2.set_title('Computation Time vs Number of Topics', fontsize=14)
    ax2.set_xlabel('Number of Topics', fontsize=12)
    ax2.set_ylabel('Computation Time (s)', fontsize=12)
    ax2.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    img2 = BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    chart2_url = base64.b64encode(img2.getvalue()).decode()
    plt.close(fig2)

    # Return HTML for embedding images
    return f'''
        <div>
            <h3>NPMI and Diversity vs Number of Topics</h3>
            <img src="data:image/png;base64,{chart1_url}" />
        </div>
        <div>
            <h3>Computation Time vs Number of Topics</h3>
            <img src="data:image/png;base64,{chart2_url}" />
        </div>
    '''

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

    json_file = "D://intro to data science//code//BERTopic_evaluation//evaluation//BERTopic_trump_0.json"
    evaluation_html = generate_evaluation_charts(json_file)

    return render_template(
        "visualizations.html",
        topics_html=topics_html,
        barchart_html=barchart_html,
        heatmap_html=heatmap_html,
        hierarchy_html=hierarchy_html,
        evaluation_html=evaluation_html,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
