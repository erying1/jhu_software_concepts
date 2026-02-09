"""
Improved detail page parser for GradCafe
Targets the actual <dl> structure used on detail pages
"""

import re
from bs4 import BeautifulSoup

def _parse_detail_page_html_improved(entry_url: str, html: str = None):
    """
    Parse detail data from HTML - IMPROVED version
    
    This version:
    1. Targets the actual <dl> structure GradCafe uses
    2. Extracts comments properly
    3. Handles multiple formats
    4. Provides better error handling
    """
    default = {
        "comments": None,
        "term": None,
        "citizenship": None,
        "gpa": None,
        "gre_total": None,
        "gre_v": None,
        "gre_q": None,
        "gre_aw": None,
    }
    
    if not entry_url:
        return default
    
    try:
        # If HTML not provided, fetch it
        if html is None:
            import time
            time.sleep(0.5)  # Longer delay for better success rate
            from urllib import request
            opener = request.build_opener()
            opener.addheaders = [("User-Agent", "jhu-module2-scraper")]
            with opener.open(entry_url, timeout=15) as resp:  # Longer timeout
                html = resp.read().decode("utf-8", errors="ignore")
        
        if not html:
            return default
        
        soup = BeautifulSoup(html, "html.parser")
        result = default.copy()
        
        # ===== METHOD 1: Parse <dl> structure (most reliable) =====
        # GradCafe uses <dt>Label:</dt><dd>Value</dd> structure
        
        dl_elements = soup.find_all('dl')
        for dl in dl_elements:
            dt_tags = dl.find_all('dt')
            for dt in dt_tags:
                label = dt.get_text(strip=True).lower()
                dd = dt.find_next_sibling('dd')
                if not dd:
                    continue
                value = dd.get_text(strip=True)
                
                # GPA
                if 'gpa' in label and not result['gpa']:
                    gpa_match = re.search(r'(\d+\.?\d*)', value)
                    if gpa_match:
                        try:
                            gpa_val = float(gpa_match.group(1))
                            if 0 < gpa_val <= 4.5:
                                result['gpa'] = gpa_val
                        except:
                            pass
                
                # GRE Verbal
                if ('gre' in label and 'verbal' in label) or label == 'gre v':
                    if not result['gre_v']:
                        gre_match = re.search(r'(\d{3})', value)
                        if gre_match:
                            try:
                                val = int(gre_match.group(1))
                                if 130 <= val <= 170:
                                    result['gre_v'] = val
                            except:
                                pass
                
                # GRE Quant
                if ('gre' in label and 'quant' in label) or label == 'gre q':
                    if not result['gre_q']:
                        gre_match = re.search(r'(\d{3})', value)
                        if gre_match:
                            try:
                                val = int(gre_match.group(1))
                                if 130 <= val <= 170:
                                    result['gre_q'] = val
                            except:
                                pass
                
                # GRE Writing
                if ('gre' in label and ('writing' in label or 'aw' in label)):
                    if not result['gre_aw']:
                        aw_match = re.search(r'(\d+\.?\d*)', value)
                        if aw_match:
                            try:
                                val = float(aw_match.group(1))
                                if 0 <= val <= 6:
                                    result['gre_aw'] = val
                            except:
                                pass
                
                # Term/Season
                if 'term' in label or 'season' in label or 'semester' in label:
                    if not result['term']:
                        term_match = re.search(r'(Fall|Spring|Summer|Winter)\s*(\d{4})', value, re.I)
                        if term_match:
                            result['term'] = f"{term_match.group(1).capitalize()} {term_match.group(2)}"
                
                # Citizenship
                if 'student' in label or 'status' in label or 'citizenship' in label:
                    if not result['citizenship']:
                        if 'international' in value.lower():
                            result['citizenship'] = "International"
                        elif any(word in value.lower() for word in ['american', 'domestic', 'u.s', 'us']):
                            result['citizenship'] = "American"
                        else:
                            result['citizenship'] = "Other"
                
                # Comments
                if 'comment' in label or 'note' in label:
                    if not result['comments'] and value and len(value) > 5:
                        result['comments'] = value
        
        # ===== METHOD 2: Fallback regex search (if <dl> failed) =====
        if not result['gpa'] or not result['citizenship']:
            page_text = soup.get_text()
            
            # GPA fallback
            if not result['gpa']:
                gpa_patterns = [
                    r'GPA[:\s]+(\d+\.?\d*)',
                    r'gpa[:\s]+(\d+\.?\d*)',
                    r'Undergrad GPA[:\s]+(\d+\.?\d*)',
                ]
                for pattern in gpa_patterns:
                    match = re.search(pattern, page_text, re.I)
                    if match:
                        try:
                            gpa_val = float(match.group(1))
                            if 0 < gpa_val <= 4.5:
                                result['gpa'] = gpa_val
                                break
                        except:
                            pass
            
            # Citizenship fallback
            if not result['citizenship']:
                if 'international' in page_text.lower():
                    result['citizenship'] = "International"
                elif any(word in page_text.lower() for word in ['american', 'domestic']):
                    result['citizenship'] = "American"
        
        # Calculate GRE total
        if result['gre_v'] and result['gre_q']:
            result['gre_total'] = result['gre_v'] + result['gre_q']
        
        return result
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error parsing {entry_url}: {e}")
        return default


# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    # Test on a real GradCafe URL
    test_url = "https://www.thegradcafe.com/result/993761"
    
    print("Testing improved parser...")
    print("=" * 60)
    
    result = _parse_detail_page_html_improved(test_url)
    
    print(f"URL: {test_url}")
    print(f"GPA: {result.get('gpa')}")
    print(f"GRE V: {result.get('gre_v')}")
    print(f"GRE Q: {result.get('gre_q')}")
    print(f"GRE AW: {result.get('gre_aw')}")
    print(f"Term: {result.get('term')}")
    print(f"Citizenship: {result.get('citizenship')}")
    print(f"Comments: {result.get('comments')}")
    print("=" * 60)
