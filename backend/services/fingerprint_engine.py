"""
Fingerprint Engine Service

Creates semantic fingerprints of clauses for change detection.
Uses TF-IDF, SimHash, and keyword extraction.
"""

import hashlib
import re
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class FingerprintEngine:
    """Service for creating clause fingerprints."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def create_fingerprint(self, text: str) -> Dict[str, any]:
        """
        Create a fingerprint for a clause.
        
        Args:
            text: Clause text
            
        Returns:
            Fingerprint dictionary
        """
        # Normalize text
        normalized_text = self._normalize_text(text)
        
        # Create text hash
        text_hash = self._create_hash(normalized_text)
        
        # Create SimHash
        simhash = self._create_simhash(normalized_text)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        # Create TF-IDF vector (will be computed in batch later)
        tfidf_vector = None
        
        return {
            "text_hash": text_hash,
            "simhash": simhash,
            "tfidf_vector": tfidf_vector,
            "keywords": keywords
        }
    
    def create_batch_fingerprints(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Create fingerprints for multiple clauses (more efficient).
        
        Args:
            texts: List of clause texts
            
        Returns:
            List of fingerprint dictionaries
        """
        fingerprints = []
        
        # Normalize all texts
        normalized_texts = [self._normalize_text(t) for t in texts]
        
        # Compute TF-IDF vectors for all texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(normalized_texts)
            tfidf_vectors = tfidf_matrix.toarray().tolist()
        except:
            tfidf_vectors = [None] * len(texts)
        
        # Create fingerprints
        for idx, text in enumerate(texts):
            fingerprint = {
                "text_hash": self._create_hash(normalized_texts[idx]),
                "simhash": self._create_simhash(normalized_texts[idx]),
                "tfidf_vector": tfidf_vectors[idx],
                "keywords": self._extract_keywords(text)
            }
            fingerprints.append(fingerprint)
        
        return fingerprints
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for fingerprinting."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep alphanumeric and spaces)
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        return text.strip()
    
    @staticmethod
    def _create_hash(text: str) -> str:
        """Create SHA-256 hash of text."""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def _create_simhash(text: str, hash_bits: int = 64) -> str:
        """
        Create SimHash for near-duplicate detection.
        
        Args:
            text: Normalized text
            hash_bits: Number of bits in hash
            
        Returns:
            SimHash as hex string
        """
        # Tokenize
        tokens = text.split()
        
        # Initialize bit vector
        v = [0] * hash_bits
        
        # Process each token
        for token in tokens:
            # Hash token
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            
            # Update bit vector
            for i in range(hash_bits):
                if h & (1 << i):
                    v[i] += 1
                else:
                    v[i] -= 1
        
        # Create fingerprint
        fingerprint = 0
        for i in range(hash_bits):
            if v[i] > 0:
                fingerprint |= (1 << i)
        
        return hex(fingerprint)[2:]
    
    @staticmethod
    def _extract_keywords(text: str, top_n: int = 10) -> Dict[str, float]:
        """
        Extract top keywords from text.
        
        Args:
            text: Clause text
            top_n: Number of keywords to extract
            
        Returns:
            Dictionary of keywords with weights
        """
        # Simple keyword extraction based on word frequency
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Count frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N with normalized weights
        total = sum(count for _, count in sorted_words[:top_n])
        if total == 0:
            return {}
        
        return {
            word: count / total
            for word, count in sorted_words[:top_n]
        }
    
    @staticmethod
    def calculate_similarity(fp1: Dict[str, any], fp2: Dict[str, any]) -> float:
        """
        Calculate similarity between two fingerprints.
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            Similarity score (0-1)
        """
        # If text hashes are identical, return 1.0
        if fp1["text_hash"] == fp2["text_hash"]:
            return 1.0
        
        # Calculate SimHash similarity
        simhash_similarity = FingerprintEngine._simhash_similarity(
            fp1["simhash"], fp2["simhash"]
        )
        
        # Calculate TF-IDF cosine similarity if available
        tfidf_similarity = 0.0
        if fp1.get("tfidf_vector") and fp2.get("tfidf_vector"):
            try:
                vec1 = np.array(fp1["tfidf_vector"]).reshape(1, -1)
                vec2 = np.array(fp2["tfidf_vector"]).reshape(1, -1)
                tfidf_similarity = cosine_similarity(vec1, vec2)[0][0]
            except:
                pass
        
        # Calculate keyword overlap
        keyword_similarity = FingerprintEngine._keyword_similarity(
            fp1.get("keywords", {}), fp2.get("keywords", {})
        )
        
        # Weighted average
        weights = {
            "simhash": 0.3,
            "tfidf": 0.5,
            "keywords": 0.2
        }
        
        similarity = (
            weights["simhash"] * simhash_similarity +
            weights["tfidf"] * tfidf_similarity +
            weights["keywords"] * keyword_similarity
        )
        
        return min(1.0, max(0.0, similarity))
    
    @staticmethod
    def _simhash_similarity(hash1: str, hash2: str) -> float:
        """Calculate similarity between two SimHashes."""
        try:
            # Convert to integers
            h1 = int(hash1, 16)
            h2 = int(hash2, 16)
            
            # Count differing bits (Hamming distance)
            xor = h1 ^ h2
            hamming_distance = bin(xor).count('1')
            
            # Convert to similarity (0-1)
            max_bits = 64
            similarity = 1.0 - (hamming_distance / max_bits)
            
            return similarity
        except:
            return 0.0
    
    @staticmethod
    def _keyword_similarity(kw1: Dict[str, float], kw2: Dict[str, float]) -> float:
        """Calculate similarity between keyword sets."""
        if not kw1 or not kw2:
            return 0.0
        
        # Get common keywords
        common = set(kw1.keys()) & set(kw2.keys())
        
        if not common:
            return 0.0
        
        # Calculate weighted overlap
        overlap = sum(min(kw1[k], kw2[k]) for k in common)
        total = sum(max(kw1.get(k, 0), kw2.get(k, 0)) for k in set(kw1.keys()) | set(kw2.keys()))
        
        return overlap / total if total > 0 else 0.0
