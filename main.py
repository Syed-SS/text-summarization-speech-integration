import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import speech_recognition as sr
from gtts import gTTS
from transformers import pipeline
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from googletrans import Translator
from wordcloud import WordCloud
from collections import Counter
import re

# Download NLTK data files (only need to run once)
nltk.download('vader_lexicon')

# Initialize the summarization model, sentiment analyzer, and translator
summarizer = pipeline("summarization")
sentiment_analyzer = SentimentIntensityAnalyzer()
translator = Translator()

# Function to summarize text
def summarize_text():
    input_text = input_text_area.get("1.0", tk.END)
    if not input_text.strip():
        messagebox.showwarning("Input Error", "Please enter some text to summarize.")
        return
    summary = summarizer(input_text, max_length=50, min_length=25, do_sample=False)
    summarized_text = summary[0]['summary_text']
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert(tk.END, summarized_text)
    visualize_summary(summarized_text)
    analyze_sentiment(summarized_text)
    generate_wordcloud(summarized_text)

# Function to convert text to speech
def text_to_speech():
    summarized_text = output_text_area.get("1.0", tk.END).strip()
    if not summarized_text:
        messagebox.showwarning("Output Error", "No summarized text to convert to speech.")
        return
    lang = language_var.get()
    if lang == "ur":
        tts = gTTS(text=summarized_text, lang='ur')
    else:
        tts = gTTS(text=summarized_text, lang='en')
    tts.save("summary.mp3")
    os.system("start summary.mp3")

# Function to convert speech to text
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Listening", "Please speak now...")
        audio = recognizer.listen(source)
        try:
            spoken_text = recognizer.recognize_google(audio)
            input_text_area.delete("1.0", tk.END)
            input_text_area.insert(tk.END, spoken_text)
        except sr.UnknownValueError:
            messagebox.showerror("Speech Error", "Could not understand audio.")
        except sr.RequestError:
            messagebox.showerror("API Error", "Could not request results from Google Speech Recognition service.")

# Function to visualize the summarized text
def visualize_summary(summary):
    words = re.findall(r'\w+', summary.lower())
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(10)
    labels, sizes = zip(*most_common_words)

    # Bar graph for word frequency distribution
    plt.figure(figsize=(10, 5))
    plt.bar(labels, sizes, color='cyan')
    plt.title('Word Frequency Distribution')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.show()

    # Pie chart for word frequency distribution
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Word Frequency Distribution')
    plt.show()

# Function to analyze sentiment
def analyze_sentiment(text):
    sentiment = sentiment_analyzer.polarity_scores(text)
    sentiment_text = f"Sentiment Analysis:\nPositive: {sentiment['pos']}\nNegative: {sentiment['neg']}\nNeutral: {sentiment['neu']}\nCompound: {sentiment['compound']}"
    sentiment_label.config(text=sentiment_text)

    # Sentiment analysis graph
    labels = ['Positive', 'Negative', 'Neutral', 'Compound']
    sizes = [sentiment['pos'], sentiment['neg'], sentiment['neu'], sentiment['compound']]
    colors = ['#66b3ff', '#ff9999', '#99ff99', '#ffcc99']

    plt.figure(figsize=(10, 5))
    plt.bar(labels, sizes, color=colors)
    plt.title('Sentiment Analysis')
    plt.xlabel('Sentiment')
    plt.ylabel('Scores')
    plt.show()

# Function to save summarized text as PDF
def save_as_pdf():
    summarized_text = output_text_area.get("1.0", tk.END).strip()
    if not summarized_text:
        messagebox.showwarning("Output Error", "No summarized text to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "Summarized Text:")
        c.drawString(100, 730, summarized_text)
        c.save()
        messagebox.showinfo("Success", "PDF saved successfully!")

# Function to translate text
def translate_text():
    input_text = input_text_area.get("1.0", tk.END)
    if not input_text.strip():
        messagebox.showwarning("Input Error", "Please enter some text to translate.")
        return
    dest_lang = language_var.get()
    translated = translator.translate(input_text, dest=dest_lang)
    translated_text = translated.text
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert(tk.END, translated_text)

# Function to generate a word cloud
def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# Create the main window
root = tk.Tk()
root.title("Text Processing Application")
root.configure(bg='black')
root.geometry("800x700")

# Create welcome label
welcome_label = tk.Label(root, text="WELCOME TO SCRIBE SUMMARIZER WORLD", font=("Arial", 16, "bold"), fg="white", bg="black")
welcome_label.pack(padx=10, pady=10)

# Create input text area
input_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10, bg='black', fg='white', insertbackground='white', font=("Arial", 12, "bold"))
input_text_area.pack(padx=10, pady=10)

# Create output text area
output_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10, bg='black', fg='white', insertbackground='white', font=("Arial", 12, "bold"))
output_text_area.pack(padx=10, pady=10)

# Create sentiment label
sentiment_label = tk.Label(root, text="Sentiment Analysis:", fg="white", bg="black", font=("Arial", 12, "bold"))
sentiment_label.pack(padx=10, pady=10)

# Create a frame for buttons
button_frame = tk.Frame(root, bg='black')
button_frame.pack(padx=10, pady=10)

# Create buttons with different colors and images
summarize_button = tk.Button(button_frame, text="Summarize Text", command=summarize_text, bg='blue', fg='white', width=20, height=2, font=("Arial", 12, "bold"))
summarize_button.grid(row=0, column=0, padx=5, pady=5)

text_to_speech_button = tk.Button(button_frame, text="Text to Speech", command=text_to_speech, bg='green', fg='white', width=20, height=2, font=("Arial", 12, "bold"))
text_to_speech_button.grid(row=0, column=1, padx=5, pady=5)

speech_to_text_button = tk.Button(button_frame, text="Speech to Text", command=speech_to_text, bg='purple', fg='white', width=20, height=2, font=("Arial", 12, "bold"))
speech_to_text_button.grid(row=0, column=2, padx=5, pady=5)

save_as_pdf_button = tk.Button(button_frame, text="Save as PDF", command=save_as_pdf, bg='orange', fg='white', width=20, height=2, font=("Arial", 12, "bold"))
save_as_pdf_button.grid(row=1, column=0, padx=5, pady=5)

translate_button = tk.Button(button_frame, text="Translate Text", command=translate_text, bg='red', fg='white', width=20, height=2, font=("Arial", 12, "bold"))
translate_button.grid(row=1, column=1, padx=5, pady=5)

visualize_button = tk.Button(button_frame, text="Visualize Summary", command=lambda: visualize_summary(output_text_area.get("1.0", tk.END)), bg='cyan', fg='black', width=20, height=2, font=("Arial", 12, "bold"))
visualize_button.grid(row=1, column=2, padx=5, pady=5)

# Create a dropdown menu for language selection
language_var = tk.StringVar(root)
language_var.set("ur")  # Default value
language_label = tk.Label(button_frame, text="Select Language:", fg="white", bg="black", font=("Arial", 12, "bold"))
language_label.grid(row=2, column=0, padx=5, pady=5)
language_menu = ttk.Combobox(button_frame, textvariable=language_var, values=["ur", "te", "hi", "fr", "it"], state="readonly", font=("Arial", 12, "bold"))
language_menu.grid(row=2, column=1, padx=5, pady=5)

# Run the application
root.mainloop()