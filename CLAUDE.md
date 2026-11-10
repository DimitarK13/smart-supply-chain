# Smart Supply Chain Analysis

Shared conventions for all analysis projects are in `../CLAUDE.md` (loaded automatically).

## Dataset

- Kaggle: https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis
- Download: `.venv/bin/python scripts/download-data.py` → `data/raw/` (not committed)
- Profile: `reports/data-profile.md`, regenerated with `.venv/bin/python scripts/profile-data.py`

## Data notes

- Main file: `data/raw/DataCoSupplyChainDataset.csv`, 180,519 rows × 53 columns. **One row per order item**
  (`Order Item Id` is unique; there are 65,752 distinct `Order Id`s).
- Encoding is not UTF-8: `pd.read_csv(..., encoding='cp1252')`.
- Dates are stored as text, format `%m/%d/%Y %H:%M`: `order date (DateOrders)` (2015-01-01 → 2018-01-31)
  and `shipping date (DateOrders)`.
- Identical column pairs: `Benefit per order` = `Order Profit Per Order`; `Sales per customer` = `Order Item Total`;
  `Category Id` = `Product Category Id`; `Customer Id` = `Order Customer Id`;
  `Order Item Cardprod Id` = `Product Card Id`; `Order Item Product Price` = `Product Price`.
- No information: `Customer Email` and `Customer Password` (all `XXXXXXXXX`), `Product Description` (empty),
  `Product Status` (always 0).
- Missing values: `Order Zipcode` 86%, `Customer Lname` 8 rows, `Customer Zipcode` 3 rows.
- Several text columns have leading/trailing whitespace (e.g. `Order Region`, `Category Name`, `Product Name`).
- Country and state names are in Spanish (e.g. `Customer Country` = "EE. UU.", `Order Country` = "Estados Unidos").
- `DescriptionDataCoSupplyChain.csv` is the data dictionary. `tokenized_access_logs.csv` is a separate website
  clickstream (Sep 2017 – Jan 2018) with no order or customer key.
