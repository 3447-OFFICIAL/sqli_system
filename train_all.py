from model.train_ml import train_and_save_ml_models
from model.train_dl import train_and_save_dl_model

if __name__ == "__main__":
    print("Starting ML Models Training...")
    train_and_save_ml_models()
    print("\nStarting DL Model Training...")
    train_and_save_dl_model()
    print("\nAll models trained successfully!")
