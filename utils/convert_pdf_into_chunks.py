from chunkr_ai import Chunkr
import asyncio
import os
import json
from typing import List, Optional, Dict, Any


def should_use_mock(pdf_path: str) -> bool:
    """
    Check if we should use mock data instead of hitting the API.
    
    Args:
        pdf_path (str): Path to the PDF file being processed
        
    Returns:
        bool: True if we should use mock data, False otherwise
    """
    # Check if environment is development and file is ArtOfWar.pdf
    is_development = os.getenv('ENVIRONMENT', '').lower() == 'development'
    is_art_of_war = os.path.basename(pdf_path).lower() == 'artofwar.pdf'
    
    return is_development and is_art_of_war


def load_mock_chunks(json_path: str = "ArtOfWar_chunkr_json.json") -> List[Dict[str, Any]]:
    """
    Load mock chunks from the JSON file.
    
    Args:
        json_path (str): Path to the JSON file containing mock chunks
        
    Returns:
        List[Dict[str, Any]]: List of mock chunks converted to the expected format
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        Exception: If there's an error parsing the JSON
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Mock JSON file not found: {json_path}")
    
    try:
        print(f"Loading mock chunks from: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract chunks from the JSON structure
        if 'output' not in data or 'chunks' not in data['output']:
            raise ValueError("Invalid JSON structure: missing 'output.chunks'")
        
        raw_chunks = data['output']['chunks']
        print(f"Found {len(raw_chunks)} mock chunks")
        
        # Convert raw chunks to clean format
        clean_chunks = []
        for i, chunk in enumerate(raw_chunks):
            clean_chunk = convert_mock_chunk_to_clean_format(chunk, i + 1)
            clean_chunks.append(clean_chunk)
        
        return clean_chunks
        
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing JSON file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error loading mock chunks: {str(e)}")


def convert_mock_chunk_to_clean_format(mock_chunk: Dict[str, Any], chunk_number: int) -> Dict[str, Any]:
    """
    Convert a mock chunk from the JSON file to the clean format expected by the application.
    
    Args:
        mock_chunk (Dict[str, Any]): Raw chunk data from the JSON file
        chunk_number (int): Sequential chunk number for reference
        
    Returns:
        Dict[str, Any]: Clean chunk data with readable content
    """
    clean_chunk = {
        'chunk_number': chunk_number,
        'chunk_id': mock_chunk.get('chunk_id', f'mock_chunk_{chunk_number}'),
        'content': '',
        'metadata': {'source': 'mock_data'}
    }
    
    # First, try to get content from the embed field (main text content)
    if 'embed' in mock_chunk and mock_chunk['embed']:
        clean_chunk['content'] = mock_chunk['embed']
        clean_chunk['metadata']['embed_available'] = True
    
    # If no embed, try to extract from segments
    elif 'segments' in mock_chunk and mock_chunk['segments']:
        segment_texts = []
        for segment in mock_chunk['segments']:
            # Try different possible text fields in segments
            if isinstance(segment, dict):
                if 'content' in segment and segment['content']:
                    segment_texts.append(segment['content'])
                elif 'text' in segment and segment['text']:
                    segment_texts.append(segment['text'])
        
        if segment_texts:
            clean_chunk['content'] = '\n'.join(segment_texts)
            clean_chunk['metadata']['source'] = 'mock_segments'
            clean_chunk['metadata']['segment_count'] = len(segment_texts)
    
    # If we still don't have content, use string representation
    if not clean_chunk['content']:
        clean_chunk['content'] = str(mock_chunk)
        clean_chunk['metadata']['source'] = 'mock_string_representation'
    
    # Add content statistics
    content = clean_chunk['content']
    clean_chunk['metadata']['character_count'] = len(content)
    clean_chunk['metadata']['word_count'] = len(content.split()) if content else 0
    
    return clean_chunk


def convert_pdf_to_chunks_sync(pdf_path: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convert a PDF file to chunks using Chunkr AI SDK (synchronous version).
    
    In development mode with ArtOfWar.pdf, uses mock data from ArtOfWar_chunkr_json.json
    instead of hitting the API endpoint.
    
    Args:
        pdf_path (str): Path to the PDF file to be processed
        api_key (str, optional): Chunkr API key. If not provided, will use environment variable
        
    Returns:
        List[Dict[str, Any]]: List of chunks extracted from the PDF with clean text content
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error during processing
    """
    # Validate input file
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    
    # Check if we should use mock data
    if should_use_mock(pdf_path):
        print("Using mock data for development environment...")
        return load_mock_chunks()
    
    # Initialize client
    chunkr = Chunkr(api_key=api_key) if api_key else Chunkr()
    
    try:
        print(f"Processing PDF: {pdf_path}")
        
        # Upload file and wait for processing
        task = chunkr.upload(pdf_path)
        print(f"Task created with ID: {task.task_id}")
        
        # Poll for completion and get chunks
        print("Waiting for processing to complete...")
        task.poll()
        
        if task.output and task.output.chunks:
            print(f"Successfully processed PDF. Found {len(task.output.chunks)} chunks.")
            
            # Convert Chunk objects to clean dictionaries
            clean_chunks = []
            for i, chunk in enumerate(task.output.chunks):
                clean_chunk = extract_clean_content(chunk, i + 1)
                clean_chunks.append(clean_chunk)
            
            return clean_chunks
        else:
            print("No chunks found in the processed document.")
            return []
            
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise
    finally:
        # Clean up
        chunkr.close()


async def convert_pdf_to_chunks_async(pdf_path: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convert a PDF file to chunks using Chunkr AI SDK (asynchronous version).
    
    In development mode with ArtOfWar.pdf, uses mock data from ArtOfWar_chunkr_json.json
    instead of hitting the API endpoint.
    
    Args:
        pdf_path (str): Path to the PDF file to be processed
        api_key (str, optional): Chunkr API key. If not provided, will use environment variable
        
    Returns:
        List[Dict[str, Any]]: List of chunks extracted from the PDF with clean text content
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error during processing
    """
    # Validate input file
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    
    # Check if we should use mock data
    if should_use_mock(pdf_path):
        print("Using mock data for development environment...")
        return load_mock_chunks()
    
    # Initialize client
    chunkr = Chunkr(api_key=api_key) if api_key else Chunkr()
    
    try:
        print(f"Processing PDF: {pdf_path}")
        
        # Upload file and wait for processing
        task = await chunkr.upload(pdf_path)
        print(f"Task created with ID: {task.task_id}")
        
        # Poll for completion and get chunks
        print("Waiting for processing to complete...")
        await task.poll()
        
        if task.output and task.output.chunks:
            print(f"Successfully processed PDF. Found {len(task.output.chunks)} chunks.")
            
            # Convert Chunk objects to clean dictionaries
            clean_chunks = []
            for i, chunk in enumerate(task.output.chunks):
                clean_chunk = extract_clean_content(chunk, i + 1)
                clean_chunks.append(clean_chunk)
            
            return clean_chunks
        else:
            print("No chunks found in the processed document.")
            return []
            
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise
    finally:
        # Clean up
        chunkr.close()


def extract_clean_content(chunk, chunk_number: int) -> Dict[str, Any]:
    """
    Extract clean, readable content from a Chunkr Chunk object.
    
    Args:
        chunk: Chunkr Chunk object
        chunk_number: Sequential chunk number for reference
        
    Returns:
        Dict[str, Any]: Clean chunk data with readable content
    """
    clean_chunk = {
        'chunk_number': chunk_number,
        'chunk_id': getattr(chunk, 'chunk_id', f'chunk_{chunk_number}'),
        'content': '',
        'metadata': {}
    }
    
    # First, try to get content from the embed attribute (usually contains clean text)
    if hasattr(chunk, 'embed') and chunk.embed:
        clean_chunk['content'] = chunk.embed
        clean_chunk['metadata']['source'] = 'embed'
    
    # If no embed, try to extract from segments
    elif hasattr(chunk, 'segments') and chunk.segments:
        segment_texts = []
        for segment in chunk.segments:
            if hasattr(segment, 'content') and segment.content:
                segment_texts.append(segment.content)
            elif hasattr(segment, 'text') and segment.text:
                segment_texts.append(segment.text)
        
        if segment_texts:
            clean_chunk['content'] = '\n'.join(segment_texts)
            clean_chunk['metadata']['source'] = 'segments'
            clean_chunk['metadata']['segment_count'] = len(segment_texts)
    
    # Add additional metadata if available
    if hasattr(chunk, 'chunk_length'):
        clean_chunk['metadata']['chunk_length'] = chunk.chunk_length
    
    # If we still don't have content, fall back to string representation
    if not clean_chunk['content']:
        clean_chunk['content'] = str(chunk)
        clean_chunk['metadata']['source'] = 'string_representation'
    
    # Add content statistics
    content = clean_chunk['content']
    clean_chunk['metadata']['character_count'] = len(content)
    clean_chunk['metadata']['word_count'] = len(content.split()) if content else 0
    
    return clean_chunk


def convert_pdf_to_chunks_with_custom_task(pdf_path: str, api_key: Optional[str] = os.getenv("CHUNKR_API_KEY")) -> List[Dict[str, Any]]:
    """
    Convert a PDF file to chunks using custom task creation (synchronous version).
    This gives more control over the task creation process.
    
    In development mode with ArtOfWar.pdf, uses mock data from ArtOfWar_chunkr_json.json
    instead of hitting the API endpoint.
    
    Args:
        pdf_path (str): Path to the PDF file to be processed
        api_key (str, optional): Chunkr API key. If not provided, will use environment variable
        
    Returns:
        List[Dict[str, Any]]: List of chunks extracted from the PDF with clean text content
    """
    # Validate input file
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    
    # Check if we should use mock data
    if should_use_mock(pdf_path):
        print("Using mock data for development environment...")
        return load_mock_chunks()
    
    # Initialize client
    chunkr = Chunkr(api_key=api_key) if api_key else Chunkr()
    
    try:
        print(f"Creating task for PDF: {pdf_path}")
        
        # Create task without waiting
        task = chunkr.create_task(pdf_path)
        print(f"Task created with ID: {task.task_id}")
        
        # Poll when ready
        print("Polling for task completion...")
        task.poll()
        
        if task.output and task.output.chunks:
            print(f"Successfully processed PDF. Found {len(task.output.chunks)} chunks.")
            
            # Convert Chunk objects to clean dictionaries
            clean_chunks = []
            for i, chunk in enumerate(task.output.chunks):
                clean_chunk = extract_clean_content(chunk, i + 1)
                clean_chunks.append(clean_chunk)
            
            return clean_chunks
        else:
            print("No chunks found in the processed document.")
            return []
            
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise
    finally:
        # Clean up
        chunkr.close()

def get_excerpts(file_path: str) -> List[Dict[str, Any]]:
    """
    Get grouped chunks from a PDF file using word limits.
    When the word limit is exceeded, the group is extended until the next sentence boundary.
    """
    WORD_LIMIT = 800  # Adjust this value as needed

    # If a plain text or markdown file is provided, split locally by WORD_LIMIT
    _, ext = os.path.splitext(file_path)
    if ext.lower() in [".txt", ".md"]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Text file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()

        words = text_content.split()
        text_chunks: List[Dict[str, Any]] = []
        for start_index in range(0, len(words), WORD_LIMIT):
            chunk_words = words[start_index:start_index + WORD_LIMIT]
            content = " ".join(chunk_words).strip()
            if content:
                # Return minimal format: list of dicts with only a `content` key
                text_chunks.append({"content": content})

        return text_chunks

    # Default behavior for PDFs via Chunkr + sentence-aware grouping
    chunks = convert_pdf_to_chunks_with_custom_task(file_path)
    grouped_chunks = []
    
    for chunk in chunks:
        chunk_word_count = len(chunk['content'].split())
        
        if chunk_word_count > WORD_LIMIT:
            # If chunk is already too long, keep it as standalone
            grouped_chunks.append(chunk)
        else:
            # If no chunks exist yet, create the first group
            if not grouped_chunks:
                grouped_chunks.append(chunk)
            else:
                # Check if adding this chunk would exceed the word limit
                current_content = grouped_chunks[-1]['content']
                current_word_count = len(current_content.split())
                
                if current_word_count + chunk_word_count > WORD_LIMIT:
                    # Would exceed limit, need to handle sentence boundary logic
                    combined_content = current_content + " " + chunk['content']
                    words = combined_content.split()
                    
                    # Find the word position that exceeds the limit
                    if len(words) > WORD_LIMIT:
                        # Find the next sentence boundary after the word limit
                        words_up_to_limit = words[:WORD_LIMIT]
                        remaining_words = words[WORD_LIMIT:]
                        
                        # Look for sentence endings in the remaining words
                        sentence_end_found = False
                        additional_words = []
                        
                        for i, word in enumerate(remaining_words):
                            additional_words.append(word)
                            # Check if this word ends a sentence (contains period, exclamation, or question mark)
                            if any(punct in word for punct in ['.', '!', '?']):
                                sentence_end_found = True
                                break
                        
                        if sentence_end_found:
                            # Extend current group until sentence boundary
                            final_words = words_up_to_limit + additional_words
                            grouped_chunks[-1]['content'] = ' '.join(final_words)
                            
                            # Create new group with remaining content if any
                            remaining_content = ' '.join(remaining_words[len(additional_words):])
                            if remaining_content.strip():
                                new_chunk = {
                                    'chunk_number': len(grouped_chunks) + 1,
                                    'chunk_id': f'split_chunk_{len(grouped_chunks) + 1}',
                                    'content': remaining_content.strip(),
                                    'metadata': chunk.get('metadata', {}).copy()
                                }
                                grouped_chunks.append(new_chunk)
                        else:
                            # No sentence boundary found in reasonable distance, 
                            # just start a new group with the current chunk
                            grouped_chunks.append(chunk)
                    else:
                        # Combined content doesn't exceed limit, safe to merge
                        grouped_chunks[-1]['content'] = combined_content
                else:
                    # Safe to merge with the last group
                    grouped_chunks[-1]['content'] += " " + chunk['content']

    return grouped_chunks

def save_chunks_to_markdown(chunks: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save chunks to a markdown file.
    
    Args:
        chunks (List[Dict[str, Any]]): List of chunks to save
        output_path (str): Path to save the markdown file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Document Chunks\n\n")
        
        for chunk in chunks:
            chunk_num = chunk.get('chunk_number', 'Unknown')
            f.write(f"## Chunk {chunk_num}\n\n")
            
            # Write metadata if available
            if 'metadata' in chunk:
                metadata = chunk['metadata']
                f.write("**Metadata:**\n")
                for key, value in metadata.items():
                    f.write(f"- {key}: {value}\n")
                f.write("\n")
            
            # Write chunk content
            content = chunk.get('content', '')
            if content:
                f.write(f"**Content:**\n\n{content}\n\n")
            else:
                f.write("*No content available*\n\n")
            
            f.write("---\n\n")
    
    print(f"Chunks saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    # Example with synchronous version
    pdf_file = "example.pdf"
    
    # For mock data usage, set environment and use ArtOfWar.pdf:
    # os.environ['ENVIRONMENT'] = 'development'
    # pdf_file = "ArtOfWar.pdf"
    
    try:
        # Synchronous processing
        chunks = convert_pdf_to_chunks_sync(pdf_file)
        
        # Save to markdown
        save_chunks_to_markdown(chunks, "output_chunks.md")
        
        # Print first chunk as example
        if chunks:
            print(f"\nFirst chunk preview:")
            print(f"Content length: {len(chunks[0]['content'])} characters")
            print(f"Preview: {chunks[0]['content'][:500]}...")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example with asynchronous version
    async def async_example():
        try:
            chunks = await convert_pdf_to_chunks_async(pdf_file)
            print(f"Async processing completed. Found {len(chunks)} chunks.")
        except Exception as e:
            print(f"Async error: {e}")
    
    # Uncomment to run async example
    # asyncio.run(async_example())


