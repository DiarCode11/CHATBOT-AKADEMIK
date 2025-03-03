def find_overlap(text1: str, text2: str, min_overlap_length=20):
    """
    Find overlapping text between two chunks and return the overlap index in first chunk.
    
    Args:
        text1 (str): First text chunk
        text2 (str): Second text chunk
        min_overlap_length (int): Minimum length of overlap to consider (default: 20)
        
    Returns:
        tuple: (overlap_text, overlap_index, first_chunk_without_overlap)
    """
    # Normalize texts by removing only extra spaces, preserving newlines
    def normalize_text(text):
        lines = text.split('\n')
        normalized_lines = [' '.join(line.split()) for line in lines]
        return '\n'.join(normalized_lines)
    
    original_text1 = text1  # Save original text before normalization
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    len1, len2 = len(text1), len(text2)
    min_len = min(len1, len2)
    
    longest_overlap = None
    
    # Try different window sizes starting from the largest possible
    for window_size in range(min_len, min_overlap_length - 1, -1):
        # Check end of text1 against start of text2
        end_text1 = text1[-window_size:]
        if end_text1 in text2[:window_size + 10]:
            longest_overlap = end_text1
            break
        
        # Check start of text2 against end of text1
        start_text2 = text2[:window_size]
        if start_text2 in text1[-window_size - 10:]:
            longest_overlap = start_text2
            break

    return longest_overlap