def chunk_text(pages_data: list[dict], chunk_size=500, chunk_overlap=50):
    """
    Splits page text into smaller, overlapping chunks while preserving
    page number metadata.
    """
    
    chunks = []
    
    for page in pages_data:
        text = page["text"]
        page_num = page["page"]
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_str = text[start:end]
            
            chunks.append({
                "text": chunk_str,
                "page": page_num
            })
            
            start += max(1,(chunk_size - chunk_overlap))
            
    return chunks