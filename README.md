# 🧠 Hangman Strategy Client

## ✨ Highlight
This project is a strategic implementation of a Hangman game client. It was developed as part of a unit project where the goal was to design an intelligent strategy to guess hidden words as efficiently as possible—faster than competing clients.


## 📌 Project Overview

In a client-server Hangman setup, multiple clients attempt to guess words served by a host. The challenge was to:

- **Minimize the number of guesses**
- **Maximize correct letter discovery**
- **Beat other clients using a smarter algorithm**

To achieve this, we implemented and tested various strategies for word guessing. The core of the project lies in how effectively the client can predict the next best letter to guess, based on previously guessed letters and word patterns.

## 🧠 Strategy

The strategy was encoded in Python scripts and revolves around:

- **Probability-based letter selection**
- **Filtering word lists** using known patterns
- **Adapting guesses dynamically** based on feedback from the server

The idea was to build an adaptive guesser that becomes faster and smarter over time.


## ⚙️ How to Run

1. Ensure all dependencies are installed (Python 3.8+ recommended).
2. Launch the client with:

```bash
python main.py
```

## Results
Our client showed a strong performance compared to others in the unit. It consistently guessed words with fewer attempts, demonstrating the effectiveness of our strategy.

## 💡 Future Improvements
- Integrate a learning model to adapt strategy over time
- Add a GUI or CLI dashboard to track game stats
- Expand the word list and preprocessing for better predictions """

