# Tomorrow Biostasis NFT Allocation

Tomorrow Biostasis NFTs will be allocated by the docker image `longevitydao/allocate-tomorrow` using the following command:

```
mkdir /tmp/results &&docker run --mount type=bind,source=/tmp/results,target=/usr/app/src/results/ longevitydao/allocate-tomorrow --num_nfts_minted={NUMBER_OF_NFTS_MINTED} --base_image_path={PATH_TO_IPFS_IMAGES} --random_seed={RANDOM_SEED} --output_directory=results
```

The random seed is as specified in our [gitbook](https://longevity-dao.gitbook.io/tomorrow-biostasis-nfts-listed-by-longevitydao/). The script will be run on an AWS instance of Ubuntu 22.04.

The docker. image is public and can be retrieved with:

```
docker pull longevitydao/allocate-tomorrow
```
