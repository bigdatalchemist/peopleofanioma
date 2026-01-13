import re
from typing import List, Dict, Tuple, Optional
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class AniomaSemanticAnalyzer:
    """
    Advanced semantic analyzer for detecting Anioma-related content
    even when not explicitly mentioned
    """
    
    def __init__(self):
        # Load spaCy model (install: python -m spacy download en_core_web_md)
        try:
            self.nlp = spacy.load("en_core_web_md")
        except:
            self.nlp = spacy.load("en_core_web_sm")
        
        # Core Anioma keywords and entities
        self.explicit_keywords = [
            'anioma', 'aniocha', 'ndokwa', 'ikhinan', 'olu', 'ukwuani',
            'igbo', 'delta igbo', 'asaba', 'ogwashi-uku', 'kwale',
            'aboh', 'akwukwu-igbo', 'isoko', 'urhobo'
        ]
        
        # Semantic patterns and concepts
        self.semantic_patterns = {
            'cultural_concepts': [
                'igwe', 'obi', 'ndi', 'ofo', 'ogene', 'ekwe',
                'cultural festival', 'traditional ruler', 'kingdom',
                'ancestral home', 'clan meeting', 'cultural heritage'
            ],
            'geographical_features': [
                'niger river', 'delta region', 'riverine area',
                'niger delta', 'coastal community', 'river bank'
            ],
            'historical_figures': [
                'nwaoboshi', 'asenime', 'mordi', 'onyeme',
                'emordi', 'okonji', 'okobia', 'okolie'
            ],
            'cultural_events': [
                'new yam festival', 'ofala festival', 'igwe coronation',
                'cultural day', 'homecoming', 'age grade meeting'
            ],
            'political_entities': [
                'delta north', 'anioma congress', 'anioma association',
                'anioma development', 'anioma youth', 'anioma women'
            ]
        }
        
        # Location mappings
        self.anioma_locations = {
            'asaba', 'ogwashi-uku', 'kwale', 'aboh', 'akwukwu-igbo',
            'umuaji', 'okpanam', 'ibusa', 'okwe', 'iselle-ukwu',
            'onicha-olona', 'isheagu', 'ejeme', 'ilah', 'umbo'
        }
        
        # Initialize TF-IDF for semantic similarity
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            stop_words='english',
            max_features=5000
        )
        
        # Reference documents for semantic matching
        self.reference_docs = self._load_reference_documents()
        
    def _load_reference_documents(self) -> List[str]:
        """Load reference documents about Anioma for similarity matching"""
        return [
            "Anioma people are an Igbo subgroup in Delta State Nigeria",
            "Anioma consists of regions like Aniocha Ndokwa Ika and Oshimili",
            "Anioma culture includes festivals like new yam festival and ofala",
            "Anioma traditional rulers are called Igwe or Obi",
            "Anioma towns include Asaba Ogwashi-Uku Kwale Aboh and Akwukwu-Igbo",
            "Anioma political representation in Delta North senatorial district",
            "Anioma cultural heritage includes masquerades music and dance",
            "Anioma development associations promote community progress",
            "Anioma youth empowerment and educational initiatives",
            "Anioma women in commerce and cultural preservation"
        ]
    
    def analyze_text(self, text: str, title: str = "") -> Dict:
        """
        Comprehensive analysis of text for Anioma relevance
        """
        if not text:
            return {
                'is_anioma_related': False,
                'relevance_score': 0.0,
                'detection_methods': [],
                'semantic_tags': [],
                'entities': {},
                'sentiment': 0.0
            }
        
        full_text = f"{title} {text}".lower()
        doc = self.nlp(full_text)
        
        results = {
            'is_anioma_related': False,
            'relevance_score': 0.0,
            'detection_methods': [],
            'semantic_tags': [],
            'entities': self._extract_entities(doc),
            'sentiment': self._analyze_sentiment(doc),
            'keywords_found': []
        }
        
        # Check multiple detection methods
        detection_scores = []
        
        # 1. Direct keyword matching
        keyword_score = self._check_keyword_match(full_text)
        if keyword_score > 0:
            detection_scores.append(('direct_keyword', keyword_score))
            results['detection_methods'].append('direct_keyword')
            results['keywords_found'].extend(
                [k for k in self.explicit_keywords if k in full_text]
            )
        
        # 2. Semantic pattern matching
        semantic_score, semantic_tags = self._check_semantic_patterns(full_text, doc)
        if semantic_score > 0:
            detection_scores.append(('semantic_pattern', semantic_score))
            results['detection_methods'].append('semantic_pattern')
            results['semantic_tags'].extend(semantic_tags)
        
        # 3. Location mention
        location_score, locations = self._check_locations(doc)
        if location_score > 0:
            detection_scores.append(('location', location_score))
            results['detection_methods'].append('location')
            results['semantic_tags'].extend([f"location:{loc}" for loc in locations])
        
        # 4. Entity-based detection
        entity_score, entity_tags = self._check_entities(doc)
        if entity_score > 0:
            detection_scores.append(('entity', entity_score))
            results['detection_methods'].append('entity')
            results['semantic_tags'].extend(entity_tags)
        
        # 5. Semantic similarity with reference docs
        similarity_score = self._check_semantic_similarity(full_text)
        if similarity_score > 0.3:  # Threshold
            detection_scores.append(('semantic_similarity', similarity_score))
            results['detection_methods'].append('semantic_similarity')
        
        # Calculate overall relevance score
        if detection_scores:
            results['relevance_score'] = max([score for _, score in detection_scores])
            results['is_anioma_related'] = results['relevance_score'] > 0.2
        
        # Add boost for multiple detection methods
        if len(results['detection_methods']) > 1:
            results['relevance_score'] *= 1.2
            results['relevance_score'] = min(results['relevance_score'], 1.0)
        
        return results
    
    def _check_keyword_match(self, text: str) -> float:
        """Check for direct keyword mentions"""
        score = 0.0
        for keyword in self.explicit_keywords:
            if keyword in text:
                score += 0.5
                # Boost for exact 'anioma' mention
                if keyword == 'anioma':
                    score += 0.3
        return min(score, 1.0)
    
    def _check_semantic_patterns(self, text: str, doc) -> Tuple[float, List[str]]:
        """Check for semantic patterns"""
        score = 0.0
        tags = []
        
        for category, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    score += 0.2
                    tags.append(f"{category}:{pattern}")
        
        # Check for n-grams
        for i in range(len(doc) - 2):
            trigram = ' '.join([doc[j].text.lower() for j in range(i, i+3)])
            if any(pattern in trigram for pattern in [
                'delta state igbo', 'niger delta igbo',
                'cultural heritage preservation', 'traditional ruler installation'
            ]):
                score += 0.3
                tags.append(f"trigram:{trigram}")
        
        return min(score, 1.0), tags
    
    def _check_locations(self, doc) -> Tuple[float, List[str]]:
        """Check for location mentions"""
        locations = []
        score = 0.0
        
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:
                loc_lower = ent.text.lower()
                if loc_lower in self.anioma_locations:
                    locations.append(loc_lower)
                    score += 0.4
        
        return min(score, 1.0), locations
    
    def _extract_entities(self, doc) -> Dict:
        """Extract named entities"""
        entities = defaultdict(list)
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        return dict(entities)
    
    def _check_entities(self, doc) -> Tuple[float, List[str]]:
        """Check for relevant entities"""
        score = 0.0
        tags = []
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                # Check for known Anioma surnames
                if any(name in ent.text.lower() for name in [
                    'oboshi', 'mordi', 'onyeme', 'okonji', 'okobia'
                ]):
                    score += 0.3
                    tags.append(f"person:{ent.text}")
            
            elif ent.label_ == 'ORG':
                if 'anioma' in ent.text.lower() or 'aniocha' in ent.text.lower():
                    score += 0.4
                    tags.append(f"organization:{ent.text}")
        
        return min(score, 1.0), tags
    
    def _check_semantic_similarity(self, text: str) -> float:
        """Check semantic similarity with reference documents"""
        try:
            all_texts = self.reference_docs + [text]
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity with each reference doc
            similarities = []
            text_vector = tfidf_matrix[-1]
            
            for i in range(len(self.reference_docs)):
                ref_vector = tfidf_matrix[i]
                similarity = cosine_similarity(text_vector, ref_vector)[0][0]
                similarities.append(similarity)
            
            return max(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error in semantic similarity: {e}")
            return 0.0
    
    def _analyze_sentiment(self, doc) -> float:
        """Simple sentiment analysis"""
        # This can be enhanced with a proper sentiment analysis model
        positive_words = {'development', 'progress', 'growth', 'success', 
                         'achievement', 'celebration', 'unity', 'peace'}
        negative_words = {'conflict', 'crisis', 'protest', 'violence',
                         'destruction', 'dispute', 'attack'}
        
        sentiment = 0.0
        for token in doc:
            if token.text.lower() in positive_words:
                sentiment += 0.1
            elif token.text.lower() in negative_words:
                sentiment -= 0.1
        
        return max(-1.0, min(1.0, sentiment))