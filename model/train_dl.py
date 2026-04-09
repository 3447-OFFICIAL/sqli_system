import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
from .dataset import load_data, get_train_test_split

MAX_WORDS = 10000
MAX_LEN = 200

def train_and_save_dl_model():
    print("Loading data for DL model...")
    df = load_data()
    X_train_text, X_test_text, y_train, y_test = get_train_test_split(df)
    
    print("Tokenizing text...")
    tokenizer = Tokenizer(num_words=MAX_WORDS, char_level=True) # Char level is better for SQLi
    tokenizer.fit_on_texts(X_train_text)
    
    X_train_seq = tokenizer.texts_to_sequences(X_train_text)
    X_test_seq = tokenizer.texts_to_sequences(X_test_text)
    
    X_train_pad = pad_sequences(X_train_seq, maxlen=MAX_LEN)
    X_test_pad = pad_sequences(X_test_seq, maxlen=MAX_LEN)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(current_dir, "../saved_models")
    os.makedirs(model_dir, exist_ok=True)
    
    print("Saving tokenizer...")
    joblib.dump(tokenizer, os.path.join(model_dir, 'dl_tokenizer.joblib'))
    
    print("Building LSTM model...")
    model = Sequential([
        Embedding(input_dim=MAX_WORDS, output_dim=32, input_length=MAX_LEN),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    print("Training STM model...")
    history = model.fit(
        X_train_pad, y_train, 
        epochs=5, 
        batch_size=64, 
        validation_data=(X_test_pad, y_test),
        verbose=1
    )
    
    loss, accuracy = model.evaluate(X_test_pad, y_test, verbose=0)
    print(f"LSTM trained, Accuracy: {accuracy:.4f}")
    
    model.save(os.path.join(model_dir, 'lstm_model.keras'))
    return accuracy

if __name__ == "__main__":
    train_and_save_dl_model()
