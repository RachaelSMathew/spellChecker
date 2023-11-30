# I created a spellchecker with Python. 
### The “dictionary” is collected from the texts of multiple novels, like the Harry Potter Series, Hunger Games, and Chronicles of Narnia, that you can find in the fileDict directory(I’m a big book nerd!). 

**NOTE: This is still the beta version(There might be some hiccups)!**
## Areas for Improvement 
Storage and Time are the main pain points. 
So, I used a cache functionality (i.e., @cache, which is taken from 'from functools import cache') for functions that are called multiple times. 

## How to run:
Download Github zip 
Input this command in the terminal in the spellChecker directory:
`python spellCheck.py [txt file that the user wants to be spellchecked]`

For a word that is incorrectly spelled in the txt file, it will print something like this into the terminal:
```
Instead of [incorrectly spelled word], did you mean?
First choice for correct spelling
Second choice
Third choice
…
```

### Inverted Index:
I went through every single document in the corpus and created an inverted index.
This was the structure of the index:
```
{
	word: {file #: [indexes of positions where word is found]}
}
```

Example:
```
{
	“this”: {4: [3, 5, 70], 6: [4, 45]},
	“tomorrow”: {41: [3, 54, 70], 62: [42, 45]}
}
```

I encoded this inverted index using [delta encoding](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L121) to reduce space.

## Features used to determine if two words are similar

## lastEdit Dictionary: 
A dictionary that holds the times each document was last edited. 
If a document was last edited very recently, there might be a higher chance that this document is more popular and more reliable for correct spelling than a document that was last edited months ago. 
Thus, if a word comes from a lot of documents that were very recently edited, we want to place a higher weight on it than a word that does not. 

### The structure of lastEdit(link):
`{file #: current time - last edited time, file #: current time - last edited time}`
This dictionary is sorted in ascending values.

## Phonetic Code Dictionary:
I’m creating a dictionary where words with the same phonetic code(link) are grouped together. The phonetic code of a word is calculated using metaphone(https://en.wikipedia.org/wiki/Metaphone) and this python library(https://pypi.org/project/Metaphone/). 
For example, the dictionary might look like this:
`{“PJTR“: [“bajador“, “begetter”, “budgetary”]}`

Dictionary of words that have the same length as incorrectly spelled words:
Structure:
`{3: [“cat”, “bat”], 5: ["hello", "pinky"]}`

The popularity of a word in the [inverted dictionary](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L128)

Words that start with the same letter as incorrectly spelled(with a length diff of three max)(https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L139):

## How do we actually spell check??
I read every word from the txt file the user inputted and stripped any leading/trailing funky characters like “!#@$%^&”. 

I created an array called iDict(https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L172) that will hold all the correct spellings of the incorrect spelled word in a ranked order. This is what I’m returning back to the user. 

Strcture of iDict:
[[word_1: Levenshtein Distance], [word_2: Levenshtein Distance]]

Ranking the words that have the same phonetic code as incorrectly spelled:
I find the phonetic code of the word, and if that code doesn’t exist in the phonetic code dictionary I made, the Python library I’m using provides a secondary code.
If the secondary code doesn’t exist, then I skip this step. 

Find the Levenshtein Distance(link) between the incorrectly spelled word and all words with the same phonetic code.

Sort the distances in iDict ascending order(https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L177). 

Ranking the words that start the same as incorrectly spelled:
Find the Levenshtein Distance(link) between the incorrectly spelled word and all words with the same starting letter

Sort the distances in iDict ascending order(https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L177). 

Ranking the words that have the same length as incorrectly spelled:
Find the Levenshtein Distance(link) between the incorrectly spelled word and all words with the same length

Sort the distances in iDict ascending order(https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L177). 

Shortening down iDict even further:
filter the iDict array such that any two elements next to each other are less than .01 in Levenshtein distance (https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L202C8-L202C8)
	compare the popularity of both 
	compare the Levenshtein distance of both (with a more detailed algorithm)

Let's say we have an iDict like this:
[[A: 1.0], [B, 1.0], [C, 2.0]]
Since A and B are less than .01 away from each other, one must go.
If the Levenshtein distance of B to the incorrectly spelled word is less than the distance of A to the incorrectly spelled word, then the resulting iDict will look like this:
[[B, 1.0], [C, 2.0]]
But let's say that A is an insanely popular word(i.e., popularity(A) * 0.1 > popularity(B)), so there is a chance that the user meant to type in A even though it might be farther away from it than B.
Thus, in that case, the resulting iDict will look like this:
[[A, 1.0], [C, 2.0]]

Whatever is left in the iDict is then displayed to the user. This is repeated for every word in the txt file. 
