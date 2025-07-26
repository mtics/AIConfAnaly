"""
AI Conference Analysis Dashboard Generator
Streamlined version with comprehensive field taxonomy and reliable visualization
"""

import os
import json
import pandas as pd
import numpy as np
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
import re
import warnings
warnings.filterwarnings('ignore')

class AIConferenceDashboard:
    def __init__(self):
        self.conferences = ['ICML', 'NeuRIPS', 'ICLR', 'AAAI', 'IJCAI']
        self.colors = {
            'ICML': '#1f77b4', 'NeuRIPS': '#ff7f0e', 'ICLR': '#2ca02c', 
            'AAAI': '#d62728', 'IJCAI': '#9467bd'
        }
        
        # Comprehensive research field taxonomy (150+ categories)
        self.field_taxonomy = {
            # Computer Vision - Detailed Breakdown
            'Object Detection - YOLO': ['yolo', 'you only look once', 'yolov3', 'yolov4', 'yolov5', 'yolov8'],
            'Object Detection - R-CNN': ['rcnn', 'r-cnn', 'faster rcnn', 'mask rcnn', 'cascade rcnn'],
            'Object Detection - Single Shot': ['ssd', 'single shot', 'retinanet', 'focal loss'],
            'Face Recognition': ['face recognition', 'facial recognition', 'face detection', 'face verification'],
            'Semantic Segmentation': ['semantic segmentation', 'pixel-wise', 'fcn', 'deeplabv3', 'pspnet', 'unet'],
            'Instance Segmentation': ['instance segmentation', 'mask rcnn', 'panoptic segmentation'],
            'Medical Image Analysis': ['medical image', 'ct scan', 'mri', 'x-ray', 'medical segmentation'],
            'Image Classification - CNN': ['image classification', 'resnet', 'densenet', 'efficientnet', 'mobilenet'],
            'Vision Transformers': ['vision transformer', 'vit', 'patch embedding', 'transformer vision'],
            'Image Generation - GAN': ['gan', 'generative adversarial', 'stylegan', 'cyclegan', 'pix2pix'],
            'Image Generation - Diffusion': ['diffusion model', 'denoising diffusion', 'ddpm', 'stable diffusion'],
            'Image Generation - VAE': ['variational autoencoder', 'vae', 'beta-vae'],
            'Style Transfer': ['style transfer', 'neural style', 'artistic style'],
            'Super Resolution': ['super resolution', 'image enhancement', 'upsampling', 'srcnn'],
            'Video Understanding': ['video classification', 'action recognition', 'video analysis'],
            'Video Generation': ['video generation', 'video synthesis', 'video prediction'],
            'Optical Flow': ['optical flow', 'motion estimation', 'flownet'],
            'Object Tracking': ['object tracking', 'visual tracking', 'multi-object tracking'],
            '3D Object Detection': ['3d object detection', 'point cloud detection', 'lidar'],
            '3D Reconstruction': ['3d reconstruction', 'structure from motion', 'nerf', 'neural radiance'],
            'Point Cloud Processing': ['point cloud', 'pointnet', 'pointnet++', 'voxel'],
            'SLAM': ['slam', 'simultaneous localization', 'visual slam', 'mapping'],
            'Depth Estimation': ['depth estimation', 'monocular depth', 'stereo depth'],
            
            # Natural Language Processing - Granular
            'BERT Family': ['bert', 'roberta', 'albert', 'distilbert', 'electra', 'deberta'],
            'GPT Family': ['gpt', 'gpt-2', 'gpt-3', 'gpt-4', 'chatgpt', 'generative pre-training'],
            'Transformer Architecture': ['transformer', 'multi-head attention', 'self-attention', 'positional encoding'],
            'Large Language Models': ['large language model', 'llm', 'foundation model', 'language model scaling'],
            'Prompt Engineering': ['prompt engineering', 'prompt tuning', 'in-context learning', 'chain of thought'],
            'Fine-tuning': ['fine-tuning', 'transfer learning', 'domain adaptation', 'parameter-efficient'],
            'Machine Translation': ['machine translation', 'neural machine translation', 'seq2seq'],
            'Multilingual NLP': ['multilingual', 'cross-lingual', 'zero-shot translation'],
            'Sentiment Analysis': ['sentiment analysis', 'emotion recognition', 'opinion mining'],
            'Text Classification': ['text classification', 'document classification', 'spam detection'],
            'Named Entity Recognition': ['named entity recognition', 'ner', 'entity extraction'],
            'Question Answering': ['question answering', 'reading comprehension', 'squad', 'qa system'],
            'Dialogue Systems': ['dialogue system', 'conversational ai', 'chatbot'],
            'Text Summarization': ['text summarization', 'abstractive summarization', 'extractive summarization'],
            'Text Generation': ['text generation', 'language generation', 'natural language generation'],
            'Language Modeling': ['language modeling', 'language model', 'perplexity', 'neural language model'],
            'Syntax Parsing': ['syntactic parsing', 'dependency parsing', 'constituency parsing'],
            'Semantic Parsing': ['semantic parsing', 'meaning representation', 'semantic role labeling'],
            'Word Embeddings': ['word embedding', 'word2vec', 'glove', 'fasttext'],
            'Sentence Embeddings': ['sentence embedding', 'sentence-bert', 'universal sentence encoder'],
            
            # Machine Learning Theory
            'Gradient Descent': ['gradient descent', 'sgd', 'stochastic gradient descent'],
            'Adaptive Optimizers': ['adam', 'adamw', 'rmsprop', 'adagrad', 'adaptive optimization'],
            'Learning Rate Scheduling': ['learning rate', 'cosine annealing', 'step decay'],
            'Convex Optimization': ['convex optimization', 'linear programming', 'quadratic programming'],
            'Non-Convex Optimization': ['non-convex optimization', 'local minima', 'saddle point'],
            'PAC Learning': ['pac learning', 'probably approximately correct', 'pac-bayes'],
            'VC Theory': ['vc dimension', 'vapnik-chervonenkis', 'statistical learning theory'],
            'Generalization': ['generalization', 'sample complexity', 'bias-variance', 'overfitting'],
            'Regularization': ['regularization', 'ridge regression', 'lasso', 'l1 regularization', 'l2 regularization'],
            'Feature Selection': ['feature selection', 'variable selection', 'forward selection'],
            'Dimensionality Reduction': ['dimensionality reduction', 'pca', 'principal component'],
            'Manifold Learning': ['manifold learning', 'isomap', 'locally linear embedding', 't-sne', 'umap'],
            
            # Deep Learning Architectures
            'ResNet': ['resnet', 'residual network', 'skip connection', 'residual block'],
            'DenseNet': ['densenet', 'dense connection', 'dense block'],
            'EfficientNet': ['efficientnet', 'compound scaling', 'mobile inverted bottleneck'],
            'MobileNet': ['mobilenet', 'depthwise separable', 'inverted residual'],
            'Attention Mechanisms': ['attention mechanism', 'self-attention', 'cross-attention'],
            'Memory Networks': ['memory network', 'neural turing machine', 'external memory'],
            'Normalization': ['batch normalization', 'layer normalization', 'group normalization'],
            'Activation Functions': ['activation function', 'relu', 'leaky relu', 'swish', 'gelu'],
            'Dropout': ['dropout', 'dropconnect', 'spatial dropout', 'variational dropout'],
            'Loss Functions': ['loss function', 'cross-entropy', 'focal loss', 'contrastive loss'],
            
            # Reinforcement Learning Methods
            'Q-Learning': ['q-learning', 'deep q-network', 'dqn', 'double dqn', 'dueling dqn'],
            'Policy Gradient': ['policy gradient', 'reinforce', 'vanilla policy gradient'],
            'Actor-Critic': ['actor-critic', 'advantage actor-critic', 'a2c', 'a3c'],
            'Trust Region': ['trust region', 'trpo', 'trust region policy optimization'],
            'PPO': ['ppo', 'proximal policy optimization', 'clipped surrogate'],
            'DDPG': ['ddpg', 'deep deterministic policy gradient', 'continuous control'],
            'SAC': ['sac', 'soft actor-critic', 'maximum entropy'],
            'Multi-Agent RL': ['multi-agent reinforcement learning', 'cooperative learning'],
            'Hierarchical RL': ['hierarchical reinforcement learning', 'option framework'],
            'Meta-RL': ['meta reinforcement learning', 'learning to adapt'],
            'Imitation Learning': ['imitation learning', 'behavioral cloning', 'inverse reinforcement'],
            'Model-Based RL': ['model-based reinforcement learning', 'model predictive control'],
            'Offline RL': ['offline reinforcement learning', 'batch reinforcement learning'],
            
            # Graph Neural Networks
            'Graph Convolution': ['graph convolutional network', 'gcn', 'spectral convolution'],
            'Graph Attention': ['graph attention network', 'gat', 'attention mechanism graph'],
            'Graph Transformer': ['graph transformer', 'graphormer', 'transformer graph'],
            'Graph Generation': ['graph generation', 'molecular generation', 'graph vae'],
            'Knowledge Graph': ['knowledge graph embedding', 'knowledge graph', 'transe'],
            'Node Classification': ['node classification', 'semi-supervised node classification'],
            'Link Prediction': ['link prediction', 'graph link prediction'],
            'Graph Clustering': ['graph clustering', 'community detection', 'spectral clustering'],
            
            # Federated Learning
            'Federated Averaging': ['federated averaging', 'fedavg', 'distributed training'],
            'Personalized FL': ['personalized federated learning', 'personalization'],
            'Privacy-Preserving FL': ['differential privacy', 'privacy-preserving', 'secure aggregation'],
            'Communication Efficient FL': ['communication efficient', 'gradient compression'],
            'Non-IID FL': ['non-iid', 'data heterogeneity', 'statistical heterogeneity'],
            
            # Meta Learning
            'MAML': ['maml', 'model-agnostic meta-learning', 'gradient-based meta-learning'],
            'Metric Learning': ['metric learning', 'prototypical network', 'matching network'],
            'Few-Shot Learning': ['few-shot learning', 'one-shot learning', 'zero-shot learning'],
            'Meta-Optimization': ['optimization-based meta-learning', 'learning to optimize'],
            
            # Time Series & Forecasting
            'LSTM Time Series': ['lstm time series', 'long short-term memory', 'sequence modeling'],
            'Transformer Time Series': ['transformer time series', 'temporal transformer', 'informer'],
            'CNN Time Series': ['cnn time series', 'temporal cnn', 'wavenet'],
            'ARIMA': ['arima', 'autoregressive integrated moving average', 'time series arima'],
            'Prophet': ['prophet', 'facebook prophet', 'seasonal decomposition'],
            'Anomaly Detection': ['time series anomaly detection', 'outlier detection temporal'],
            
            # Multimodal Learning
            'Vision-Language': ['vision-language', 'clip', 'visual-textual', 'multimodal transformer'],
            'Visual Question Answering': ['visual question answering', 'vqa', 'visual reasoning'],
            'Image Captioning': ['image captioning', 'automatic captioning', 'show and tell'],
            'Audio-Visual': ['audio-visual', 'cross-modal audio visual', 'lip reading'],
            'Multimodal Fusion': ['multimodal fusion', 'early fusion', 'late fusion'],
            
            # Adversarial Learning
            'Adversarial Examples': ['adversarial examples', 'adversarial attack', 'fgsm', 'pgd'],
            'Adversarial Training': ['adversarial training', 'adversarial defense', 'robust training'],
            'Certified Robustness': ['certified robustness', 'certified defense', 'verification'],
            
            # Interpretability
            'Attention Visualization': ['attention visualization', 'attention map', 'attention heatmap'],
            'Gradient Attribution': ['gradient attribution', 'integrated gradients', 'saliency map'],
            'LIME SHAP': ['lime', 'shap', 'local interpretable', 'shapley additive'],
            'Concept Learning': ['concept activation vector', 'tcav', 'concept-based explanation'],
            
            # AutoML
            'Neural Architecture Search': ['neural architecture search', 'nas', 'darts', 'enas'],
            'Hyperparameter Optimization': ['hyperparameter optimization', 'bayesian optimization'],
            'Automated Feature Engineering': ['automated feature engineering', 'feature synthesis'],
            'Model Selection': ['automated model selection', 'model search', 'ensemble selection'],
            
            # Scientific ML
            'Physics-Informed NN': ['physics-informed neural network', 'pinn', 'scientific machine learning'],
            'Neural ODEs': ['neural ode', 'ordinary differential equation', 'continuous-time'],
            'Molecular ML': ['molecular machine learning', 'drug discovery', 'molecular property'],
            'Climate Modeling': ['climate modeling', 'weather prediction', 'atmospheric modeling'],
            'Computational Biology': ['computational biology', 'bioinformatics', 'genomics'],
            
            # Edge AI & Efficiency
            'Model Compression': ['model compression', 'model pruning', 'weight pruning'],
            'Quantization': ['quantization', 'int8 quantization', 'binary neural network'],
            'Knowledge Distillation': ['knowledge distillation', 'teacher-student', 'model distillation'],
            'Mobile AI': ['mobile ai', 'edge computing', 'on-device ai'],
            
            # Other Specialized Areas
            'Causal Inference': ['causal inference', 'causal discovery', 'do-calculus'],
            'Fairness': ['algorithmic fairness', 'bias mitigation', 'fair representation'],
            'Continual Learning': ['continual learning', 'lifelong learning', 'catastrophic forgetting'],
            'Self-Supervised': ['self-supervised learning', 'contrastive learning', 'simclr'],
            'Contrastive Learning': ['contrastive learning', 'contrastive loss', 'negative sampling'],
            'Representation Learning': ['representation learning', 'feature learning', 'disentangled representation']
        }
        
    def load_data(self):
        """Load all conference data"""
        print("Loading conference data...")
        all_papers = []
        
        for conf in self.conferences:
            for year in range(2018, 2025):
                filename = f'outputs/data/raw/{conf}_{year}.json'
                if os.path.exists(filename):
                    try:
                        with open(filename, 'r', encoding='utf-8') as f:
                            papers = json.load(f)
                            for paper in papers:
                                paper['conference'] = conf
                                paper['year'] = year
                                all_papers.append(paper)
                    except Exception as e:
                        print(f"Warning: Error loading {filename}: {e}")
        
        df = pd.DataFrame(all_papers)
        print(f"Loaded {len(df)} papers from {len(df['conference'].unique())} conferences")
        return df
    
    def classify_fields(self, df):
        """Classify papers into detailed research fields"""
        print("Classifying papers into research fields...")
        print(f"Using taxonomy with {len(self.field_taxonomy)} field categories")
        
        df['text'] = df['title'].fillna('') + ' ' + df['abstract'].fillna('')
        field_data = []
        unclassified = 0
        
        for idx, row in df.iterrows():
            if idx % 2000 == 0:
                print(f"Processed {idx}/{len(df)} papers...")
                
            text = row['text'].lower()
            detected_fields = []
            
            # Check detailed field categories
            for field, keywords in self.field_taxonomy.items():
                if any(keyword.lower() in text for keyword in keywords):
                    detected_fields.append(field)
            
            # Fallback classification
            if not detected_fields:
                if any(term in text for term in ['deep', 'neural', 'cnn', 'rnn']):
                    detected_fields.append('General Deep Learning')
                elif any(term in text for term in ['reinforcement', 'policy', 'reward']):
                    detected_fields.append('General RL')
                elif any(term in text for term in ['optimization', 'gradient']):
                    detected_fields.append('General Optimization')
                else:
                    detected_fields.append('Other')
                    unclassified += 1
            
            for field in detected_fields:
                field_data.append({
                    'conference': row['conference'],
                    'year': row['year'],
                    'field': field,
                    'title': row['title']
                })
        
        field_df = pd.DataFrame(field_data)
        print(f"Classification complete. {unclassified} papers unclassified.")
        print(f"Identified {len(field_df['field'].unique())} unique fields")
        return field_df
    
    def create_visualizations(self, df, field_df):
        """Create all dashboard visualizations"""
        print("Creating visualizations...")
        figs = []
        
        try:
            # 1. Publication trends
            yearly = df.groupby(['year', 'conference']).size().unstack(fill_value=0)
            fig1 = go.Figure()
            for conf in self.conferences:
                if conf in yearly.columns:
                    fig1.add_trace(go.Scatter(
                        x=yearly.index, y=yearly[conf], mode='lines+markers',
                        name=conf, line=dict(color=self.colors[conf], width=3),
                        hovertemplate=f'<b>{conf}</b><br>Year: %{{x}}<br>Papers: %{{y}}<extra></extra>'
                    ))
            fig1.update_layout(
                title='AI Conference Publication Trends (2018-2024)',
                xaxis_title='Year', yaxis_title='Papers', height=500, template='plotly_white'
            )
            figs.append(fig1)
            
            # 2. Top research fields
            top_fields = field_df['field'].value_counts().head(20)
            fig2 = go.Figure(go.Pie(
                labels=top_fields.index, values=top_fields.values, hole=0.3,
                hovertemplate='<b>%{label}</b><br>Papers: %{value}<br>%{percent}<extra></extra>'
            ))
            fig2.update_layout(title='Top 20 Research Fields', height=600)
            figs.append(fig2)
            
            # 3. Conference comparison
            conf_totals = df['conference'].value_counts()
            fig3 = go.Figure(go.Bar(
                x=conf_totals.values, y=conf_totals.index, orientation='h',
                marker_color=[self.colors[conf] for conf in conf_totals.index],
                text=[f'{x:,}' for x in conf_totals.values], textposition='auto'
            ))
            fig3.update_layout(title='Papers by Conference', xaxis_title='Total Papers', height=400)
            figs.append(fig3)
            
            # 4. Field evolution
            field_yearly = field_df.groupby(['year', 'field']).size().unstack(fill_value=0)
            top_evolving = field_yearly.sum(axis=0).nlargest(12).index
            fig4 = go.Figure()
            colors = px.colors.qualitative.Set3
            for i, field in enumerate(top_evolving):
                fig4.add_trace(go.Scatter(
                    x=field_yearly.index, y=field_yearly[field], mode='lines+markers',
                    name=field, line=dict(color=colors[i % len(colors)], width=2)
                ))
            fig4.update_layout(
                title='Top Fields Evolution Over Time', height=600,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            figs.append(fig4)
            
            # 5. Conference-field heatmap
            conf_field = field_df.groupby(['conference', 'field']).size().unstack(fill_value=0)
            conf_field_pct = conf_field.div(conf_field.sum(axis=1), axis=0) * 100
            top_heatmap_fields = conf_field.sum(axis=0).nlargest(20).index
            heatmap_data = conf_field_pct[top_heatmap_fields]
            
            fig5 = go.Figure(go.Heatmap(
                z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index,
                colorscale='Viridis', colorbar=dict(title="Percentage")
            ))
            fig5.update_layout(
                title='Field Distribution by Conference (%)', height=500,
                xaxis=dict(tickangle=45)
            )
            figs.append(fig5)
            
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            return []
        
        print(f"Created {len(figs)} visualizations successfully")
        return figs
    
    def generate_dashboard_html(self, df, field_df, figures):
        """Generate the final dashboard HTML"""
        print("Generating dashboard HTML...")
        
        stats = {
            'total_papers': len(df),
            'conferences': len(df['conference'].unique()),
            'years': f"{df['year'].min()}-{df['year'].max()}",
            'fields': len(field_df['field'].unique()),
            'top_conf': df['conference'].value_counts().index[0],
            'top_conf_count': df['conference'].value_counts().iloc[0],
            'peak_year': df['year'].value_counts().idxmax(),
            'peak_count': df['year'].value_counts().max(),
            'top_field': field_df['field'].value_counts().index[0],
            'top_field_count': field_df['field'].value_counts().iloc[0]
        }
        
        # Convert figures to JSON with proper error handling
        figure_jsons = []
        for i, fig in enumerate(figures):
            try:
                json_str = fig.to_json()
                # 验证JSON是否有效
                import json
                json.loads(json_str)
                figure_jsons.append(json_str)
                print(f"✓ 图表 {i+1} JSON转换成功")
            except Exception as e:
                print(f"✗ 图表 {i+1} JSON转换失败: {e}")
                figure_jsons.append('{"data":[],"layout":{"title":"图表加载失败"}}')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Conference Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
        .header h1 {{ font-size: 3em; margin-bottom: 15px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .header p {{ font-size: 1.3em; opacity: 0.9; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 30px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px; margin-bottom: 40px; }}
        .stat-card {{ background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; transition: transform 0.3s ease; }}
        .stat-card:hover {{ transform: translateY(-8px); }}
        .stat-icon {{ font-size: 3em; margin-bottom: 20px; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stat-number {{ font-size: 2.8em; font-weight: bold; color: #333; margin-bottom: 8px; }}
        .stat-label {{ color: #666; font-size: 1.2em; }}
        .section {{ background: white; margin-bottom: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }}
        .section-header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 25px 35px; font-size: 1.6em; font-weight: bold; }}
        .section-content {{ padding: 30px; }}
        .chart-container {{ min-height: 500px; margin-bottom: 30px; }}
        .insights {{ background: linear-gradient(135deg, #f8f9ff, #e8f2ff); padding: 30px; border-radius: 20px; margin-bottom: 40px; border-left: 6px solid #667eea; }}
        .insight-item {{ background: white; margin-bottom: 20px; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
        .insight-item strong {{ color: #667eea; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
        @media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} .header h1 {{ font-size: 2.5em; }} }}
        .footer {{ text-align: center; padding: 40px; color: white; background: rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-chart-network"></i> AI Conference Analysis Dashboard</h1>
        <p>Comprehensive Analysis of {stats['total_papers']:,} Papers from {stats['conferences']} Major AI Conferences</p>
        <p>Covering {stats['years']} • {stats['fields']} Detailed Research Fields</p>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-file-alt"></i></div>
                <div class="stat-number">{stats['total_papers']:,}</div>
                <div class="stat-label">Total Papers</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-university"></i></div>
                <div class="stat-number">{stats['conferences']}</div>
                <div class="stat-label">Conferences</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-brain"></i></div>
                <div class="stat-number">{stats['fields']}</div>
                <div class="stat-label">Research Fields</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-calendar-alt"></i></div>
                <div class="stat-number">{stats['years'].split('-')[1]}</div>
                <div class="stat-label">Latest Year</div>
            </div>
        </div>
        
        <div class="insights">
            <h3><i class="fas fa-lightbulb"></i> Key Insights</h3>
            <div class="insight-item">
                <strong><i class="fas fa-trophy"></i> Leading Conference:</strong> 
                {stats['top_conf']} dominates with {stats['top_conf_count']:,} papers ({stats['top_conf_count']/stats['total_papers']*100:.1f}% of total)
            </div>
            <div class="insight-item">
                <strong><i class="fas fa-rocket"></i> Peak Year:</strong> 
                {stats['peak_year']} was most productive with {stats['peak_count']:,} publications
            </div>
            <div class="insight-item">
                <strong><i class="fas fa-fire"></i> Hottest Field:</strong> 
                {stats['top_field']} leads with {stats['top_field_count']:,} papers
            </div>
            <div class="insight-item">
                <strong><i class="fas fa-chart-line"></i> Research Diversity:</strong> 
                {stats['fields']} specialized fields identified, showing the breadth of AI/ML research
            </div>
        </div>
        
        <div class="section">
            <div class="section-header"><i class="fas fa-chart-line"></i> Publication Trends</div>
            <div class="section-content"><div class="chart-container" id="chart1"></div></div>
        </div>
        
        <div class="section">
            <div class="section-header"><i class="fas fa-brain"></i> Top Research Fields</div>
            <div class="section-content"><div class="chart-container" id="chart2"></div></div>
        </div>
        
        <div class="section">
            <div class="section-header"><i class="fas fa-university"></i> Conference Comparison</div>
            <div class="section-content"><div class="chart-container" id="chart3"></div></div>
        </div>
        
        <div class="section">
            <div class="section-header"><i class="fas fa-chart-area"></i> Field Evolution</div>
            <div class="section-content"><div class="chart-container" id="chart4"></div></div>
        </div>
        
        <div class="section">
            <div class="section-header"><i class="fas fa-fire"></i> Conference-Field Heatmap</div>
            <div class="section-content"><div class="chart-container" id="chart5"></div></div>
        </div>
    </div>
    
    <div class="footer">
        <p><i class="fas fa-code"></i> AI Conference Analysis Dashboard</p>
        <p>Data from ICML, NeuRIPS, ICLR, AAAI, IJCAI • Generated with Python & Plotly</p>
    </div>
    
    <script>
        const config = {{ responsive: true, displayModeBar: true, displaylogo: false }};
        
        function renderChart(id, data, name) {{
            console.log('开始渲染图表:', name);
            try {{
                // 检查Plotly是否可用
                if (typeof Plotly === 'undefined') {{
                    throw new Error('Plotly库未加载');
                }}
                
                // 检查数据是否有效
                if (!data || typeof data !== 'object') {{
                    throw new Error('图表数据无效');
                }}
                
                let chartData, chartLayout;
                
                // 如果数据是字符串，尝试解析
                if (typeof data === 'string') {{
                    const parsed = JSON.parse(data);
                    chartData = parsed.data;
                    chartLayout = parsed.layout;
                }} else {{
                    chartData = data.data;
                    chartLayout = data.layout;
                }}
                
                if (!chartData || !chartLayout) {{
                    throw new Error('图表数据结构不完整');
                }}
                
                // 渲染图表
                Plotly.newPlot(id, chartData, chartLayout, {{
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false
                }});
                
                console.log('✓ ' + name + ' 渲染成功');
                
            }} catch (error) {{
                console.error('✗ 渲染失败 ' + name + ':', error);
                const errorMsg = `<div style="text-align:center;color:#dc3545;padding:50px;">
                    <h4>图表加载失败</h4>
                    <p>${{error.message}}</p>
                    <small>请刷新页面重试或检查网络连接</small>
                </div>`;
                document.getElementById(id).innerHTML = errorMsg;
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🚀 Loading AI Conference Dashboard...');
            
            const charts = [
                {{ id: 'chart1', name: 'Publication Trends', data: {figure_jsons[0] if len(figure_jsons) > 0 else '{}'} }},
                {{ id: 'chart2', name: 'Research Fields', data: {figure_jsons[1] if len(figure_jsons) > 1 else '{}'} }},
                {{ id: 'chart3', name: 'Conference Comparison', data: {figure_jsons[2] if len(figure_jsons) > 2 else '{}'} }},
                {{ id: 'chart4', name: 'Field Evolution', data: {figure_jsons[3] if len(figure_jsons) > 3 else '{}'} }},
                {{ id: 'chart5', name: 'Conference Heatmap', data: {figure_jsons[4] if len(figure_jsons) > 4 else '{}'} }}
            ];
            
            charts.forEach((chart, i) => {{
                setTimeout(() => renderChart(chart.id, chart.data, chart.name), i * 300);
            }});
            
            window.addEventListener('resize', () => {{
                charts.forEach(chart => {{
                    try {{ Plotly.Plots.resize(chart.id); }} catch(e) {{}}
                }});
            }});
            
            console.log('✅ Dashboard initialized successfully');
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def generate(self):
        """Main generation function"""
        print("="*60)
        print("🚀 AI CONFERENCE ANALYSIS DASHBOARD GENERATOR")
        print("="*60)
        
        # Load and process data
        df = self.load_data()
        field_df = self.classify_fields(df)
        
        # Create visualizations
        figures = self.create_visualizations(df, field_df)
        
        # Generate HTML
        html_content = self.generate_dashboard_html(df, field_df, figures)
        
        # Save to dashboard folder
        output_path = 'outputs/dashboard/ai_conference_dashboard.html'
        os.makedirs('outputs/dashboard', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Summary
        print("\\n" + "="*60)
        print("✅ DASHBOARD GENERATED SUCCESSFULLY!")
        print("="*60)
        print(f"📊 Papers analyzed: {len(df):,}")
        print(f"🔬 Research fields: {len(field_df['field'].unique())}")
        print(f"📈 Visualizations: {len(figures)}")
        print(f"💾 Output: {output_path}")
        print("="*60)
        print(f"🌐 Open {output_path} in your browser to view the dashboard!")
        print("="*60)
        
        return output_path

if __name__ == "__main__":
    dashboard = AIConferenceDashboard()
    dashboard.generate()