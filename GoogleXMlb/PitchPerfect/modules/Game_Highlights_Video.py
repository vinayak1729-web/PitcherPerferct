import statsapi

def display_game_highlights(gamePk):
    """
    Fetch and display the highlight videos for a specific game.

    Parameters:
        gamePk (int): The unique game ID.

    Returns:
        None
    """
    try:
        # Fetch the highlight video data
        highlights = statsapi.game_highlights(gamePk)
        
        # If the response is a string, handle it as a direct highlight
        if isinstance(highlights, str):
            print(f"Highlight: {highlights}")
            return

        # If the response is a dictionary, process the structured data
        if isinstance(highlights, dict):
            items = highlights.get('highlights', {}).get('items', [])
            if not items:
                print(f"No highlight videos found for game ID: {gamePk}")
                return
            
            print(f"Highlights for Game ID: {gamePk}")
            for idx, highlight in enumerate(items, 1):
                title = highlight.get('headline', 'No Title')
                playbacks = highlight.get('playbacks', [])
                playback_url = playbacks[-1]['url'] if playbacks else 'No URL'
                print(f"{idx}. {title}")
                print(f"   Watch: {playback_url}")
        else:
            print(f"Unexpected response format: {type(highlights)}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
game_id =744980  # Replace with a valid game ID
display_game_highlights(game_id)
