from github_helper import GithubRepositoryDataReader
import frontmatter

from typing import Any, Dict, Iterable, List
from minsearch import Index


def filename_filter(filepath, folder_name='_podcast/s'):
    if folder_name in filepath:
        return True
    else:
        return False

def read_github_data():
    allowed_extensions = {"md", "mdx"}

    repo_owner = 'DataTalksClub'
    repo_name = 'datatalksclub.github.io'

    reader = GithubRepositoryDataReader(
        repo_owner,
        repo_name,
        filename_filter=filename_filter,
        allowed_extensions=allowed_extensions
    )
    
    return reader.read()



def parse_data(data_raw):

    data_parsed = []
    for f in data_raw:
        post = frontmatter.loads(f.content)
        data = post.to_dict()
        del data['content']
        data['filename'] = f.filename
        if 'transcript' in data.keys():
            data_parsed.append(data)

    return data_parsed


def extract_only_transcript_text(doc_content):
    transcript_text = " "
    for d in doc_content[1:]:
        if 'line' in d.keys():
            transcript_text += d['line']
        elif 'header' in d.keys():
            transcript_text += d['header']
    
    transcript_text = transcript_text.strip()

    return transcript_text


def sliding_window(
        seq: Iterable[Any],
        size: int,
        step: int
    ) -> List[Dict[str, Any]]:
    """
    Create overlapping chunks from a sequence using a sliding window approach.

    Args:
        seq: The input sequence (string or list) to be chunked.
        size (int): The size of each chunk/window.
        step (int): The step size between consecutive windows.

    Returns:
        list: A list of dictionaries, each containing:
            - 'start': The starting position of the chunk in the original sequence
            - 'content': The chunk content

    Raises:
        ValueError: If size or step are not positive integers.

    Example:
        >>> sliding_window("hello world", size=5, step=3)
        [{'start': 0, 'content': 'hello'}, {'start': 3, 'content': 'lo wo'}]
    """
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")

    n = len(seq)
    result = []
    for i in range(0, n, step):
        batch = seq[i:i+size]
        result.append({'start': i, 'content': batch})
        if i + size > n:
            break

    return result


def chunk_documents(
        documents: Iterable[Dict[str, str]],
        size: int = 30,
        step: int = 15,
        content_field_name: str = 'transcript'
) -> List[Dict[str, str]]:
    """
    Split a collection of documents into smaller chunks using sliding windows.

    Takes documents and breaks their content into overlapping chunks while preserving
    all other document metadata (filename, etc.) in each chunk.

    Args:
        documents: An iterable of document dictionaries. Each document must have a content field.
        size (int, optional): The maximum size of each chunk. Defaults to 2000.
        step (int, optional): The step size between chunks. Defaults to 1000.
        content_field_name (str, optional): The name of the field containing document content.
                                          Defaults to 'content'.

    Returns:
        list: A list of chunk dictionaries. Each chunk contains:
            - All original document fields except the content field
            - 'start': Starting position of the chunk in original content
            - 'content': The chunk content

    Example:
        >>> documents = [{'content': 'long text...', 'filename': 'doc.txt'}]
        >>> chunks = chunk_documents(documents, size=100, step=50)
        >>> # Or with custom content field:
        >>> documents = [{'text': 'long text...', 'filename': 'doc.txt'}]
        >>> chunks = chunk_documents(documents, content_field_name='text')
    """
    results = []

    for doc in documents:
        doc_copy = doc.copy()
        if content_field_name in doc_copy.keys():
            doc_content = doc_copy.pop(content_field_name)
            transcript_text = extract_only_transcript_text(doc_content)
            chunks = sliding_window(transcript_text, size=size, step=step)
            for chunk in chunks:
                chunk.update(doc_copy)
            results.extend(chunks)
        else:
            continue

    return results


def index_documents(documents, chunk: bool = False, chunking_params=None) -> Index:
    """
    Create a searchable index from a collection of documents.

    Args:
        documents: A collection of document dictionaries, each containing at least
                  'content' and 'filename' fields.
        chunk (bool, optional): Whether to chunk documents before indexing.
                               Defaults to False.
        chunking_params (dict, optional): Parameters for document chunking.
                                        Defaults to {'size': 2000, 'step': 1000}.
                                        Only used when chunk=True.

    Returns:
        Index: A fitted minsearch Index object ready for searching.

    Example:
        >>> docs = [{'content': 'Hello world', 'filename': 'doc1.txt'}]
        >>> index = index_documents(docs)
        >>> results = index.search('hello')
    """
    if chunk:
        if chunking_params is None:
            chunking_params = {'size': 30, 'step': 15}
        documents = chunk_documents(documents, **chunking_params)
        print(f"We have generated {len(documents)} chunks from the podcasts")

    index = Index(
        text_fields=["content", "filename"],
    )

    index.fit(documents)
    return index



# Downloading and extracting the github data
data_raw = read_github_data()
print(f"Downloaded {len(data_raw)} podcast transcripts")
# print(data_raw[2])

# Parsing the data to the dictionary format
parsed_data = parse_data(data_raw)

#Chunk the data and index using minsearch
index = index_documents(parsed_data)

# Test the question 
search_result = index.search(
    "how do I make money with AI?",
    num_results=1
)


print(f"First search result for \" how do I make money with AI \" \
      \nseason: {search_result[0]['season']} \
      \nespisode: {search_result[0]['episode']} \
      \ntitle: {search_result[0]['title']}")