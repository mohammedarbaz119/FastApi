from typing import List,Union
from llama_index.core.schema import Document
def add_texts_to_documents(
    existing_documents: List[Document],
    text_input: Union[str, List[str]], 
    metadata: dict = None,
    chunk_size: int = None,
    chunk_overlap: int = 0
) -> List[Document]:
    """
    Convert text input into LlamaIndex Document objects and add them to existing document array.
    
    Args:
        existing_documents (List[Document]): Existing array of LlamaIndex Documents
        text_input (Union[str, List[str]]): Single text string or list of text strings
        metadata (dict, optional): Metadata to attach to documents
        chunk_size (int, optional): Size of text chunks if splitting is desired
        chunk_overlap (int, optional): Number of characters to overlap between chunks
        
    Returns:
        List[Document]: Updated list of LlamaIndex Document objects
    """
    # Ensure existing_documents is a list
    if existing_documents is None:
        existing_documents = []
    
    # Get the starting index for new documents
    start_idx = len(existing_documents)
    
    # Convert single string to list for consistent processing
    if isinstance(text_input, str):
        text_input = [text_input]
    
    # Process each text input
    for idx, text in enumerate(text_input):
        # Skip empty texts
        if not text.strip():
            continue
            
        # Create document metadata
        doc_metadata = {
            'doc_id': f'doc_{start_idx + idx}',
            'source': 'User'
        }
        
        # Merge with provided metadata if any
        if metadata:
            doc_metadata.update(metadata)
            
        # If chunking is requested
        if chunk_size:
            # Split text into chunks
            chunks = []
            start = 0
            while start < len(text):
                end = start + chunk_size
                if end > len(text):
                    end = len(text)
                chunk = text[start:end]
                chunks.append(chunk)
                start = end - chunk_overlap
                
            # Create document for each chunk
            for chunk_idx, chunk in enumerate(chunks):
                chunk_metadata = doc_metadata.copy()
                chunk_metadata['chunk_id'] = chunk_idx
                existing_documents.append(Document(
                    text=chunk,
                    metadata=chunk_metadata
                ))
        else:
            # Create single document for entire text
            existing_documents.append(Document(
                text=text,
                metadata=doc_metadata
            ))
    
    return existing_documents