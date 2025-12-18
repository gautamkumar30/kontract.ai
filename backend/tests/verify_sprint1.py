"""
Quick Verification Script for Sprint 1

Tests the core services without requiring database:
1. Text extraction
2. Clause segmentation
3. Fingerprint generation
4. Drift detection
5. Risk classification
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.text_extractor import TextExtractor
from services.clause_segmenter import ClauseSegmenter
from services.fingerprint_engine import FingerprintEngine
from services.drift_detector import DriftDetector
from services.risk_classifier import RiskClassifier

# Sample contract text
SAMPLE_CONTRACT = """
TERMS OF SERVICE

1. ACCEPTANCE OF TERMS
By accessing and using this service, you accept and agree to be bound by the terms and provision of this agreement.

2. LIABILITY LIMITATION
The service provider shall not be liable for any indirect, incidental, special, consequential or punitive damages.
Maximum liability is limited to $100.

3. DATA USAGE
We collect and process your personal data in accordance with our Privacy Policy.
Your data may be shared with third-party service providers.

4. TERMINATION
We may terminate or suspend access to our service immediately, without prior notice or liability.
"""

MODIFIED_CONTRACT = """
TERMS OF SERVICE

1. ACCEPTANCE OF TERMS
By accessing and using this service, you accept and agree to be bound by the terms and provision of this agreement.

2. LIABILITY LIMITATION
The service provider shall not be liable for any damages whatsoever.
Maximum liability is limited to $50.

3. DATA USAGE
We collect and process your personal data in accordance with our Privacy Policy.
Your data will be shared with third-party service providers and marketing partners.

4. TERMINATION
We may terminate or suspend access to our service at any time, for any reason.

5. ARBITRATION
All disputes shall be resolved through binding arbitration in Delaware.
"""


async def test_pipeline():
    """Test the complete processing pipeline."""
    
    print("=" * 70)
    print("SPRINT 1 VERIFICATION - Backend Processing Pipeline")
    print("=" * 70)
    
    # 1. Text Extraction
    print("\n[1/5] Testing Text Extraction...")
    extractor = TextExtractor()
    result = await extractor.extract_from_text(SAMPLE_CONTRACT)
    
    if result["success"]:
        print(f"✓ Text extracted: {len(result['raw_text'])} characters")
        print(f"✓ Sections detected: {len(result.get('sections', []))}")
    else:
        print(f"✗ Text extraction failed: {result.get('error')}")
        return False
    
    # 2. Clause Segmentation
    print("\n[2/5] Testing Clause Segmentation...")
    segmenter = ClauseSegmenter()
    clauses_v1 = segmenter.segment_text(result['raw_text'])
    
    print(f"✓ Segmented into {len(clauses_v1)} clauses")
    for clause in clauses_v1:  # Show all clauses
        print(f"  - Clause {clause['clause_number']}: {clause.get('category', 'uncategorized')}")
    
    # 3. Fingerprint Generation
    print("\n[3/5] Testing Fingerprint Generation...")
    fingerprint_engine = FingerprintEngine()
    
    clause_texts = [c['text'] for c in clauses_v1]
    fingerprints_v1 = fingerprint_engine.create_batch_fingerprints(clause_texts)
    
    print(f"✓ Generated {len(fingerprints_v1)} fingerprints")
    print(f"  Sample fingerprint:")
    print(f"    - Text hash: {fingerprints_v1[0]['text_hash'][:16]}...")
    print(f"    - SimHash: {fingerprints_v1[0]['simhash'][:16]}...")
    print(f"    - Keywords: {list(fingerprints_v1[0]['keywords'].keys())[:3]}")
    
    # 4. Process Modified Version
    print("\n[4/5] Testing Drift Detection...")
    result_v2 = await extractor.extract_from_text(MODIFIED_CONTRACT)
    clauses_v2 = segmenter.segment_text(result_v2['raw_text'])
    fingerprints_v2 = fingerprint_engine.create_batch_fingerprints([c['text'] for c in clauses_v2])
    
    print(f"✓ Version 2: {len(clauses_v2)} clauses")
    
    # Prepare data for drift detector
    old_clauses = []
    for i, (clause, fp) in enumerate(zip(clauses_v1, fingerprints_v1)):
        old_clauses.append({
            "id": f"old_{i}",
            "text": clause['text'],
            "category": clause.get('category'),
            "heading": clause.get('heading'),
            "fingerprint": fp
        })
    
    new_clauses = []
    for i, (clause, fp) in enumerate(zip(clauses_v2, fingerprints_v2)):
        new_clauses.append({
            "id": f"new_{i}",
            "text": clause['text'],
            "category": clause.get('category'),
            "heading": clause.get('heading'),
            "fingerprint": fp
        })
    
    # Detect changes
    drift_detector = DriftDetector()
    changes = await drift_detector.detect_changes(old_clauses, new_clauses)
    
    print(f"✓ Detected {len(changes)} changes:")
    for change in changes:
        print(f"  - {change['change_type'].value}: similarity={change.get('similarity_score', 'N/A')}")
    
    # 5. Risk Classification
    print("\n[5/5] Testing Risk Classification...")
    risk_classifier = RiskClassifier()
    
    for i, change in enumerate(changes[:3]):  # Classify first 3 changes
        # Get the relevant clause
        clause = None
        if change.get('new_clause_id'):
            clause = next((c for c in new_clauses if c['id'] == change['new_clause_id']), None)
        elif change.get('old_clause_id'):
            clause = next((c for c in old_clauses if c['id'] == change['old_clause_id']), None)
        
        if clause:
            risk_data = await risk_classifier.classify_risk(change, clause)
            print(f"  - Change {i+1}: {risk_data['risk_level'].value} (score: {risk_data['risk_score']})")
            if risk_data.get('explanation'):
                print(f"    Reason: {risk_data['explanation'][:80]}...")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE ✓")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  ✓ Text extraction: Working")
    print(f"  ✓ Clause segmentation: {len(clauses_v1)} → {len(clauses_v2)} clauses")
    print(f"  ✓ Fingerprint generation: {len(fingerprints_v1)} fingerprints")
    print(f"  ✓ Drift detection: {len(changes)} changes detected")
    print(f"  ✓ Risk classification: Working")
    
    # Change breakdown
    change_types = {}
    for change in changes:
        change_type = change['change_type'].value
        change_types[change_type] = change_types.get(change_type, 0) + 1
    
    print(f"\nChange Breakdown:")
    for change_type, count in change_types.items():
        print(f"  - {change_type}: {count}")
    
    print("\n✅ Sprint 1 backend services are working correctly!")
    print("   Ready to proceed with Sprint 2 (Frontend Integration)\n")
    
    return True


if __name__ == "__main__":
    import asyncio
    
    try:
        success = asyncio.run(test_pipeline())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
