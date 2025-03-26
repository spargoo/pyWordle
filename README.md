# 🐍 pyWordle  


<img src="https://github.com/user-attachments/assets/40255187-8d00-41b7-856a-f5e591463917" width="450" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

## 👾 *A Spanish Wordle clone built with Python & Tkinter*  

🎮 *Guess the Hidden 5-Letter Spanish Word!*
---


## ✨ Features  

### 🎲 Game Modes  
| Mode        | Description                          | Difficulty |
|-------------|--------------------------------------|------------|
| **Classic** | 6 attempts to guess the word         | 🌶️🌶️     |
| **Timed**   | 30-120 seconds to win!               | 🌶️🌶️🌶️🌶️ |

### 🎨 Color Feedback System  
| Color  | Meaning                          | Indication |
|--------|----------------------------------|-------|
| Green  | Correct letter in right position | 🟩    |
| Yellow | Correct letter, wrong position   | 🟨    |
| Gray   | Letter not in the word           | ⬛    |

---

## 🕹️ How to Play  
1. Select a game mode  
2. Type a 5-letter Spanish word  
3. Press `Enter` to submit  
4. Use the color hints for your next guess  
5. Win by guessing the word!

## 🛠️ Requirements  
- Python 3.x  
- Tkinter (included in standard library)  

---

## 🥱 TL;DR

Using the words.py script, I extracted all the 5-letter words from diccionario.txt (u can find it here: https://github.com/JorgeDuenasLerin/diccionario-espanol-txt) and saved them into a JSON file. 

However, since many of these words were uncommon, I created a separate file with some more familiar 5-letter words for the game’s guessable options (though you can still input any word from the full dictionary).

;)
