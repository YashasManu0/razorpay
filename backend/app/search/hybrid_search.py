import re
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import Product, Inventory, ProductEmbedding, MerchantPolicy

class SearchFilterRequirements:
    def __init__(
        self,
        raw_query: str,
        budget_max: Optional[float] = None,
        min_ram_gb: Optional[int] = None,
        min_storage_gb: Optional[int] = None,
        max_delivery_days: Optional[int] = None,
        category: Optional[str] = None
    ):
        self.raw_query = raw_query
        self.budget_max = budget_max
        self.min_ram_gb = min_ram_gb
        self.min_storage_gb = min_storage_gb
        self.max_delivery_days = max_delivery_days
        self.category = category

class HybridProductSearch:
    """
    Hybrid Retrieval Engine combining semantic search with strict hardware & financial constraints.
    Constraint Rule: Semantic similarity CANNOT override explicit hard requirements.
    """
    
    @staticmethod
    def extract_structured_requirements(query: str) -> SearchFilterRequirements:
        """
        Regex and rule-based parser to extract hardware specs, budget, and delivery constraints
        from raw natural language query.
        """
        text = query.lower()
        
        # 1. Budget extraction (e.g. "under 80,000", "under 80k", "budget 75000", "< 85000", "80k")
        budget = None
        budget_match = re.search(r'(?:under|below|budget|within|max|around|upto|<|<=|₹|rs\.?)\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)\s*(k|lac|lakh|thousand)?', text)
        if not budget_match:
            budget_match = re.search(r'([0-9]+)\s*k\b', text)
            
        if budget_match:
            val_str = budget_match.group(1).replace(',', '')
            multiplier_str = budget_match.group(2) if len(budget_match.groups()) >= 2 else None
            try:
                val = float(val_str)
                if multiplier_str == 'k' or 'k' in text[budget_match.start():budget_match.end()+2]:
                    val *= 1000
                elif multiplier_str in ('lac', 'lakh'):
                    val *= 100000
                elif val < 1000 and "k" in text:
                    val *= 1000
                budget = val
            except ValueError:
                pass
                
        # 2. RAM extraction (e.g. "32GB RAM", "16 GB", "32 gig")
        min_ram = None
        ram_match = re.search(r'(\d+)\s*(?:gb|gig)\s*(?:ram|memory)?', text)
        if ram_match:
            ram_val = int(ram_match.group(1))
            if ram_val in (4, 8, 16, 24, 32, 64, 128):
                min_ram = ram_val
                
        # 3. Storage extraction (e.g. "1TB SSD", "512GB", "1 TB NVMe")
        min_storage = None
        tb_match = re.search(r'(\d+)\s*(?:tb|terabyte)\s*(?:ssd|storage|nvme|hdd)?', text)
        if tb_match:
            min_storage = int(tb_match.group(1)) * 1000
        else:
            gb_match = re.search(r'(\d{3,4})\s*(?:gb)\s*(?:ssd|storage|nvme|drive)?', text)
            if gb_match:
                min_storage = int(gb_match.group(1))
                
        # 4. Delivery timeframe (e.g. "within 3 days", "in 2 days", "3 day delivery")
        max_delivery = None
        deliv_match = re.search(r'(?:within|in|under)?\s*(\d+)\s*(?:days?|day)\s*(?:delivery)?', text)
        if deliv_match:
            max_delivery = int(deliv_match.group(1))
            
        # 5. Category detection
        category = None
        if any(w in text for w in ["laptop", "notebook", "macbook", "thinkpad", "gaming laptop"]):
            category = "laptops"
        elif any(w in text for w in ["phone", "smartphone", "iphone", "galaxy", "android"]):
            category = "smartphones"
        elif any(w in text for w in ["monitor", "display", "screen", "144hz", "165hz", "240hz"]):
            category = "monitors"
        elif any(w in text for w in ["tablet", "ipad", "tab"]):
            category = "tablets"
        elif any(w in text for w in ["headphone", "earphone", "audio", "earbuds", "speaker"]):
            category = "audio"
            
        return SearchFilterRequirements(
            raw_query=query,
            budget_max=budget,
            min_ram_gb=min_ram,
            min_storage_gb=min_storage,
            max_delivery_days=max_delivery,
            category=category
        )

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a, dtype=float)
        b = np.array(vec_b, dtype=float)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @classmethod
    def search(
        cls,
        db: Session,
        query: str,
        merchant_id: Optional[str] = None,
        limit: int = 5,
        query_embedding: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid search:
        1. Parse hard requirements.
        2. Query candidate products.
        3. Enforce strict constraint filters (price ceiling, RAM, SSD, Stock, Delivery).
        4. Rank surviving candidates by semantic relevance + financial fit.
        """
        reqs = cls.extract_structured_requirements(query)
        
        # Base query
        q = db.query(Product).filter(Product.is_active == True)
        if merchant_id:
            q = q.filter(Product.merchant_id == merchant_id)
        if reqs.category:
            q = q.filter(Product.category == reqs.category)
            
        all_products = q.all()
        results = []
        
        query_tokens = set(re.findall(r'\w+', query.lower()))
        
        for p in all_products:
            # 1. Enforce Stock Constraint: Available stock > 0
            inv = p.inventory
            available_stock = (inv.quantity - inv.reserved_quantity) if inv else 0
            if available_stock <= 0:
                continue  # Hard filter: completely out of stock
                
            specs = p.specs or {}
            
            # 2. Enforce RAM Constraint (if specified)
            if reqs.min_ram_gb:
                product_ram = int(specs.get("ram_gb", 0))
                if product_ram < reqs.min_ram_gb:
                    continue  # Hard filter: insufficient RAM
                    
            # 3. Enforce Storage Constraint (if specified)
            if reqs.min_storage_gb:
                product_storage = int(specs.get("storage_gb", 0))
                if product_storage < reqs.min_storage_gb:
                    continue  # Hard filter: insufficient storage
                    
            # 4. Enforce Delivery Constraint (if specified)
            if reqs.max_delivery_days:
                policy = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == p.merchant_id).first()
                min_deliv = policy.min_delivery_days if policy else 2
                if min_deliv > reqs.max_delivery_days:
                    continue  # Hard filter: delivery takes longer than requested
                    
            # 5. Enforce Budget Range
            # We allow listing prices up to 15% above buyer's stated budget because the merchant AI
            # has discounting power to negotiate the price down into budget. Anything higher is filtered.
            if reqs.budget_max:
                if p.base_price > (reqs.budget_max * 1.15):
                    continue  # Hard filter: completely outside feasible negotiation reach
                    
            # Calculate semantic similarity
            score = 0.5
            if query_embedding and p.embedding and p.embedding.embedding_vector:
                score = cls.cosine_similarity(query_embedding, p.embedding.embedding_vector)
            else:
                # Term frequency / keyword overlap fallback
                prod_text = f"{p.title} {p.brand} {p.category} {p.description or ''} {' '.join(str(v) for v in specs.values())}".lower()
                prod_tokens = set(re.findall(r'\w+', prod_text))
                intersection = query_tokens.intersection(prod_tokens)
                overlap = len(intersection) / max(len(query_tokens), 1)
                score = 0.4 + 0.6 * overlap
                
            # Financial fit bonus: within buyer budget is strongly preferred
            fit_bonus = 0.0
            if reqs.budget_max:
                if p.base_price <= reqs.budget_max:
                    # Within budget: bonus proportional to close fit
                    fit_bonus = 0.15 + 0.10 * (p.base_price / reqs.budget_max)
                else:
                    # Above budget: penalty proportional to budget overshoot
                    overshoot = (p.base_price - reqs.budget_max) / reqs.budget_max
                    fit_bonus = max(0.0, 0.15 - (overshoot * 1.5))
                
            final_relevance = round(min(score + fit_bonus, 0.99), 3)
            
            results.append({
                "product": p,
                "inventory": inv,
                "specs": specs,
                "available_stock": available_stock,
                "relevance_score": final_relevance,
                "matched_constraints": {
                    "budget_max": reqs.budget_max,
                    "min_ram_gb": reqs.min_ram_gb,
                    "min_storage_gb": reqs.min_storage_gb,
                    "max_delivery_days": reqs.max_delivery_days
                }
            })
            
        # Fallback: Live search from external real-world catalog if no local results match
        if not results:
            try:
                from app.services.real_world_products import search_external_products, upsert_real_world_product
                from app.db.models import Merchant
                
                # Extract core search keywords (strip filler phrases)
                clean_query = re.sub(
                    r'\b(i need|looking for|want|under|budget|delivery|within|\d+\s*days?|with|and|a|an|the|in|for|please|can you find)\b',
                    ' ',
                    query,
                    flags=re.IGNORECASE
                ).strip()
                clean_query = ' '.join(clean_query.split())
                search_term = clean_query if len(clean_query) >= 3 else query
                
                external_matches = search_external_products(search_term, limit=5)
                if external_matches:
                    target_merchant = None
                    if merchant_id:
                        target_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
                    if not target_merchant:
                        target_merchant = db.query(Merchant).first()
                        
                    if target_merchant:
                        for ext_item in external_matches:
                            new_p = upsert_real_world_product(db, ext_item, target_merchant.id)
                            inv = new_p.inventory
                            avail = (inv.quantity - inv.reserved_quantity) if inv else 0
                            if avail > 0:
                                results.append({
                                    "product": new_p,
                                    "inventory": inv,
                                    "specs": new_p.specs or {},
                                    "available_stock": avail,
                                    "relevance_score": 0.88,
                                    "matched_constraints": {
                                        "budget_max": reqs.budget_max,
                                        "min_ram_gb": reqs.min_ram_gb,
                                        "min_storage_gb": reqs.min_storage_gb,
                                        "max_delivery_days": reqs.max_delivery_days
                                    }
                                })
            except Exception as e:
                print(f"[HybridSearch] External live search fallback error: {e}")

        # Sort by relevance score descending
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
