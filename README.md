# Smart Supply Chain Analysis

## Overview

This project aims to evaluate shipping performance, identify operational inefficiencies, and investigate how shipping delays relate to sales and profitability.

## Setup

To obtain the data for this project, execute the download-data.py script found in scripts/. The data will get downloaded in data/raw/.

To generate a data-quality profile of the raw data, run `python scripts/profile-data.py`. It writes `reports/data-profile.md`.

## Dataset

- Source: Kaggle
- Geographic coverage: Global
- Time period: 1 January 2015 - 1 February 2018

## Research Questions

- Which areas should management investigate first?
- Which shipping modes require attention?
- Which geographical markets have the biggest operational challenges?
- Are there opportunities to improve profitability?
- What operational changes would you recommend?

## Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook

## Project Structure

```text
smart-supply-chain/
├── data/           # Raw and processed datasets
├── notebooks/      # Data understanding, cleaning and EDA
├── reports/        # Project documentation and analytical report
├── visualizations/ # Exported visualizations
├── scripts/        # Reusable Python modules
├── README.md
├── requirements.txt
└── .gitignore
```
