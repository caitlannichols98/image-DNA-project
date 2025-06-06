import sqlite3
import numpy as np
from PIL import Image
import os

# config
GRID_SIZE = 4  # 4x4 = 16 pieces
RESIZED_DIM = 128  # final image is 128x128

# initialize database
def init_db():
    conn = sqlite3.connect("imageDNA.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS image_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            block_row INTEGER,
            block_col INTEGER,
            data BLOB
        )
    ''')
    conn.commit()
    conn.close()

# process image
def process_image(filepath):
    img = Image.open(filepath).convert("L")  # grayscale
    # i will be keeping this here in case, until I am done with the project. might need old constants.
    # img = img.resize((RESIZED_DIM, RESIZED_DIM), Image.ANTIALIAS)
    img = img.resize((RESIZED_DIM, RESIZED_DIM), Image.Resampling.LANCZOS)
    return np.array(img)


# split into grid blocks
def split_into_blocks(image_array):
    h, w = image_array.shape
    block_h = h // GRID_SIZE
    block_w = w // GRID_SIZE

    blocks = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            block = image_array[i*block_h:(i+1)*block_h, j*block_w:(j+1)*block_w]
            blocks.append((i, j, block))
    return blocks

# store blocks into DB
def save_blocks_to_db(image_name, blocks):
    conn = sqlite3.connect("imageDNA.db")
    c = conn.cursor()

    for row, col, block in blocks:
        # convert to bytes for storage
        data_bytes = block.tobytes()
        c.execute('''
            INSERT INTO image_blocks (image_name, block_row, block_col, data)
            VALUES (?, ?, ?, ?)
        ''', (image_name, row, col, data_bytes))

    conn.commit()
    conn.close()

# main pipeline
def process_and_store(filepath):
    image_name = os.path.basename(filepath)
    image_array = process_image(filepath)
    blocks = split_into_blocks(image_array)
    save_blocks_to_db(image_name, blocks)
    print(f"Processed and stored: {image_name}")


#Saving this for possible use incase me removing this breaks the whole program
#if __name__ == "__main__":
 #   init_db()
    # example image path
   # test_image_path = "sample_image.jpg"
  #  process_and_store(test_image_path)
