import socket
from collections import Counter, defaultdict
import re

HOST = '146.59.45.35'
PORT = 65432
SIZE_OF_DATA = 1024

LETTERS_1LINE = 'weęruioóaąsśzżźxcćvnńm'
LETTERS_2LINE = 'pyjgq'
LETTERS_3LINE = 'tlłbdhk'
LETTERS_4LINE = 'f'

import time

def timeit(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print(func.__name__, (t2 - t1), "s")
        return res
    return wrapper

def main():
  """
  1. Connect to server
  2. Authenticate with login and password
  3. Receive "+{alphabet number}" and continue, or "-" and retry login
  4. Receive length of the word
  5. Guess
  6. If someone guesses the word you receive lines:
    - Word
    - Score
    - ?

  Requests:
  ={word}
  +{letter}

  Responses:
  =           correct guess (word or letter)
  !           incorrect guess (word or letter)
  #           player ignored
  ?           end of game (connection closing)
  """

  """
  - get only words of correct length
  - get only words that match the pattern

  - get most common letter
  - recompile new list of words based on the answer

  - does it need to be quick?

  every word that matches:
  - count letters
  - add it to a dictionary of letter

  """
  DICT_PATH = './resources/slowa.txt'

  @timeit
  def count_file():
    with open(DICT_PATH) as f:
      return Counter(f.read())

  count = count_file()
  print(count)

  def construct_regex(pattern):
    mapper = {
      '1': '[weęruioóaąsśzżźxcćvnńm]',
      '2': '[pyjgq]',
      '3': '[tlłbdhk]',
      '4': '[f]'
    }
    return re.compile(r"".join([mapper[num] for num in pattern.strip()]))

  @timeit
  def get_words(pattern):
    with open(DICT_PATH) as f:
      return [ word for line in f if pattern.fullmatch(word := line.strip())]

  words = get_words(construct_regex("313112111"))
  # @timeit
  # def get_words(length):
  #   with open(DICT_PATH) as f:
  #     return [ line.strip() for line in f]

  # words = get_words(3)
  print(words)

  @timeit
  def get_most_common(words):
    count = Counter()
    for word in words:
      for letter in word:
        count[letter] += 1
    return count.most_common()

  print(get_most_common(words))




  # regex = construct_regex("313")
  # print(regex)
  # filtered = [word for word in words if regex.fullmatch(word)]

class Words:
  def __init__(self, pattern) -> None:
      self.indices = []

  def add(self, word):
    pass

  def match(self, index, letter):
    pass

  def remove(self, letter):
    pass

  def most_common_letter(self):
    pass

if __name__ == '__main__':
  main()
