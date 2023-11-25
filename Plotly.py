# Import necessary libraries
from pycaret.datasets import get_data
from pycaret.clustering import setup, create_model, assign_model
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import dash
import dash_core_components as dcc
import dash_html_components as html

# Load and set up dataset
data = get_data('jewellery')
s = setup(data, session_id = 123)

# Create KMeans model
kmeans = create_model('kmeans')
kmeans_results = assign_model(kmeans)

# PCA for visualization
pca = PCA(2)
data_pca = pca.fit_transform(data)

# Create PCA cluster plot using Plotly
fig_cluster = px.scatter(x=data_pca[:,0], y=data_pca[:,1], color=kmeans_results['Cluster'].astype(str))

# Elbow Plot
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
    kmeans.fit(data)
    wcss.append(kmeans.inertia_)

fig_elbow = go.Figure()
fig_elbow.add_trace(go.Scatter(x=list(range(1, 11)), y=wcss, mode='lines+markers'))
fig_elbow.update_layout(title='Elbow Method',
                        xaxis_title='Number of clusters',
                        yaxis_title='WCSS',
                        template='plotly_dark')

# Silhouette Score Plot
range_n_clusters = [2, 3, 4, 5, 6, 7, 8, 9, 10]
silhouette_avg_scores = []

for n_clusters in range_n_clusters:
    clusterer = KMeans(n_clusters=n_clusters, random_state=10)
    cluster_labels = clusterer.fit_predict(data)
    silhouette_avg = silhouette_score(data, cluster_labels)
    silhouette_avg_scores.append(silhouette_avg)

fig_silhouette = go.Figure()
fig_silhouette.add_trace(go.Scatter(x=range_n_clusters, y=silhouette_avg_scores, mode='lines+markers'))
fig_silhouette.update_layout(title='Silhouette Scores for Various Clusters',
                             xaxis_title='Number of clusters',
                             yaxis_title='Average Silhouette Score',
                             template='plotly_dark')

# Dash app layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Clustering Analysis Dashboard"),
    dcc.Graph(figure=fig_cluster),
    dcc.Graph(figure=fig_elbow),
    dcc.Graph(figure=fig_silhouette)
])

# Run Dash app
if __name__ == '__main__':
    app.run_server(debug=True)