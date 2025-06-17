import re
import string

# A sample list of offensive or low-quality words. You can expand this.
OFFENSIVE_WORDS = {
    'hate', 'violence', 'racist', 'stupid', 'dumb', 'kill', 'idiot', 'nonsense'
}

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def auto_moderate_story(title, content):
    content_clean = clean_text(content)

    # 1. Minimum word count
    if len(content_clean.split()) < 50:
        return False

    # 2. Offensive content check
    if any(offensive_word in content_clean for offensive_word in OFFENSIVE_WORDS):
        return False

    # 3. Title too similar to body
    if title.lower() in content_clean:
        return False

    # 4. Must contain at least 3 sentences
    if len(re.findall(r'\.', content)) < 3:
        return False

    # 5. Check for high repetition of words (overuse of 1 word)
    words = content_clean.split()
    word_freq = {word: words.count(word) for word in set(words)}
    if any(freq / len(words) > 0.15 for freq in word_freq.values()):
        return False

    return True
