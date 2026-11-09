import kagglehub # type: ignore

path = kagglehub.dataset_download("shashwatwork/dataco-smart-supply-chain-for-big-data-analysis", output_dir='./data/raw')

print("Dataset downloaded to:", path)