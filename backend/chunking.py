def chunk_text(pages_data: list[dict], chunk_size=1200, chunk_overlap=300):
    """
    Splits page text into smaller, overlapping chunks while preserving
    page number metadata.
    """
    chunks = []
    
    for page in pages_data:
        text = page["text"]
        page_num = page["page"]
        
        # If the page has very little text, keep it as a single chunk
        if len(text) <= chunk_size:
            chunks.append({
                "text": text,
                "page": page_num
            })
            continue

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_str = text[start:end]
            
            chunks.append({
                "text": chunk_str,
                "page": page_num
            })
            
            # Step forward by chunk_size minus overlap
            start += (chunk_size - chunk_overlap)
            
    return chunks