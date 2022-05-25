"""Shuffles the serial numbers of NFTs in a provably random way.

Example usage:
python3 allocate_nfts.py --num_nfts_minted=10000 --random_seed=cacf1455c21 \
    --output_directory=/tmp/allocations \
    --base_image_path=ipfs://QmaBaBoro352YJH1qZW6c7N1d3q6RFVFXjsGQtmRKMhF5N

The random seed should be an ascii-encoded string without any unicode characters.
If the seed has upper-case characters, they will be converted to lower-case
characters.

Images will be assumed to be located at base_image_path/1.jpg and so on without
leading zeros. 1.jpg should correspond to the legendary artwork. 2-21 should
correspond to the epic artwork. 22-521 should correspond to rare artwork. The rest
should be common.
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
flags.DEFINE_string("base_image_path", None,
                    "The base path to images. Images will be assumed to be located at "
                    "base_image_path/1.jpg and so on without leading zeros. 1.jpg should "
                    "correspond to the legendary artwork. 2-21 should correspond to the "
                    "epic artwork. 22-521 should correspond to rare artwork. The rest "
                    "should be common.",  required=True)
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


def write_metadata(serial_number: int, artwork_id: int, rarity: str, output_directory: str):
    """Writes metadata corresponding to the final version of the NFTs."""
    output_path = os.path.join(output_directory, f'{serial_number}')
    metadata = {"image": os.path.join(
        FLAGS.base_image_path, f'{artwork_id}.jpg'),
        "attributes": [{
            "trait_type": "Rarity",
            "value": rarity
        }]}
    with open(output_path, "w", encoding="UTF-8") as fp:
        json.dump(metadata, fp)


def get_rarity(art_id: int) -> str:
    """Returns the rarity of an artwork as a function of its index."""
    if art_id <= 0:
        raise LookupError(f"Index {int} is not supported.")
    elif art_id <= 1:
        return "Legendary"
    elif art_id <= 21:
        return "Epic"
    elif art_id <= 521:
        return "Rare"
    else:
        return "Common"


def main(argv):
    """Randomly allocate NFT serial numbers artwork and rarity."""
    del argv

    if not is_ascii(FLAGS.random_seed):
        raise ValueError("The random seed should be an ascii string.")

    random_seed = FLAGS.random_seed.lower()

    if not os.path.exists(FLAGS.output_directory):
        os.makedirs(FLAGS.output_directory)

    shuffled_nft_serial_numbers = shuffle_ids(
        FLAGS.num_nfts_minted, random_seed)

    # Iterate through the shuffled serial numbers and assign each a rarity and artwork.
    for index, nft_serial_number in enumerate(shuffled_nft_serial_numbers):
        # Artwork is 1-indexed, so we need to add one.
        art_id = index + 1
        rarity = get_rarity(art_id)
        write_metadata(
            nft_serial_number, art_id, rarity, FLAGS.output_directory)    


if __name__ == '__main__':
    app.run(main)
