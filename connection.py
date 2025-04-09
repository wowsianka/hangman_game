import socket
import time
from collections import Counter
import re
import word_guess as wg

# SERVER_IP = "209.182.238.21" #Jurczyk#
# PORT = 4444
# PASSWORD = "Mdj/Lu:go}H:gvfv"
DICT_PATH = './resources/slowa.txt'

SERVER_IP = "136.243.156.120" #Konopek#
PORT = 12186
# PASSWORD = "albumhaslo123"
PASSWORD = "1"

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


LOGIN = "1"
# LOGIN = "307034"
# LOGIN = "p1"

DATA_SIZE = 1024

MAX_GUESS = 10


def decode_response(response):
    x = response.decode().replace('\n', '\0').replace('\0', '')
    return x


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
        self.letters = [self.mapper[num] for num in pattern.strip()]
        self.words = self.load_words()
            
    def load_words(self):
        regex = self.get_regex()
        with open(DICT_PATH) as f:
            return [word for line in f if regex.fullmatch(word := line.strip())]

    def get_regex(self):
        return re.compile(r"".join(self.letters))

    def was_correct(self, new_pattern):
        for i, num in enumerate(new_pattern):
            if num == '1':
                self.letters[i] = self.last_guess

        regex = self.get_regex()
        self.words = [word for word in self.words if regex.fullmatch(word)]

    def was_incorrect(self):
        regex = re.compile(f"\w*{self.last_guess}\w*")
        self.words = [word for word in self.words if not regex.match(word)]

    def most_common_letter(self):
        count = Counter()
        for word in self.words:
            for letter in word:
                count[letter] += 1
        return count.most_common()

    def next_guess(self):
        if len(self.words) == 1:
            return ('=\n' + self.words[0] + '\n').encode()

        most_common = self.most_common_letter()
        # print(most_common)
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


class Connection:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.word_guess = Guesser()
        self.guessed = ""

    def connect(self):
        self.socket.connect((SERVER_IP, PORT))

        # if Konopek:
        self.socket.send(f'{LOGIN}\n'.encode())
        self.socket.send(f'{PASSWORD}\n'.encode())

        # else 
        # self.socket.sendall(f'{LOGIN}\n{PASSWORD}\n'.encode())


    def wait_authorisation(self):
        while True:
            data = self.socket.recv(1024)
            data = decode_response(data)
            if data:
                self.interpret_authorisation(data)
                break

    def interpret_authorisation(self, data):
        print(data)
        if data == "-":
            self.socket.close()
        elif data == "+1":
            self.word_guess.set_alphabet("1")
        elif data == "+2":
            self.word_guess.set_alphabet("2")
        else:
            self.end_unexpectedly()
            raise Exception("Wrong login message")

    def wait_pattern(self):
        while True:
            pattern = self.socket.recv(DATA_SIZE)
            pattern = decode_response(pattern)
            if pattern:
                print("PATTERN", pattern)
                self.interpret_pattern(pattern)
                break

    def interpret_pattern(self, pattern):
        if pattern.isnumeric():
            start = time.time()
            self.word_guess.set_pattern(pattern)
            self.send_guess()
            self.guessed = "l"
            print(time.time() - start)

    def send_guess(self, guess=None):
        if not guess:
            guess = self.word_guess.next_guess()
        print('GUESS:', guess.decode())
        self.socket.send(guess)

    def play(self):
        while True:
            response = self.socket.recv(DATA_SIZE)
            response = decode_response(response)
            if self.interpret_response(response):
                break

    def interpret_response(self, response):
        print(response)
        if '=' in response:
            if response == '=':
                if '?' in response:
                    return self.end_unexpectedly()

                self.wait_response_pattern()
                self.send_guess()
                return False
            elif response[1:].isnumeric():
                # corrent guess
                self.word_guess.was_correct(response[1:])
                self.send_guess()
            elif response[1:-1].isnumeric():
                return self.end_unexpectedly()
        elif '!' in response:
            if response == '!':
                # guess was incorrect
                self.word_guess.was_incorrect()
                self.send_guess()
            return self.end_unexpectedly()
        elif response == '#':
            # TODO: what the flipp am i supposed to do here
            self.send_guess(self.word_guess.last_guess)
            # self.try_again()
            return False
        elif len(response) == len(self.word_guess.letters):
            # TODO: what's this?
            print(response)
            return self.end_game()
        elif "?" in response:
            return self.end_unexpectedly()
        elif response == '':
            return False
        else:
            raise Exception("Error in response")

    # def try_again(self):
    #     if self.guessed == "l":
    #         letter = self.word_guess.letter_try_again()
    #         self.socket.recv((letter + '\n').encode())
    #     else:
    #         word = self.word_guess.word_try_again()
    #         self.socket.recv((word + '\n').encode())

    def wait_response_pattern(self):
        while True:
            pattern = self.socket.recv(DATA_SIZE)
            if pattern:
                pattern = decode_response(pattern)
                self.word_guess.was_correct(pattern)
                break

    def end_game(self):
        while True:
            points = self.socket.recv(DATA_SIZE)
            points = decode_response(points)
            if points:
                if "?" not in points:
                    print("Points: " + points)
                    while True:
                        end = self.socket.recv(DATA_SIZE)
                        end = decode_response(end)
                        print(end)
                        break

                print(points)
                break

        self.socket.close()
        return True

    def end_unexpectedly(self):
        print("Ending expectedly")
        self.socket.close()
        return True

    def execute(self):
        try:
            self.connect()
            self.wait_authorisation()
            self.wait_pattern()
            self.play()
        except (TimeoutError, OSError) as error:
            self.end_unexpectedly()


if __name__ == '__main__':
    c = Connection()
    c.execute()
