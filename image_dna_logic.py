import imagehash
from PIL import Image
import sqlite3
import os
import numpy as np

# hash single blocks using average hash
def hash_block(block):
    img = Image.fromarray(block)
    return str(imagehash.average_hash(img))

# config
GRID_SIZE = 4  # 4x4 = 16 pieces
RESIZED_DIM = 128  # final image is 128x128

def init_db():
    if os.path.exists("imageDNA.db"):
        os.remove("imageDNA.db")  # remove old DB
    conn = sqlite3.connect("imageDNA.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE image_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            block_row INTEGER,
            block_col INTEGER,
            data TEXT
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

def save_blocks_to_db(image_name, blocks):
    conn = sqlite3.connect("imageDNA.db")
    c = conn.cursor()

    for row, col, block in blocks:
        block_hash = hash_block(block)
        c.execute('''
            INSERT INTO image_blocks (image_name, block_row, block_col, data)
            VALUES (?, ?, ?, ?)
        ''', (image_name, row, col, block_hash))

    conn.commit()
    conn.close()

# main pipeline
def process_and_store(filepath):
    image_name = os.path.basename(filepath)
    image_array = process_image(filepath)
    blocks = split_into_blocks(image_array)
    save_blocks_to_db(image_name, blocks)
    print(f"Processed and stored: {image_name}")

def hamming_distance(hash1, hash2):
    return bin(int(str(hash1), 16) ^ int(str(hash2), 16)).count('1')

def compare_image(filepath, distance_threshold=5, match_ratio=0.75):
    image_array = process_image(filepath)
    new_blocks = split_into_blocks(image_array)
    hashed_new = [(row, col, hash_block(block)) for row, col, block in new_blocks]

    conn = sqlite3.connect("imageDNA.db")
    c = conn.cursor()
    c.execute("SELECT block_row, block_col, data FROM image_blocks")
    stored_blocks = c.fetchall()
    conn.close()

    similar_blocks = 0
    total_blocks = len(hashed_new)

    for row, col, new_hash in hashed_new:
        for db_row, db_col, db_hash in stored_blocks:
            if row == db_row and col == db_col:
                if hamming_distance(new_hash, db_hash) <= distance_threshold:
                    similar_blocks += 1
                    break  # match found, move to next

    similarity_ratio = similar_blocks / total_blocks
    print(f"Match ratio: {similar_blocks}/{total_blocks} blocks matched")

    if similarity_ratio >= match_ratio:
        print("Potential match detected.")
    else:
        print("No significant match.")

