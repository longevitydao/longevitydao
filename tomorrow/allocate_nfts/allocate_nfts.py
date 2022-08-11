"""Shuffles the serial numbers of NFTs in a provably random way.

Example usage:
python3 allocate_nfts.py --num_nfts_minted=10000 --random_seed=cacf1455c21 \
    --output_directory=/tmp/allocations \
    --input_metadata_folder=/path/to/input_metadata

The random seed should be an ascii-encoded string without any unicode characters.
If the seed has upper-case characters, they will be converted to lower-case
characters.

Input metadata will be assumed to be located at input_metadata_folder/0 and so on without
leading zeros. 0 should correspond to the legendary artwork. 1-20 should correspond to 
the epic artwork. 21-520 should correspond to rare artwork. The rest should be common.
"""
import hashlib
import json
import math
import os

from typing import List

from absl import flags
from absl import app


flags.DEFINE_integer("num_nfts_minted", None,
                     "The number of NFT minted.", required=True)
flags.DEFINE_string("input_metadata_folder", "", "Input metadata related to the artwork "
                    "above. The metadata should have no extension and 0 shold correspond to "
                    "legendary. 1-20 should correspond to the epics, 21-520 should correspond "
                    "to the rares and the rest should be common.")
flags.DEFINE_string("random_seed", None,
                    "A random seed used to randomly allocate the NFT serial numbers .",  required=True)
flags.DEFINE_string("output_directory", None,
                    "What directory to write metadata to.", required=True)
FLAGS = flags.FLAGS


def is_ascii(input_string: str):
    """Returns whether s contains only ascii characters."""
    return all(ord(c) < 128 for c in input_string)


def shuffle_ids(num_nfts: int, random_seed: str) -> List[int]:
    """Shuffles the NFTs serial numbers in a deterministic way based on random_seed."""
    hashes = []
    nft_serials = range(1, num_nfts + 1)
    num_bytes_needed = int(math.ceil(math.log2(num_nfts)) // 8 + 2)
    for i in nft_serials:
        concatenated = b"".join(
            [random_seed.encode('utf-8'), i.to_bytes(num_bytes_needed, 'little')])
        hashes.append(hashlib.sha256(concatenated).hexdigest())
    return sorted(nft_serials, key=lambda k: hashes[k - 1])


def strip_leading_zeros(image_path: str):
    """Removes leading zeros from the basename of image_path."""
    dirname, basename = os.path.split(image_path)
    return os.path.join(dirname, basename.lstrip("0"))


def set_name(serial_number:int, rarity: str):
    """Modifies the name of the cryonaut."""
    if rarity == "COMMON":
        return f"Cryonaut #{serial_number}"
    return f"{rarity.title()} Cryonaut #{serial_number}"


def write_metadata(serial_number: int, artwork_id: int, rarity: str, output_directory: str):
    """Writes metadata corresponding to the final version of the NFTs."""
    input_metadata_path = os.path.join(FLAGS.input_metadata_folder, f'{artwork_id}')
    output_path = os.path.join(output_directory, f'{serial_number}')

    if (os.path.exists(input_metadata_path)):
        with open(input_metadata_path, "rt", encoding="UTF-8") as fp:
            metadata = json.loads(fp.read())
    else:
        metadata = {"attributes": []}
    
    metadata["attributes"].append({
            "trait_type": "Rarity",
            "value": rarity
        })
    if "image" in metadata:
        metadata["image"] = strip_leading_zeros(metadata["image"])
    metadata["name"] = set_name(serial_number=serial_number, rarity=rarity)
    with open(output_path, "w", encoding="UTF-8") as fp:
        json.dump(metadata, fp)    


def get_rarity(art_id: int) -> str:
    """Returns the rarity of an artwork as a function of its index."""
    if art_id < 0:
        raise LookupError(f"Index {int} is not supported.")
    elif art_id <= 0:
        return "LEGENDARY"
    elif art_id <= 20:
        return "EPIC"
    elif art_id <= 520:
        return "RARE"
    else:
        return "COMMON"


def main(argv):
    """Randomly allocate NFT serial numbers artwork and rarity."""
    del argv

    if not is_ascii(FLAGS.random_seed):
        raise ValueError("The random seed should be an ascii string.")

    random_seed = FLAGS.random_seed.lower()
    print(os.path.os.listdir(FLAGS.output_directory))
    if not os.path.exists(FLAGS.output_directory):
        os.makedirs(FLAGS.output_directory)

    shuffled_nft_serial_numbers = shuffle_ids(
        FLAGS.num_nfts_minted, random_seed)

    # Iterate through the shuffled serial numbers and assign each a rarity and artwork.
    for metadata_id, nft_serial_number in enumerate(shuffled_nft_serial_numbers):                
        rarity = get_rarity(metadata_id)
        write_metadata(
            nft_serial_number, metadata_id, rarity, FLAGS.output_directory)    

if __name__ == '__main__':
    app.run(main)
