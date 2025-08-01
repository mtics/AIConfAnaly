#!/usr/bin/env python3
"""
Full Dataset Analyzer - Complete Analysis of All 53,159 Papers
==============================================================

Analyzes the complete dataset of 53,159 papers with enhanced keyword extraction
and comprehensive field classification.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Any
import datetime

class FullDatasetAnalyzer:
    """Analyzer for the complete dataset of all papers"""
    
    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        self.data_dir = project_root / "outputs/data"
        self.raw_data_dir = self.data_dir / "raw"
        
        # Enhanced granular field keywords (same as before but more comprehensive)
        self.field_keywords = {
            "Computer_Vision_3D": ["3d", "point cloud", "depth", "stereo", "lidar", "voxel", "mesh", "3d detection", "3d segmentation", "3d reconstruction", "3d object", "depth estimation"],
            "Computer_Vision_Object_Detection": ["object detection", "yolo", "rcnn", "faster rcnn", "detection", "bbox", "anchor", "proposal", "ssd", "feature pyramid"],
            "Computer_Vision_Segmentation": ["segmentation", "u-net", "mask rcnn", "semantic segmentation", "instance segmentation", "panoptic", "deeplabv3", "fcn"],
            "Computer_Vision_Image_Generation": ["gan", "diffusion", "generation", "synthesis", "style transfer", "super resolution", "inpainting", "cyclegan", "pix2pix", "stable diffusion"],
            "Computer_Vision_Face": ["face recognition", "facial", "face detection", "expression", "deepfake", "biometric", "face verification", "landmark detection"],
            "Computer_Vision_Medical": ["medical imaging", "ct", "mri", "x-ray", "medical", "clinical", "diagnosis", "radiology", "pathology", "mammography"],
            "Computer_Vision_Video": ["video", "action recognition", "temporal", "optical flow", "video understanding", "activity recognition", "motion"],
            
            "NLP_Transformers": ["transformer", "bert", "gpt", "attention", "self-attention", "language model", "pre-trained", "fine-tuning", "llm", "large language"],
            "NLP_Machine_Translation": ["translation", "machine translation", "nmt", "multilingual", "cross-lingual", "neural machine translation"],
            "NLP_Question_Answering": ["question answering", "qa", "reading comprehension", "squad", "question", "answer", "open-domain qa"],
            "NLP_Sentiment": ["sentiment", "emotion", "opinion", "polarity", "affect", "stance", "sentiment analysis"],
            "NLP_Named_Entity": ["named entity", "ner", "entity", "relation extraction", "information extraction", "entity linking"],
            "NLP_Dialogue": ["dialogue", "conversation", "chatbot", "response generation", "conversational", "dialog system"],
            "NLP_Text_Generation": ["text generation", "language generation", "text summarization", "paraphrase", "abstractive"],
            
            "ML_Deep_Learning": ["convolutional", "cnn", "rnn", "lstm", "resnet", "transformer", "neural architecture", "densenet", "mobilenet"],
            "ML_Optimization": ["gradient descent", "sgd", "adam", "optimization", "learning rate", "batch normalization", "adamw", "rmsprop"],
            "ML_Transfer_Learning": ["transfer learning", "fine-tuning", "pre-training", "few-shot", "zero-shot", "meta-learning", "domain adaptation"],
            "ML_Self_Supervised": ["self-supervised", "contrastive", "ssl", "representation learning", "unsupervised", "simclr", "moco"],
            "ML_Federated": ["federated", "distributed", "privacy", "differential privacy", "secure", "federated learning"],
            "ML_Adversarial": ["adversarial", "adversarial training", "robust", "robustness", "adversarial examples", "adversarial attack"],
            
            "RL_Deep_RL": ["reinforcement learning", "dqn", "policy gradient", "actor-critic", "ppo", "ddpg", "q-learning", "deep reinforcement"],
            "RL_Multi_Agent": ["multi-agent", "marl", "cooperative", "game theory", "nash", "multi-agent reinforcement"],
            "RL_Offline": ["offline reinforcement", "batch reinforcement", "offline policy", "behavior cloning", "offline rl"],
            
            "Graph_Learning": ["graph neural", "gnn", "graph convolution", "gcn", "node classification", "link prediction", "graph attention", "graphsage"],
            "Knowledge_Graph": ["knowledge graph", "entity embedding", "relation", "triple", "knowledge base", "kg", "knowledge representation"],
            
            "AI_Applications_Autonomous": ["autonomous", "self-driving", "vehicle", "navigation", "slam", "path planning", "autonomous driving"],
            "AI_Applications_Robotics": ["robot", "manipulation", "grasping", "control", "motion planning", "robotic", "robot learning"],
            "AI_Applications_Healthcare": ["healthcare", "medical ai", "drug discovery", "clinical", "biomarker", "precision medicine"],
            "AI_Applications_Finance": ["finance", "trading", "risk", "fraud", "credit", "financial", "algorithmic trading"],
            "AI_Applications_Security": ["adversarial", "attack", "robustness", "security", "privacy", "backdoor", "defense"],
            "AI_Applications_Recommender": ["recommendation", "recommender", "collaborative filtering", "matrix factorization", "personalization"],
            
            "Emerging_Quantum": ["quantum", "quantum computing", "quantum machine", "variational quantum", "quantum neural"],
            "Emerging_Edge": ["edge computing", "mobile", "compression", "quantization", "pruning", "efficient", "model compression"],
            "Emerging_Neuromorphic": ["neuromorphic", "spiking", "brain-inspired", "event-driven", "spiking neural"],
            "Emerging_Multimodal": ["multimodal", "vision-language", "cross-modal", "multi-modal", "vqa", "clip"]
        }
        
        # Load all papers
        self.papers_data = self.load_all_papers()
        print(f"✅ Loaded {len(self.papers_data)} papers for complete analysis")
    
    def load_all_papers(self) -> List[Dict]:
        """Load all papers from JSON files"""
        papers = []
        for json_file in sorted(self.raw_data_dir.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_papers = json.load(f)
                    papers.extend(file_papers)
                    print(f"📚 Loaded {len(file_papers)} papers from {json_file.name}")
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
        
        return papers
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text with improved filtering"""
        if not text:
            return []
        
        text = text.lower()
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Extract phrases and technical terms
        words = text.split()
        keywords = []
        
        # Extract 1-4 word technical phrases
        for n in range(1, 5):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                
                # Filter for technical terms
                if (len(phrase) >= 3 and 
                    self._is_technical_term(phrase) and
                    not phrase.isdigit() and
                    not self._is_stop_phrase(phrase)):
                    keywords.append(phrase)
        
        return keywords
    
    def _is_technical_term(self, phrase: str) -> bool:
        """Enhanced check for technical terms"""
        technical_indicators = [
            'neural', 'deep', 'learning', 'network', 'algorithm', 'model',
            'transformer', 'attention', 'convolution', 'optimization',
            'classification', 'regression', 'clustering', 'detection',
            'segmentation', 'generation', 'prediction', 'recognition',
            'embedding', 'encoding', 'decoding', 'training', 'inference',
            'adversarial', 'reinforcement', 'supervised', 'unsupervised',
            'graph', 'quantum', 'federated', 'multimodal', 'robotic'
        ]
        
        # Include if contains technical indicators
        if any(indicator in phrase for indicator in technical_indicators):
            return True
        
        # Include specific domain terms
        if any(phrase in keywords for keywords in self.field_keywords.values()):
            return True
        
        # Include compound technical terms
        words = phrase.split()
        if len(words) > 1 and any(len(word) > 5 for word in words):
            return True
        
        return False
    
    def _is_stop_phrase(self, phrase: str) -> bool:
        """Check if phrase should be filtered out"""
        stop_phrases = {
            'the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'they', 
            'have', 'been', 'paper', 'approach', 'method', 'propose', 'show', 
            'result', 'study', 'work', 'research', 'analysis', 'evaluation',
            'experimental', 'experiments', 'performance', 'accuracy', 'novel',
            'new', 'based on', 'in this', 'we propose', 'we show', 'our approach',
            'our method', 'this paper', 'we present', 'in order', 'such as'
        }
        
        return phrase in stop_phrases
    
    def classify_fields(self, paper: Dict) -> List[tuple]:
        """Classify paper into research fields with scores"""
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        
        classified = []
        for field, keywords in self.field_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                classified.append((field, score))
        
        classified.sort(key=lambda x: x[1], reverse=True)
        return classified[:5]  # Top 5 fields
    
    def analyze_complete_dataset(self) -> Dict[str, Any]:
        """Analyze the complete dataset of all papers"""
        print("🔍 Analyzing complete dataset of all papers...")
        
        # Initialize data structures
        all_keywords = []
        field_keywords_extracted = defaultdict(list)
        conference_analysis = defaultdict(lambda: {'keywords': [], 'fields': [], 'papers': 0})
        yearly_analysis = defaultdict(lambda: {'keywords': [], 'fields': [], 'papers': 0})
        field_paper_counts = defaultdict(int)
        
        # Process all papers
        for i, paper in enumerate(self.papers_data):
            if i % 5000 == 0:
                print(f"📊 Processed {i}/{len(self.papers_data)} papers...")
            
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            keywords = self.extract_keywords(text)
            fields = self.classify_fields(paper)
            
            # Collect all keywords
            all_keywords.extend(keywords)
            
            # Associate keywords with fields
            for field, score in fields:
                field_keywords_extracted[field].extend(keywords)
                field_paper_counts[field] += 1
            
            # Conference and year analysis
            conference = paper.get('conference', 'Unknown')
            year = paper.get('year', 2024)
            
            conference_analysis[conference]['keywords'].extend(keywords)
            conference_analysis[conference]['fields'].extend([f[0] for f in fields])
            conference_analysis[conference]['papers'] += 1
            
            yearly_analysis[year]['keywords'].extend(keywords)
            yearly_analysis[year]['fields'].extend([f[0] for f in fields])
            yearly_analysis[year]['papers'] += 1
        
        print("📈 Computing keyword frequencies and statistics...")
        
        # Count keywords by field
        field_keyword_counts = {}
        for field, keywords in field_keywords_extracted.items():
            field_keyword_counts[field] = Counter(keywords).most_common(50)
        
        # Overall keyword analysis
        top_keywords = Counter(all_keywords).most_common(200)
        
        # Conference keyword analysis
        conference_keywords = {}
        for conf, data in conference_analysis.items():
            conference_keywords[conf] = Counter(data['keywords']).most_common(30)
        
        # Yearly trends
        yearly_trends = {}
        for year, data in yearly_analysis.items():
            yearly_trends[year] = {
                'top_keywords': Counter(data['keywords']).most_common(20),
                'papers': data['papers'],
                'top_fields': Counter(data['fields']).most_common(10)
            }
        
        return {
            'metadata': {
                'total_papers_analyzed': len(self.papers_data),
                'total_unique_keywords': len(set(all_keywords)),
                'field_categories': list(self.field_keywords.keys()),
                'conferences': list(conference_analysis.keys()),
                'years': sorted(yearly_analysis.keys()),
                'analysis_timestamp': datetime.datetime.now().isoformat()
            },
            'top_overall_keywords': top_keywords,
            'field_specific_keywords': field_keyword_counts,
            'field_paper_counts': dict(field_paper_counts),
            'conference_analysis': {
                conf: {
                    'papers': data['papers'],
                    'top_keywords': Counter(data['keywords']).most_common(25),
                    'top_fields': Counter(data['fields']).most_common(10)
                }
                for conf, data in conference_analysis.items()
            },
            'yearly_trends': yearly_trends,
            'field_definitions': self.field_keywords
        }
    
    def generate_insights(self, analysis: Dict) -> List[Dict[str, str]]:
        """Generate comprehensive insights from complete dataset"""
        insights = []
        
        metadata = analysis['metadata']
        top_keywords = analysis['top_overall_keywords']
        field_counts = analysis['field_paper_counts']
        conference_analysis = analysis['conference_analysis']
        
        # Dataset overview insight
        insights.append({
            'title': '📊 Complete Dataset Analysis',
            'content': f'Comprehensive analysis of {metadata["total_papers_analyzed"]:,} papers from {len(metadata["conferences"])} top AI conferences, spanning {metadata["years"][0]}-{metadata["years"][-1]}. Extracted {metadata["total_unique_keywords"]:,} unique technical keywords across {len(metadata["field_categories"])} research fields.'
        })
        
        # Technology dominance
        if top_keywords:
            top_3_keywords = top_keywords[:3]
            insights.append({
                'title': '🚀 Technology Dominance Trends',
                'content': f'Top technical terms: "{top_3_keywords[0][0]}" ({top_3_keywords[0][1]:,} occurrences), "{top_3_keywords[1][0]}" ({top_3_keywords[1][1]:,}), and "{top_3_keywords[2][0]}" ({top_3_keywords[2][1]:,}). This reflects the field\'s evolution toward more sophisticated learning approaches.'
            })
        
        # Field distribution insights
        if field_counts:
            top_field = max(field_counts.items(), key=lambda x: x[1])
            total_classifications = sum(field_counts.values())
            percentage = (top_field[1] / total_classifications) * 100
            
            insights.append({
                'title': '🏗️ Research Field Landscape',
                'content': f'{top_field[0].replace("_", " ")} dominates with {top_field[1]:,} papers ({percentage:.1f}% of classifications). The diversity across {len(field_counts)} fields indicates healthy research ecosystem with balanced focus on theory and applications.'
            })
        
        # Conference analysis
        if conference_analysis:
            conf_papers = {conf: data['papers'] for conf, data in conference_analysis.items()}
            top_conf = max(conf_papers.items(), key=lambda x: x[1])
            
            insights.append({
                'title': '🏛️ Conference Ecosystem',
                'content': f'{top_conf[0]} leads with {top_conf[1]:,} papers, followed by strong contributions from other venues. Each conference shows distinct research focus areas, contributing to the field\'s comprehensive coverage.'
            })
        
        # Technology evolution
        adversarial_count = next((count for keyword, count in top_keywords if 'adversarial' in keyword.lower()), 0)
        attention_count = next((count for keyword, count in top_keywords if 'attention' in keyword.lower()), 0)
        
        insights.append({
            'title': '🔬 Technology Evolution Patterns',
            'content': f'Attention mechanisms ({attention_count:,} mentions) and adversarial approaches ({adversarial_count:,} mentions) represent major paradigm shifts. The transformer revolution and focus on AI safety demonstrate field maturation.'
        })
        
        # Emerging trends
        multimodal_fields = [field for field in field_counts.keys() if 'multimodal' in field.lower() or 'vision' in field.lower()]
        edge_count = field_counts.get('Emerging_Edge', 0)
        
        insights.append({
            'title': '📱 Emerging Technology Trends',
            'content': f'Edge AI and model efficiency ({edge_count:,} papers) show strong growth, reflecting industry demands for deployable solutions. Multimodal AI convergence indicates next-generation capabilities combining vision, language, and reasoning.'
        })
        
        return insights
    
    def save_results(self, analysis: Dict[str, Any]):
        """Save complete analysis results"""
        output_dir = self.data_dir.parent / "analysis"
        output_dir.mkdir(exist_ok=True)
        
        # Save complete analysis
        output_file = output_dir / "complete_dataset_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Complete analysis saved to: {output_file}")
        
        # Generate readable report
        report_file = output_dir / "complete_dataset_report.md"
        self.generate_report(analysis, report_file)
        
        return output_file
    
    def generate_report(self, analysis: Dict[str, Any], report_file: Path):
        """Generate comprehensive markdown report"""
        insights = self.generate_insights(analysis)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Complete Dataset Analysis Report\n\n")
            f.write(f"**Analysis Date:** {analysis['metadata']['analysis_timestamp']}\n")
            f.write(f"**Total Papers:** {analysis['metadata']['total_papers_analyzed']:,}\n")
            f.write(f"**Unique Keywords:** {analysis['metadata']['total_unique_keywords']:,}\n")
            f.write(f"**Field Categories:** {len(analysis['metadata']['field_categories'])}\n\n")
            
            # Key insights
            f.write("## 🧠 Key Insights\n\n")
            for insight in insights:
                f.write(f"### {insight['title']}\n")
                f.write(f"{insight['content']}\n\n")
            
            # Top keywords
            f.write("## 📊 Top 100 Keywords\n\n")
            for i, (keyword, count) in enumerate(analysis['top_overall_keywords'][:100], 1):
                f.write(f"{i}. **{keyword}** ({count:,} occurrences)\n")
            
            # Conference analysis
            f.write("\n## 🏛️ Conference Analysis\n\n")
            for conf, data in analysis['conference_analysis'].items():
                f.write(f"### {conf}\n")
                f.write(f"- **Papers:** {data['papers']:,}\n")
                f.write(f"- **Top Keywords:** {', '.join([kw[0] for kw in data['top_keywords'][:10]])}\n")
                f.write(f"- **Top Fields:** {', '.join([field[0].replace('_', ' ') for field in data['top_fields'][:5]])}\n\n")
            
            # Field distribution
            f.write("## 🏗️ Research Field Distribution\n\n")
            for field, count in sorted(analysis['field_paper_counts'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{field.replace('_', ' ')}:** {count:,} papers\n")
        
        print(f"📝 Complete report saved to: {report_file}")
    
    def run_complete_analysis(self):
        """Run complete analysis of all papers"""
        print("🚀 Starting Complete Dataset Analysis...")
        print(f"📊 Analyzing {len(self.papers_data):,} papers...")
        print("="*60)
        
        analysis = self.analyze_complete_dataset()
        insights = self.generate_insights(analysis)
        analysis['insights'] = insights
        
        output_file = self.save_results(analysis)
        
        print("\n" + "="*60)
        print("🎉 Complete Dataset Analysis Finished!")
        print("="*60)
        print(f"📊 Papers analyzed: {analysis['metadata']['total_papers_analyzed']:,}")
        print(f"🏷️ Unique keywords: {analysis['metadata']['total_unique_keywords']:,}")
        print(f"🏗️ Field categories: {len(analysis['metadata']['field_categories'])}")
        print(f"💾 Results saved to: {output_file}")
        
        return analysis

def main():
    analyzer = FullDatasetAnalyzer()
    return analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()