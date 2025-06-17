import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.graph_objects as go

def generate_wordcloud_image(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Save to buffer using matplotlib
    buffer = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    image = wordcloud.to_image()

    return image, img_base64

def generate_tfidf_plot(tfidf_keywords):
    fig = go.Figure(
        data=[go.Bar(
            x=[entry[0] for entry in tfidf_keywords],
            y=[entry[1] for entry in tfidf_keywords],
            marker=dict(color='rgba(103, 58, 183, 0.7)')
        )]
    )
    fig.update_layout(
        title="Top TF-IDF Keywords",
        xaxis_title="Term",
        yaxis_title="Score",
        template="plotly_white"
    )
    return fig.to_html(full_html=False)
