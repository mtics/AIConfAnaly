"""
Field extraction module for identifying research areas from paper titles and abstracts
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from collections import defaultdict, Counter
import re


class FieldExtractor:
    def __init__(self):
        # Predefined research field keywords based on common ML/AI areas
        self.field_keywords = {
            'Computer Vision': {
                'image', 'visual', 'vision', 'object detection', 'segmentation',
                'recognition', 'classification', 'cnn', 'convolutional', 'gan',
                'generative adversarial', 'face', 'video', 'depth', 'optical',
                'scene', 'tracking', 'pose estimation', 'super resolution',
                'keypoint', 'landmark', 'feature extraction', 'contour', 'texture',
                'stereo', '3d reconstruction', 'photometry', 'geometric', 'perspective'
            },
            'Natural Language Processing': {
                'language', 'text', 'nlp', 'bert', 'transformer', 'attention',
                'translation', 'sentiment', 'parsing', 'generation', 'dialogue',
                'question answering', 'summarization', 'word embedding', 'lstm',
                'rnn', 'gpt', 'semantic', 'syntactic', 'corpus', 'tokenization',
                'named entity', 'pos tagging', 'dependency parsing', 'coreference',
                'information extraction', 'chatbot', 'conversational', 'multilingual'
            },
            'Reinforcement Learning': {
                'reinforcement', 'rl', 'policy', 'reward', 'agent', 'environment',
                'markov decision', 'q-learning', 'temporal difference', 'actor critic',
                'exploration', 'exploitation', 'monte carlo', 'multi-armed bandit',
                'deep q', 'ddpg', 'ppo', 'a3c', 'sarsa', 'value function',
                'policy gradient', 'inverse reinforcement', 'imitation learning'
            },
            'Deep Learning Architecture': {
                'deep', 'neural network', 'backpropagation', 'gradient descent',
                'optimization', 'regularization', 'dropout', 'batch normalization',
                'activation', 'layer', 'hidden', 'weight', 'bias', 'training',
                'overfitting', 'generalization', 'architecture', 'residual', 'skip connection',
                'attention mechanism', 'transformer', 'encoder', 'decoder'
            },
            'Machine Learning Theory': {
                'theoretical', 'analysis', 'convergence', 'complexity', 'bound',
                'regret', 'sample complexity', 'pac learning', 'statistical',
                'probability', 'concentration', 'uniform', 'empirical risk',
                'generalization bound', 'rademacher', 'vc dimension', 'stability',
                'learnability', 'computational complexity'
            },
            'Optimization Methods': {
                'optimization', 'gradient descent', 'stochastic', 'adam', 'sgd',
                'momentum', 'learning rate', 'convergence', 'convex', 'non-convex',
                'global minimum', 'local minimum', 'saddle point', 'second order',
                'quasi-newton', 'line search', 'coordinate descent', 'proximal'
            },
            'Probabilistic Models': {
                'probabilistic', 'bayesian', 'inference', 'posterior', 'prior',
                'likelihood', 'variational', 'mcmc', 'sampling', 'gaussian process',
                'dirichlet', 'beta', 'gamma', 'latent variable', 'expectation maximization',
                'belief network', 'markov random field', 'hidden markov'
            },
            'Graph Neural Networks': {
                'graph', 'node', 'edge', 'adjacency', 'spectral', 'gcn', 'gat',
                'message passing', 'aggregation', 'neighborhood', 'topology',
                'social network', 'citation network', 'molecular', 'heterogeneous graph',
                'graph convolution', 'graph attention', 'graph isomorphism', 'subgraph'
            },
            'Federated Learning': {
                'federated', 'distributed', 'decentralized', 'privacy', 'differential privacy',
                'secure aggregation', 'communication', 'client', 'server', 'local update',
                'global model', 'non-iid', 'heterogeneous', 'byzantine', 'consensus'
            },
            'Meta Learning': {
                'meta learning', 'few shot', 'meta', 'adaptation', 'transfer',
                'multitask', 'learning to learn', 'maml', 'prototypical', 'metric learning',
                'support set', 'query set', 'episodes', 'gradient-based meta', 'model-agnostic'
            },
            'Generative Models': {
                'generative', 'generation', 'gan', 'vae', 'variational autoencoder',
                'diffusion', 'flow', 'autoregressive', 'decoder', 'latent space',
                'reconstruction', 'sampling', 'likelihood', 'density estimation',
                'normalizing flow', 'score matching', 'energy-based'
            },
            'Adversarial Learning': {
                'adversarial', 'robust', 'attack', 'defense', 'perturbation',
                'noise', 'fooling', 'evasion', 'poisoning', 'certified',
                'verification', 'provable', 'worst case', 'adversarial training',
                'certified defense', 'randomized smoothing'
            },
            'Multimodal Learning': {
                'multimodal', 'cross-modal', 'vision-language', 'audio-visual',
                'fusion', 'alignment', 'grounding', 'retrieval', 'captioning',
                'video understanding', 'speech recognition', 'lip reading'
            },
            'Continual Learning': {
                'continual', 'lifelong', 'incremental', 'catastrophic forgetting',
                'replay', 'regularization', 'task-specific', 'memory', 'adaptation',
                'plasticity', 'stability', 'rehearsal'
            },
            'Self-Supervised Learning': {
                'self-supervised', 'contrastive', 'pretext task', 'representation learning',
                'unsupervised', 'masked language', 'autoencoder', 'reconstruction',
                'pretraining', 'downstream', 'transfer learning'
            },
            'Causal Learning': {
                'causal', 'causality', 'intervention', 'confounding', 'dag',
                'structural equation', 'instrumental variable', 'counterfactual',
                'causal inference', 'do-calculus', 'backdoor', 'frontdoor'
            },
            'Quantum Machine Learning': {
                'quantum', 'qubit', 'quantum circuit', 'variational quantum',
                'quantum neural', 'quantum computing', 'quantum advantage',
                'quantum algorithm', 'quantum supremacy', 'nisq'
            },
            'Explainable AI': {
                'explainable', 'interpretable', 'explanation', 'attribution',
                'feature importance', 'saliency', 'lime', 'shap', 'grad-cam',
                'counterfactual explanation', 'model interpretation', 'transparency'
            },
            'Neural Architecture Search': {
                'neural architecture search', 'nas', 'automl', 'differentiable',
                'evolutionary', 'architecture optimization', 'cell-based',
                'supernet', 'one-shot', 'progressive'
            },
            'Time Series Analysis': {
                'time series', 'temporal', 'sequential', 'forecasting', 'prediction',
                'trend', 'seasonality', 'anomaly detection', 'change point',
                'recurrent', 'temporal convolution', 'attention'
            },
            'Anomaly Detection': {
                'anomaly', 'outlier', 'novelty', 'one-class', 'isolation forest',
                'autoencoder', 'density estimation', 'reconstruction error',
                'statistical test', 'threshold', 'unsupervised detection'
            }
        }
    
    def extract_fields_by_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract research fields based on keyword matching"""
        df_copy = df.copy()
        
        # Initialize field columns
        for field in self.field_keywords:
            df_copy[f'field_{field.lower().replace(" ", "_")}'] = 0
        
        for idx, row in df_copy.iterrows():
            # Combine title and abstract
            text = f"{row.get('title', '')} {row.get('abstract', '')}".lower()
            
            # Check each field
            for field, keywords in self.field_keywords.items():
                field_col = f'field_{field.lower().replace(" ", "_")}'
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in text)
                df_copy.at[idx, field_col] = matches
        
        return df_copy
    
    def get_dominant_field(self, df: pd.DataFrame) -> pd.DataFrame:
        """Determine dominant research field for each paper"""
        df_copy = df.copy()
        
        # Get field columns
        field_cols = [col for col in df_copy.columns if col.startswith('field_')]
        
        # Find dominant field for each paper
        dominant_fields = []
        confidence_scores = []
        
        for idx, row in df_copy.iterrows():
            field_scores = {col.replace('field_', '').replace('_', ' ').title(): 
                          row[col] for col in field_cols}
            
            max_score = max(field_scores.values())
            if max_score > 0:
                dominant_field = max(field_scores, key=field_scores.get)
                confidence = max_score / sum(field_scores.values()) if sum(field_scores.values()) > 0 else 0
            else:
                dominant_field = 'Other'
                confidence = 0
            
            dominant_fields.append(dominant_field)
            confidence_scores.append(confidence)
        
        df_copy['dominant_field'] = dominant_fields
        df_copy['field_confidence'] = confidence_scores
        
        return df_copy
    
    def cluster_papers_by_content(self, df: pd.DataFrame, n_clusters: int = 15) -> pd.DataFrame:
        """Cluster papers based on title and abstract content"""
        df_copy = df.copy()
        
        # Prepare text data
        texts = []
        for idx, row in df_copy.iterrows():
            text = f"{row.get('title', '')} {row.get('abstract', '')}"
            texts.append(text)
        
        # Vectorize text
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        try:
            X = vectorizer.fit_transform(texts)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X)
            
            df_copy['content_cluster'] = clusters
            
            # Get top terms for each cluster
            feature_names = vectorizer.get_feature_names_out()
            cluster_terms = {}
            
            for i in range(n_clusters):
                center = kmeans.cluster_centers_[i]
                top_indices = center.argsort()[-10:][::-1]
                top_terms = [feature_names[idx] for idx in top_indices]
                cluster_terms[i] = top_terms
            
            df_copy['cluster_terms'] = df_copy['content_cluster'].map(cluster_terms)
            
        except Exception as e:
            print(f"Error in clustering: {e}")
            df_copy['content_cluster'] = 0
            df_copy['cluster_terms'] = []
        
        return df_copy
    
    def topic_modeling_lda(self, df: pd.DataFrame, n_topics: int = 10) -> Tuple[pd.DataFrame, Dict]:
        """Perform LDA topic modeling on paper content"""
        df_copy = df.copy()
        
        # Prepare text data
        texts = []
        for idx, row in df_copy.iterrows():
            text = f"{row.get('title', '')} {row.get('abstract', '')}"
            texts.append(text)
        
        # Vectorize text
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            min_df=2,
            max_df=0.8
        )
        
        try:
            X = vectorizer.fit_transform(texts)
            
            # Perform LDA
            lda = LatentDirichletAllocation(
                n_components=n_topics, 
                random_state=42,
                max_iter=10
            )
            
            topic_distributions = lda.fit_transform(X)
            
            # Get dominant topic for each paper
            dominant_topics = np.argmax(topic_distributions, axis=1)
            topic_weights = np.max(topic_distributions, axis=1)
            
            df_copy['lda_topic'] = dominant_topics
            df_copy['topic_weight'] = topic_weights
            
            # Extract topic keywords
            feature_names = vectorizer.get_feature_names_out()
            topics_info = {}
            
            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                top_weights = [topic[i] for i in top_indices]
                
                topics_info[topic_idx] = {
                    'words': top_words,
                    'weights': top_weights
                }
            
            return df_copy, topics_info
            
        except Exception as e:
            print(f"Error in LDA topic modeling: {e}")
            df_copy['lda_topic'] = 0
            df_copy['topic_weight'] = 0
            return df_copy, {}
    
    def analyze_field_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze trends in research fields over time"""
        trends = {}
        
        # Field trends by year
        field_cols = [col for col in df.columns if col.startswith('field_')]
        
        for field_col in field_cols:
            field_name = field_col.replace('field_', '').replace('_', ' ').title()
            yearly_counts = df.groupby('year')[field_col].sum().to_dict()
            trends[field_name] = yearly_counts
        
        # Dominant field trends
        if 'dominant_field' in df.columns:
            dominant_trends = df.groupby(['year', 'dominant_field']).size().unstack(fill_value=0)
            trends['dominant_field_trends'] = dominant_trends.to_dict()
        
        return trends
    
    def get_field_statistics(self, df: pd.DataFrame) -> Dict:
        """Get comprehensive field statistics"""
        stats = {}
        
        # Overall field distribution
        if 'dominant_field' in df.columns:
            field_dist = df['dominant_field'].value_counts().to_dict()
            stats['field_distribution'] = field_dist
        
        # Field distribution by conference
        if 'dominant_field' in df.columns and 'conference' in df.columns:
            conf_field = df.groupby(['conference', 'dominant_field']).size().unstack(fill_value=0)
            stats['field_by_conference'] = conf_field.to_dict()
        
        # Average confidence by field
        if 'field_confidence' in df.columns and 'dominant_field' in df.columns:
            avg_conf = df.groupby('dominant_field')['field_confidence'].mean().to_dict()
            stats['average_confidence'] = avg_conf
        
        return stats
    
    def calculate_field_growth_rates(self, df: pd.DataFrame) -> Dict:
        """Calculate growth rates for each research field"""
        if 'dominant_field' not in df.columns or 'year' not in df.columns:
            return {}
        
        growth_rates = {}
        field_year_counts = df.groupby(['dominant_field', 'year']).size().unstack(fill_value=0)
        
        for field in field_year_counts.index:
            yearly_counts = field_year_counts.loc[field]
            
            # Calculate year-over-year growth rates
            growth_rate_list = []
            for i in range(1, len(yearly_counts)):
                if yearly_counts.iloc[i-1] > 0:
                    growth_rate = (yearly_counts.iloc[i] - yearly_counts.iloc[i-1]) / yearly_counts.iloc[i-1]
                    growth_rate_list.append(growth_rate)
            
            if growth_rate_list:
                avg_growth_rate = np.mean(growth_rate_list)
                growth_rates[field] = {
                    'average_growth_rate': avg_growth_rate,
                    'yearly_growth_rates': growth_rate_list,
                    'total_papers': yearly_counts.sum(),
                    'recent_trend': 'increasing' if len(growth_rate_list) >= 2 and growth_rate_list[-1] > growth_rate_list[-2] else 'stable'
                }
        
        return growth_rates
    
    def identify_emerging_fields(self, df: pd.DataFrame, min_papers: int = 10, growth_threshold: float = 0.3) -> Dict:
        """Identify emerging research fields based on growth patterns"""
        growth_rates = self.calculate_field_growth_rates(df)
        
        emerging_fields = {}
        for field, stats in growth_rates.items():
            if (stats['total_papers'] >= min_papers and 
                stats['average_growth_rate'] > growth_threshold):
                emerging_fields[field] = stats
        
        # Sort by growth rate
        emerging_fields = dict(sorted(emerging_fields.items(), 
                                    key=lambda x: x[1]['average_growth_rate'], 
                                    reverse=True))
        
        return emerging_fields
    
    def analyze_conference_specialization(self, df: pd.DataFrame) -> Dict:
        """Analyze which conferences specialize in which fields"""
        if 'dominant_field' not in df.columns or 'conference' not in df.columns:
            return {}
        
        specialization = {}
        
        # Calculate field distribution for each conference
        for conference in df['conference'].unique():
            conf_data = df[df['conference'] == conference]
            field_dist = conf_data['dominant_field'].value_counts()
            total_papers = len(conf_data)
            
            field_percentages = {field: count/total_papers for field, count in field_dist.items()}
            
            # Find top specializations (fields with > 15% of papers)
            top_specializations = {field: pct for field, pct in field_percentages.items() if pct > 0.15}
            
            specialization[conference] = {
                'field_distribution': field_percentages,
                'top_specializations': top_specializations,
                'total_papers': total_papers,
                'diversity_score': len([pct for pct in field_percentages.values() if pct > 0.05])  # Number of fields with >5% representation
            }
        
        return specialization
    
    def calculate_field_momentum(self, df: pd.DataFrame, recent_years: int = 3) -> Dict:
        """Calculate field momentum based on recent publication trends"""
        if 'dominant_field' not in df.columns or 'year' not in df.columns:
            return {}
        
        max_year = df['year'].max()
        recent_data = df[df['year'] > max_year - recent_years]
        historical_data = df[df['year'] <= max_year - recent_years]
        
        momentum = {}
        
        for field in df['dominant_field'].unique():
            if field == 'Other':
                continue
                
            recent_count = len(recent_data[recent_data['dominant_field'] == field])
            historical_count = len(historical_data[historical_data['dominant_field'] == field])
            
            # Calculate momentum score
            if historical_count > 0:
                momentum_score = recent_count / (historical_count / (len(df['year'].unique()) - recent_years))
            else:
                momentum_score = recent_count  # New field
            
            momentum[field] = {
                'momentum_score': momentum_score,
                'recent_papers': recent_count,
                'historical_average': historical_count / max(1, len(df['year'].unique()) - recent_years),
                'status': 'hot' if momentum_score > 1.5 else 'stable' if momentum_score > 0.8 else 'declining'
            }
        
        return dict(sorted(momentum.items(), key=lambda x: x[1]['momentum_score'], reverse=True))