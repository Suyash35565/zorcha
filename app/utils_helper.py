from fuzzywuzzy import fuzz

# Function to perform fuzzy search
def fuzzy_search_comments(commentText, searchText, threshold=80):
    score = fuzz.partial_ratio(commentText.lower(), searchText.lower())
    if score >= threshold:
        return True
    return False