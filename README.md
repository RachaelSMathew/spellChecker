# So I created a spellchecker with Python. 
The “dictionary” is collected from the texts of multiple novels, like the Harry Potter Series, Hunger Games, and Chronicles of Narnia, that you can find in the `fileDict` directory(I’m a big book nerd!). 

**NOTE: This is still the beta version(There might be some hiccups, you obviously need a dictionary of thousands of documents to make this more accurate)!**
## Areas for Improvement 
**_Storage of Corpus_ and _Execution Time_ are the main pain points.**
So, I used a cache functionality (i.e., `@cache`, which is taken from `from functools import cache`) for functions that are called multiple times. 

### I want to attempt [using Redis and SQLAlchemy](https://levelup.gitconnected.com/caching-data-with-redis-and-sqlalchemy-in-python-a-step-by-step-guide-97f898f55ef) to cache data
> Caching is a powerful technique to improve the performance of applications by storing frequently accessed data in a fast, in-memory storage system. Redis, a popular in-memory data store, provides excellent support for caching in Python applications.

## How to run program:
Download the [Github zip file](https://github.com/RachaelSMathew/spellChecker/tree/main)

Input this command in the terminal inside the `spellChecker` directory:

`python spellCheck.py [txt file that you want spellchecked]`

For a word that is incorrectly spelled in the txt file, it will print something like this into the terminal:
```
Instead of [incorrectly spelled word], did you mean?
First choice for correct spelling
Second choice
Third choice
…
```
### The Noisy Channel Model

> In this model, the goal is to find the intended word given a word where the letters have been scrambled in some manner.
> 
![Noisy Channel Model](https://sandipanweb.files.wordpress.com/2017/05/im01.png?w=676)

**The correct spelling of a word will be the one with the highest probability in the Noisy Channel Model**

### Inverted Index:
I went through every document and word in the corpus and created an inverted index.

I removed the documents' unnecessary whitespace and the leading/trailing funky characters like "!@#$%^&".

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

## Features used to determine if two words are similar(i.e., one is the correct spelling of another)

## lastEdit Dictionary: 
A dictionary that holds the times each document was last edited. 
If a document was last edited very recently, there might be a higher chance that this document is more popular and more reliable for correct spelling than a document that was last edited months ago. 

Thus, if a word comes from many recently edited documents, we want to place a higher weight on it than a word that does not. 

The lastEdit values are used when [determining popularity](https://github.com/RachaelSMathew/spellChecker/blob/1342ebf17b79052d2e37c9affcc1925738bee0f5/spellCheck.py#L81).

### The structure of [lastEdit](https://github.com/RachaelSMathew/spellChecker/blob/1342ebf17b79052d2e37c9affcc1925738bee0f5/spellCheck.py):
`{file #: current time - last edited time, file #: current time - last edited time}`

This dictionary is sorted in ascending values.

## Phonetic Code Dictionary:
I’m creating a dictionary where words with the same [phonetic code](https://en.wikipedia.org/wiki/Phonetic_algorithm) are grouped together. 

The phonetic code of a word is calculated using [metaphone](https://en.wikipedia.org/wiki/Metaphone) and [this python library](https://pypi.org/project/Metaphone/). 

For example, the dictionary might look like this:
`{“PJTR“: [“bajador“, “begetter”, “budgetary”]}`

## Dictionary of words that have the same length as incorrectly spelled words:

Structure: `{3: [“cat”, “bat”], 5: ["hello", "pinky"]}`

## The popularity of a word from the [inverted dictionary](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L128)

## Words that [start with the same letter](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L139) as incorrectly spelled(with a length diff of three max)

## So, how do we actually spell check?
I read every word from the txt file the user inputted and stripped any leading/trailing funky characters like “!#@$%^&”. 

I created an array called [iDict](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L172) that will hold all the correct spellings of the incorrectly spelled word in a ranked order. 

This is what I’m returning back to the user. 

Structure of iDict:
`[[word_1: Levenshtein Distance], [word_2: Levenshtein Distance]]`

### Ranking the words that have the same phonetic code as incorrectly spelled:
I find the phonetic code of the word, and if that code doesn’t exist in the phonetic code dictionary I made, the Python library I’m using provides a secondary code.
If the secondary code doesn’t exist, then I skip this step. 

Find the [Levenshtein Distance](https://www.educative.io/answers/the-levenshtein-distance-algorithm) between the incorrectly spelled word and all words with the same phonetic code.

[Sort the distances](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L177) in iDict ascending order. 

### Ranking the words that start the same as incorrectly spelled:
Find the [Levenshtein Distance](https://www.educative.io/answers/the-levenshtein-distance-algorithm) between the incorrectly spelled word and all words with the same starting letter

[Sort the distances](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L177) in iDict ascending order. 

### Ranking the words that have the same length as incorrectly spelled:
Find the [Levenshtein Distance](https://www.educative.io/answers/the-levenshtein-distance-algorithm) between the incorrectly spelled word and all words with the same length

[Sort the distances](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L177) in iDict ascending order. 

### Shortening down iDict even further:
Filter the iDict array such that any two elements next to each other are less than .01 in [Levenshtein distance](https://github.com/RachaelSMathew/spellChecker/blob/2fd9d16e9638dfbbd6503e47e78461047765b133/spellCheck.py#L202C8-L202C8)

	- compare the popularity of both 
 
	- compare the Levenshtein distance of both (with a more detailed algorithm)

Let's say we have an iDict like this:

`[[A: 1.0], [B, 1.0], [C, 2.0]]`

Since A and B are less than .01 away from each other, one must go.
If the Levenshtein distance of B to the incorrectly spelled word is less than the distance of A to the incorrectly spelled word, then the resulting iDict will look like this:

`[[B, 1.0], [C, 2.0]]`

But let's say that A is an **insanely popular word**(i.e., `popularity(A) * 0.1 > popularity(B)`), so there is a chance that the user meant to type in A even though it might be farther away from it than B.
Thus, in that case, the resulting iDict will look like this:

`[[A, 1.0], [C, 2.0]]`

**You made it this far? Congrats.**

Whatever is left in the iDict is then displayed to the user. This is repeated for every word in the txt file. 

## Levenshtein Algorithm [More Detailed](https://github.com/RachaelSMathew/spellChecker/blob/fa5b0362567e4187a319c66480aee228acb80b14/spellCheck.py#L70-L72)
Let's say we have an incorrect word, "wdsh" and we have two options for the potentially correct spelling, "wash" and wish".

There is a higher chance that the user meant to type in "wash" because "a" is closer to "d" than it is to "i".

So, let's think about the distance between characters on a keyboard when figuring out the cost of operations in this algorithm. 

In the traditional Levenshtein Alg., the cost of inserting/replacing/deletion is all the same.

**But** if we had an incorrect word, "lon", and two options for correct spelling, "lion" and "lan". 

The cost of adding an "i" is less than the cost of replacing "o" with an "a"("i" is closer to "o" on the keyboard, and "a" is on the other side of the keyboard). 

As seen [here](https://github.com/RachaelSMathew/spellChecker/blob/1342ebf17b79052d2e37c9affcc1925738bee0f5/spellCheck.py#L28), I'm calculating the distance between two keys(only focusing on the alphabet keys) on the keyboard.

To do this, I'm turning the alphabet keys into an [x and y coordinate graph](https://drive.google.com/file/d/1Ia5p5dsX6LNtoloYZYcVz3avklBGLX_h/view?usp=sharing). 

For example, the distance between "f"(0.9, 1) and "z"(0, 2)  is: `((2-1)^2+(0-0.9)^2)^.5`


