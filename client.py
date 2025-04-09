import socket
import signal
import mmap
from random import randint
import re
import sys
from time import sleep
from collections import Counter

from connection import LOGIN, PASSWORD


# HOST = "136.243.156.120" #Konopek#
# PORT = 12186
# PASSW = "albumhaslo123"
HOST = "31.172.70.25" #Heorhi#
PORT = 130
PASSW = "J4dl93Bn"

# HOST = '146.59.45.35' #Nedza#
# PORT = 65432
# PASSW = "albumhaslo123"

# HOST = "136.243.156.120" #Dyrcz#
# PORT = 50804
# PASSW="kVlTXUYcpL"

# HOST = "209.182.238.21" #Jurczyk#
# PORT = 4444
# PASSW = "fCR63Oy@.}xgs!vq"


SIZE_OF_DATA = 1024
MAX_TRIES = 3

DICT_PATH = './slowa.txt'
LOG="307034"


class Guesser:
  mapper = {
    '1': '[weęruioóaąsśzżźxcćvnńm]',
    '2': '[pyjgq]',
    '3': '[tlłbdhk]',
    '4': '[f]'
  }
  mapper1 = {
    '1': '[weruoaszxcvnm]',
    '2': '[pyjgqąę]',
    '3': '[tlbdhkłóśńćżźi]',
    '4': '[f]'
  }


  def __init__(self, pattern, alphabet):
    if alphabet == "1":
      self.letters = [self.mapper[num] for num in pattern.strip()]
    else:
      self.letters = [self.mapper1[num] for num in pattern.strip()] 
    self.words = self.load_words()
    self.guessed = set()
    self.last_guess = None


  def load_words(self):
    regex = self.get_regex()
    with open(DICT_PATH) as f:
      return [ word for line in f if regex.fullmatch(word := line.strip())]

  def get_regex(self):
    return re.compile(r"".join(self.letters))

  def was_correct(self, new_pattern):
    for i, num in enumerate(new_pattern):
      if num == '1':
        self.letters[i] = self.last_guess
    
    regex = self.get_regex()
    self.words = [ word for word in self.words if regex.fullmatch(word) ]

  def was_incorrect(self):
    regex = re.compile(f"\w*{self.last_guess}\w*")
    self.words = [ word for word in self.words if not regex.match(word) ]

  def most_common_letter(self):
    count = Counter()
    for word in self.words:
      for letter in word:
        count[letter] += 1
    return count.most_common()

  def next_guess(self):
    if len(self.words) == 1:
      return '=\n' + self.words[0] + '\n'
    
    most_common = self.most_common_letter()
    print(most_common)
    guess = None

    for letter, count in most_common:
      if letter not in self.guessed and count != len(self.words):
        guess = letter
        break
    
    if guess:
      self.guessed.add(guess)
      self.last_guess = guess
      return '+\n' + guess + '\n'

    raise Exception('Failed to get new guess')


class Connection:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_alive = False
        signal.signal(signal.SIGINT, self.signal_handler)
        self.word = None
        self.guessed = ''
        self.word_list = []
        self.word_guess=''

    def connect(self, login, password):
        print('Press CTRL-C to exit.\n')
        try:
            self.client.connect((HOST, PORT))
            self.conn_alive = True
            self.client.sendall(f'{login}\n{password}\n'.encode())

            # self.client.send(f'{login}\n'.encode())
            # self.client.send(f'{password}\n'.encode())
            # self.client.sendall(f'{login}\n{password}\0'.encode())
            data = self.receive()
            if data == '+1':
                self.word_guess="1"
            elif data == "+2":
              self.word_guess="2"
            elif data == '-':
                print('Access denied. Quitting...')
                self.disconnect()
                return 0
            # waiting in the queue
            while True:
                self.client.settimeout(0.2)
                try:
                    data = self.client.recv(SIZE_OF_DATA).decode().replace('\n', '\0').replace('\0', '')
                    if data:
                        print(f'{data}')
                        break
                except socket.timeout:
                    continue
            # the game has started
            while True:
              try:
                    print("---------------------------")
                    if data:
                        data = self.send(data)
                    data = self.receive_and_display()
                    if not self.conn_alive:
                        return 0
                    print(f'Words: {self.guesser.words[:10]}', len(self.guesser.words))
                    print(f'Current word state: {self.guesser.get_regex()}')
              except socket.timeout as e:
                print(e)
                continue
        except socket.error as e:
            print(e)

    def signal_handler(self, sig, frame):
        self.disconnect()
        exit(0)

    def disconnect(self):
        print('\nDisconnecting...')
        self.conn_alive = False

    def receive(self):
        return self.client.recv(SIZE_OF_DATA).decode().replace('\n', '\0').replace('\0', '')

    def receive_and_display(self):
        data = self.client.recv(SIZE_OF_DATA).decode().replace('\0', '\n')[:-1]
        print(f'Received: {data}')
        return data

    def send(self, data_last):
        try:
            data = None
            if data_last[-1] == '?':
                # end of game
                if data_last[0] == '=':
                    score = data_last.replace('\n', '\0').split('\0')[1]
                    print(f'YOUR SCORE IS: {score}')
                self.disconnect()
                return 0
            elif re.match(r'[1-4]+', data_last):
                # beginning pattern
                self.guesser = Guesser(data_last, self.word_guess)
                data = self.guesser.next_guess()
            elif data_last[0] == '#':
                # player was ignored
                data = '+' + self.guesser.last_guess + '\0'
            elif data_last[0] == '=':
                # correct guess
                data_last = data_last.replace('\0', '\n').split('\n')[1]
                if data_last is not None:
                    self.guesser.was_correct(data_last)
                data = self.guesser.next_guess()
            elif data_last[0] == '!':
                self.guesser.was_incorrect()
                data = self.guesser.next_guess()
            if data is not None:
                print(f'Sending data: {data}')
                self.client.sendall(data.encode())
        except socket.error as error:
            print(f'Error while sending data: {error}')


def main():
    c = Connection()
    c.connect(LOG, PASSW)

if __name__ == '__main__':
  main()
