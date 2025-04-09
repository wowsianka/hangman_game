import socket
import time
from collections import Counter, defaultdict
import re

KONOPEK = False
DICT_PATH = './resources/slowa.txt'

SERVER_IP = "136.243.156.120" #Konopek#
KOKOPEK = True
PORT = 12186
PASSWORD = "albumhaslo123"

# SERVER_IP = "31.172.70.25" #Heorhi#
# PORT = 130
# PASSWORD = "J4dl93Bn"

# SERVER_IP = '146.59.45.35' #Nedza#
# PORT = 65432
# PASSWORD = "albumhaslo123"

# SERVER_IP = "136.243.156.120" #Dyrcz#
# PORT = 50804
# PASSWORD="kVlTXUYcpL"

# SERVER_IP = "209.182.238.21" #Jurczyk#
# PORT = 4444
# PASSWORD = "fCR63Oy@.}xgs!vq"


LOGIN = "307034"
# LOGIN = "p1"

DATA_SIZE = 1024

MAX_GUESS = 10


def decode_response(response):
    x = response.decode().replace('\n', '\0').replace('\0', '')
    return x

word_unique_letters = {}
length_to_words = defaultdict(list)

with open(DICT_PATH) as f:
    for line in f:
        word = line.strip()
        letters = set(word)
        word_unique_letters[word] = letters
        length_to_words[len(word)].append(word)

class Guesser:
    alphabets = {
        '1': {
            '1': '[weęruioóaąsśzżźxcćvnńm]',
            '2': '[pyjgq]',
            '3': '[tlłbdhk]',
            '4': '[f]'
        },
        '2': {
            '1': '[weruoaszxcvnm]',
            '2': '[pyjgqąę]',
            '3': '[tlbdhkłóśńćżźi]',
            '4': '[f]'
        }
    }

    def __init__(self):
        self.guessed = set()
        self.last_guess = None

    def set_alphabet(self, alphabet):
        self.mapper = self.alphabets[alphabet]
        
    def set_pattern(self, pattern):
        pattern = pattern.strip()
        self.letters = [self.mapper[num] for num in pattern]
        self.words = self.load_words(len(pattern))
            
    def load_words(self, length):
        regex = self.get_regex()
        # with open(DICT_PATH) as f:
        #     return [word for line in f if regex.fullmatch(word := line.strip())]
        return [word for word in length_to_words[length] if regex.fullmatch(word)]

    def get_regex(self):
        return re.compile(r"".join(self.letters))

    def was_correct(self, new_pattern):
        new_pattern = new_pattern.strip()
        for i, num in enumerate(new_pattern):
            if num == '1':
                self.letters[i] = self.last_guess

        regex = self.get_regex()
        self.words = [word for word in self.words if regex.fullmatch(word)]

    def was_incorrect(self):
        if self.guessed_letter():
            regex = re.compile(f"\w*{self.last_guess}\w*")
            self.words = [word for word in self.words if not regex.match(word)]
        else:
            self.words = [word for word in self.words if word != self.last_guess]

    def most_common_letter(self):
        count = Counter()
        for word in self.words:
            # for letter in word:
            for letter in word_unique_letters[word]:
                count[letter] += 1
        return count.most_common()

    def next_guess(self):
        print("CANDIDATE WORDS:", len(self.words))

        if (0 < len(self.words) <= 2):
            self.last_guess = self.words[0]
            return ('=\n' + self.words[0] + '\n').encode()

        # if len(self.words) == 1:
        #     self.last_guess = self.words[0]
        #     return ('=\n' + self.words[0] + '\n').encode()

        most_common = self.most_common_letter()
        guess = None

        for letter, count in most_common:
            if letter not in self.guessed and count != len(self.words):
                guess = letter
                break

        if guess:
            self.guessed.add(guess)
            self.last_guess = guess
            return ('+\n' + guess + '\n').encode()
        
        print('AJAJAJJAJA')
        raise Exception('Failed to get new guess')

    def repeat_guess(self):
        if self.guessed_letter():
            return ('+\n' + self.last_guess + '\n').encode()
        return ('=\n' + self.last_guess + '\n').encode()

    def guessed_letter(self):
        return len(self.last_guess) == 1

class Connection:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.word_guess = Guesser()
        self.guessed = ""

    def log_in(self):
        self.socket.connect((SERVER_IP, PORT))

        if KOKOPEK:
            self.socket.send(f'{LOGIN}\n'.encode())
            self.socket.send(f'{PASSWORD}\n'.encode())
        else: 
            self.socket.sendall(f'{LOGIN}\n{PASSWORD}\n'.encode())

    def check_log_in(self):
        while True:
            data = self.socket.recv(1024)
            data = decode_response(data)
            if data:
                self.get_alphabet(data)
                break

    def get_alphabet(self, data):
        print("ALPHABET:", data)
        if data == "-":
            self.socket.close()
        elif data == "+1":
            self.word_guess.set_alphabet("1")
        elif data == "+2":
            self.word_guess.set_alphabet("2")
        else:
            self.end()
            raise Exception("Wrong login message")

    def get_pattern(self):
        while True:
            pattern = self.socket.recv(DATA_SIZE)
            pattern = decode_response(pattern)
            if pattern:
                print("PATTERN", pattern)
                self.read_pattern(pattern)
                break

    def read_pattern(self, pattern):
        if pattern.isnumeric():
            start = time.time()
            self.word_guess.set_pattern(pattern)
            self.send_guess()
            self.guessed = "l"
            print("TIME",time.time() - start)

    def send_guess(self, guess=None):
        if not guess:
            guess = self.word_guess.next_guess()
        print('GUESS:', guess.decode())
        self.socket.send(guess)

    def quess(self):
        while True:
            response = self.socket.recv(DATA_SIZE)
            response = decode_response(response)
            if self.read_response(response):
                break

    def read_response(self, response):
        print("RESPONSE:", response)
        if '=' in response:
            if response == '=':
                if self.word_guess.guessed_letter():
                    self.wait_response_pattern()
                    self.send_guess()
                    return False
                else:
                    return self.get_score()
            elif '?' in response:
                return self.end()
            elif response[1:].isnumeric():
                # correctt guess
                self.word_guess.was_correct(response[1:])
                self.send_guess()
            elif response[1:-1].isnumeric():
                return self.end()
        elif '!' in response:
            if response == '!':
                # guess was incorrect
                self.word_guess.was_incorrect()
                self.send_guess()
                return False
            return self.end()
        elif response == '#':
            self.send_guess(self.word_guess.last_guess)
            return False
        elif len(response) == len(self.word_guess.letters):
            return self.get_score()
        elif "?" in response:
            return self.end()
        elif response == '':
            return False
        else:
            return True
       
    def wait_response_pattern(self):
        while True:
            pattern = self.socket.recv(DATA_SIZE)
            if pattern:
                pattern = decode_response(pattern)
                print("PATTERN:", pattern)
                if not pattern.isnumeric():
                    self.end()
                self.word_guess.was_correct(pattern)
                break

    def get_score(self):
        while True:
            points = self.socket.recv(DATA_SIZE)
            points = decode_response(points)
            if points:
                if "?" not in points:
                    print("SCORE: " + points)
                    while True:
                        end = self.socket.recv(DATA_SIZE)
                        end = decode_response(end)
                        print(end)
                        break

                print("POINTS:", points)
                break

        self.socket.close()
        return True

    def end(self):
        print("Ending the game.")
        self.socket.close()
        return True

    def run(self):
        self.log_in()
        self.check_log_in()
        self.get_pattern()
        self.quess()
        # self.disconnect()


if __name__ == '__main__':
    for i in range(2):
        c = Connection()
        c.run()
        print("-------------------------------------")
