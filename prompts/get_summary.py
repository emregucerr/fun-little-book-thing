def system_prompt() -> str:
    return """
    You are a helpful assistant that summarizes a book by its title.
    """

def user_prompt(book: str) -> str:
    return f"""
    Summarize the following book:
    {book}
    """