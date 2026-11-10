# Data Profile

_Generated 2026-11-10 13:15 by `scripts/profile-data.py`. Re-run the script to regenerate this file, and don't edit it by hand._

This file lists facts about the raw data and flags things to check. It doesn't interpret them; the decisions belong in the data-preparation notebook.

| File                                                         | Rows    | Columns | Size    | Encoding | Flags |
| ------------------------------------------------------------ | ------- | ------- | ------- | -------- | ----- |
| [DataCoSupplyChainDataset.csv](#datacosupplychaindatasetcsv) | 180,519 | 53      | 95.9 MB | `cp1252` | 34    |
| [tokenized_access_logs.csv](#tokenizedaccesslogscsv)         | 469,977 | 8       | 95.4 MB | `utf-8`  | 2     |

Data dictionary: `data/raw/DescriptionDataCoSupplyChain.csv` (52 entries)

## DataCoSupplyChainDataset.csv

- **Rows × columns:** 180,519 × 53
- **Read with:** `cp1252` ← not UTF-8; pass `encoding=` to `pd.read_csv`
- **Memory in pandas:** 315 MB
- **Fully duplicated rows:** none
- **Columns with missing values:** 4 of 53

### Flags

_Things to check before cleaning. Each one may be fine; that's for you to decide._

**Identical columns** (same values in every row):

- `Benefit per order` = `Order Profit Per Order`
- `Sales per customer` = `Order Item Total`
- `Category Id` = `Product Category Id`
- `Customer Email` = `Customer Password`
- `Customer Id` = `Order Customer Id`
- `Order Item Cardprod Id` = `Product Card Id`
- `Order Item Product Price` = `Product Price`

**1:1 mappings** (each value of one column matches exactly one value of the other, e.g. an ID and its name):

- `Days for shipment (scheduled)` ↔ `Shipping Mode`
- `Department Id` ↔ `Department Name`
- `Order Item Cardprod Id` ↔ `Product Image`
- `Order Item Cardprod Id` ↔ `Product Name`
- `Product Image` ↔ `Product Name`

**Empty columns:**

- `Product Description`: column is entirely empty

**Constant columns:**

- `Customer Email`: single value 'XXXXXXXXX' in every non-missing row
- `Customer Password`: single value 'XXXXXXXXX' in every non-missing row
- `Product Status`: single value '0' in every non-missing row

**Placeholder or masked values:**

- `Customer Email`: placeholder/masked values: 'XXXXXXXXX' ×180,519
- `Customer Password`: placeholder/masked values: 'XXXXXXXXX' ×180,519

**Mostly missing (≥50%):**

- `Order Zipcode`: 86.2% missing

**Dates stored as text:**

- `order date (DateOrders)`: dates stored as text (format `%m/%d/%Y %H:%M`)
- `shipping date (DateOrders)`: dates stored as text (format `%m/%d/%Y %H:%M`)

**Leading/trailing whitespace:**

- `Category Name`: 1,475 values have leading/trailing whitespace
- `Customer Street`: 1,829 values have leading/trailing whitespace
- `Department Name`: 362 values have leading/trailing whitespace
- `Order Region`: 17,925 values have leading/trailing whitespace
- `Product Image`: 886 values have leading/trailing whitespace
- `Product Name`: 1,774 values have leading/trailing whitespace

**Inconsistent spelling/case:**

- `Customer Fname`: 1 value differs only by letter case, e.g. 'TaShya' / 'Tashya'

**Whole numbers stored as float:**

- `Customer Zipcode`: whole numbers stored as float (because of missing values)
- `Order Zipcode`: whole numbers stored as float (because of missing values)

**Many IQR outliers (≥5%):**

- `Benefit per order`: 10.5% of values outside 1.5×IQR
- `Order Item Profit Ratio`: 9.6% of values outside 1.5×IQR
- `Order Profit Per Order`: 10.5% of values outside 1.5×IQR

**Row identifiers:**

- `Order Item Id`: unique in every row (row identifier?)

### Columns

| #   | Column                          | Type               | Missing          | Unique  | Most common values                                                           | Description                                                            |
| --- | ------------------------------- | ------------------ | ---------------- | ------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 1   | `Type`                          | text (str)         | –                | 4       | DEBIT, TRANSFER, PAYMENT                                                     | Type of transaction made                                               |
| 2   | `Days for shipping (real)`      | numeric (int64)    | –                | 7       | 2, 3, 6                                                                      | Actual shipping days of the purchased product                          |
| 3   | `Days for shipment (scheduled)` | numeric (int64)    | –                | 4       | 4, 2, 1                                                                      | Days of scheduled delivery of the purchased product                    |
| 4   | `Benefit per order`             | numeric (float64)  | –                | 21,998  | 0, 143.99, 72                                                                | Earnings per order placed                                              |
| 5   | `Sales per customer`            | numeric (float64)  | –                | 2,927   | 122.84, 109.19, 127.39                                                       | Total sales per customer made per customer                             |
| 6   | `Delivery Status`               | text (str)         | –                | 4       | Late delivery, Advance shipping, Shipping on time                            | Delivery status of orders: Advance shipping , Late delivery , Shippin… |
| 7   | `Late_delivery_risk`            | binary 0/1 (int64) | –                | 2       | 1, 0                                                                         | Categorical variable that indicates if sending is late (1), it is not… |
| 8   | `Category Id`                   | numeric (int64)    | –                | 51      | 17, 18, 24                                                                   | Product category code                                                  |
| 9   | `Category Name`                 | text (str)         | –                | 50      | Cleats, Men's Footwear, Women's Apparel                                      | Description of the product category                                    |
| 10  | `Customer City`                 | text (str)         | –                | 563     | Caguas, Chicago, Los Angeles                                                 | City where the customer made the purchase                              |
| 11  | `Customer Country`              | text (str)         | –                | 2       | EE. UU., Puerto Rico                                                         | Country where the customer made the purchase                           |
| 12  | `Customer Email`                | text (str)         | –                | 1       | XXXXXXXXX                                                                    | Customer's email                                                       |
| 13  | `Customer Fname`                | text (str)         | –                | 782     | Mary, James, Robert                                                          | Customer name                                                          |
| 14  | `Customer Id`                   | numeric (int64)    | –                | 20,652  | 5654, 10591, 5004                                                            | Customer ID                                                            |
| 15  | `Customer Lname`                | text (str)         | 8 (<0.1%)        | 1,109   | Smith, Johnson, Brown                                                        | Customer lastname                                                      |
| 16  | `Customer Password`             | text (str)         | –                | 1       | XXXXXXXXX                                                                    | Masked customer key                                                    |
| 17  | `Customer Segment`              | text (str)         | –                | 3       | Consumer, Corporate, Home Office                                             | Types of Customers: Consumer , Corporate , Home Office                 |
| 18  | `Customer State`                | text (str)         | –                | 46      | PR, CA, NY                                                                   | State to which the store where the purchase is registered belongs      |
| 19  | `Customer Street`               | text (str)         | –                | 7,458   | 9126 Wishing Expressway, 4388 Burning Goose Ridge, 4720 Noble Hills Wynd     | Street to which the store where the purchase is registered belongs     |
| 20  | `Customer Zipcode`              | numeric (float64)  | 3 (<0.1%)        | 995     | 725, 921, 23455                                                              | Customer Zipcode                                                       |
| 21  | `Department Id`                 | numeric (int64)    | –                | 11      | 7, 4, 5                                                                      | Department code of store                                               |
| 22  | `Department Name`               | text (str)         | –                | 11      | Fan Shop, Apparel, Golf                                                      | Department name of store                                               |
| 23  | `Latitude`                      | numeric (float64)  | –                | 11,250  | 18.2276, 39.4959, 18.2276                                                    | Latitude corresponding to location of store                            |
| 24  | `Longitude`                     | numeric (float64)  | –                | 4,487   | -66.3706, -66.3706, -66.3706                                                 | Longitude corresponding to location of store                           |
| 25  | `Market`                        | text (str)         | –                | 5       | LATAM, Europe, Pacific Asia                                                  | Market to where the order is delivered : Africa , Europe , LATAM , Pa… |
| 26  | `Order City`                    | text (str)         | –                | 3,597   | Santo Domingo, New York City, Los Angeles                                    | Destination city of the order                                          |
| 27  | `Order Country`                 | text (str)         | –                | 164     | Estados Unidos, Francia, México                                              | Destination country of the order                                       |
| 28  | `Order Customer Id`             | numeric (int64)    | –                | 20,652  | 5654, 10591, 5004                                                            | Customer order code                                                    |
| 29  | `order date (DateOrders)`       | date (text) (str)  | –                | 65,752  | 10/25/2016 14:39, 3/30/2016 4:37, 11/28/2016 1:18                            | Date on which the order is made                                        |
| 30  | `Order Id`                      | numeric (int64)    | –                | 65,752  | 45461, 31115, 47752                                                          | Order code                                                             |
| 31  | `Order Item Cardprod Id`        | numeric (int64)    | –                | 118     | 365, 403, 502                                                                | Product code generated through the RFID reader                         |
| 32  | `Order Item Discount`           | numeric (float64)  | –                | 1,017   | 0, 6, 12                                                                     | Order item discount value                                              |
| 33  | `Order Item Discount Rate`      | numeric (float64)  | –                | 18      | 0.04, 0.05, 0.06                                                             | Order item discount percentage                                         |
| 34  | `Order Item Id`                 | numeric (int64)    | –                | 180,519 | 180517, 179254, 179253                                                       | Order item code                                                        |
| 35  | `Order Item Product Price`      | numeric (float64)  | –                | 75      | 59.99, 129.99, 50                                                            | Price of products without discount                                     |
| 36  | `Order Item Profit Ratio`       | numeric (float64)  | –                | 162     | 0.48, 0.35, 0.26                                                             | Order Item Profit Ratio                                                |
| 37  | `Order Item Quantity`           | numeric (int64)    | –                | 5       | 1, 5, 3                                                                      | Number of products per order                                           |
| 38  | `Sales`                         | numeric (float64)  | –                | 193     | 129.99, 399.98, 199.99                                                       | Value in sales                                                         |
| 39  | `Order Item Total`              | numeric (float64)  | –                | 2,927   | 122.84, 109.19, 127.39                                                       | Total amount per order                                                 |
| 40  | `Order Profit Per Order`        | numeric (float64)  | –                | 21,998  | 0, 143.99, 72                                                                | Order Profit Per Order                                                 |
| 41  | `Order Region`                  | text (str)         | –                | 23      | Central America, Western Europe, South America                               | Region of the world where the order is delivered : Southeast Asia ,S…  |
| 42  | `Order State`                   | text (str)         | –                | 1,089   | Inglaterra, California, Isla de Francia                                      | State of the region where the order is delivered                       |
| 43  | `Order Status`                  | text (str)         | –                | 9       | COMPLETE, PENDING_PAYMENT, PROCESSING                                        | Order Status : COMPLETE , PENDING , CLOSED , PENDING_PAYMENT ,CANCELE… |
| 44  | `Order Zipcode`                 | numeric (float64)  | 155,679 (86.2%)  | 609     | 10035, 10009, 10024                                                          | —                                                                      |
| 45  | `Product Card Id`               | numeric (int64)    | –                | 118     | 365, 403, 502                                                                | Product code                                                           |
| 46  | `Product Category Id`           | numeric (int64)    | –                | 51      | 17, 18, 24                                                                   | Product category code                                                  |
| 47  | `Product Description`           | empty (float64)    | 180,519 (100.0%) | 0       |                                                                              | Product Description                                                    |
| 48  | `Product Image`                 | text (str)         | –                | 118     | http://images.acmesport…, http://images.acmesport…, http://images.acmesport… | Link of visit and purchase of the product                              |
| 49  | `Product Name`                  | text (str)         | –                | 118     | Perfect Fitness Perfect…, Nike Men's CJ Elite 2 T…, Nike Men's Dri-FIT Vict… | Product Name                                                           |
| 50  | `Product Price`                 | numeric (float64)  | –                | 75      | 59.99, 129.99, 50                                                            | Product Price                                                          |
| 51  | `Product Status`                | numeric (int64)    | –                | 1       | 0                                                                            | Status of the product stock :If it is 1 not available , 0 the product… |
| 52  | `shipping date (DateOrders)`    | date (text) (str)  | –                | 63,701  | 5/9/2015 18:02, 9/27/2015 20:28, 9/24/2015 23:48                             | Exact date and time of shipment                                        |
| 53  | `Shipping Mode`                 | text (str)         | –                | 4       | Standard Class, Second Class, First Class                                    | The following shipping modes are presented : Standard Class , First C… |

### Numeric columns

| Column                          | Min       | 25%       | Median | Mean      | 75%        | Max      | Std       | Zeros  | Negative | IQR outliers |
| ------------------------------- | --------- | --------- | ------ | --------- | ---------- | -------- | --------- | ------ | -------- | ------------ |
| `Days for shipping (real)`      | 0         | 2         | 3      | 3.50      | 5          | 6        | 1.62      | 2.8%   | 0%       | 0%           |
| `Days for shipment (scheduled)` | 0         | 2         | 4      | 2.93      | 4          | 4        | 1.37      | 5.4%   | 0%       | 0%           |
| `Benefit per order`             | -4,274.98 | 7         | 31.52  | 21.97     | 64.80      | 911.80   | 104.43    | 0.7%   | 18.7%    | 10.5%        |
| `Sales per customer`            | 7.49      | 104.38    | 163.99 | 183.11    | 247.40     | 1,939.99 | 120.04    | 0%     | 0%       | 1.1%         |
| `Category Id`                   | 2         | 18        | 29     | 31.85     | 45         | 76       | 15.64     | 0%     | 0%       | 0%           |
| `Customer Id`                   | 1         | 3,258.50  | 6,457  | 6,691.38  | 9,779      | 20,757   | 4,162.92  | 0%     | 0%       | 0.7%         |
| `Customer Zipcode`              | 603       | 725       | 19,380 | 35,921.13 | 78,207     | 99,205   | 37,542.46 | 0%     | 0%       | 0%           |
| `Department Id`                 | 2         | 4         | 5      | 5.44      | 7          | 12       | 1.63      | 0%     | 0%       | 0.2%         |
| `Latitude`                      | -33.94    | 18.27     | 33.14  | 29.72     | 39.28      | 48.78    | 9.81      | 0%     | <0.1%    | <0.1%        |
| `Longitude`                     | -158.03   | -98.45    | -76.85 | -84.92    | -66.37     | 115.26   | 21.43     | 0%     | 99.9%    | 0.8%         |
| `Order Customer Id`             | 1         | 3,258.50  | 6,457  | 6,691.38  | 9,779      | 20,757   | 4,162.92  | 0%     | 0%       | 0.7%         |
| `Order Id`                      | 1         | 18,057    | 36,140 | 36,221.89 | 54,144     | 77,204   | 21,045.38 | 0%     | 0%       | 0%           |
| `Order Item Cardprod Id`        | 19        | 403       | 627    | 692.51    | 1,004      | 1,363    | 336.45    | 0%     | 0%       | 0%           |
| `Order Item Discount`           | 0         | 5.40      | 14     | 20.66     | 29.99      | 500      | 21.80     | 5.6%   | 0%       | 4.2%         |
| `Order Item Discount Rate`      | 0         | 0.04      | 0.10   | 0.10      | 0.16       | 0.25     | 0.07      | 5.6%   | 0%       | 0%           |
| `Order Item Id`                 | 1         | 45,130.50 | 90,260 | 90,260    | 135,389.50 | 180,519  | 52,111.49 | 0%     | 0%       | 0%           |
| `Order Item Product Price`      | 9.99      | 50        | 59.99  | 141.23    | 199.99     | 1,999.99 | 139.73    | 0%     | 0%       | 1.1%         |
| `Order Item Profit Ratio`       | -2.75     | 0.08      | 0.27   | 0.12      | 0.36       | 0.50     | 0.47      | 0.7%   | 18.7%    | 9.6%         |
| `Order Item Quantity`           | 1         | 1         | 1      | 2.13      | 3          | 5        | 1.45      | 0%     | 0%       | 0%           |
| `Sales`                         | 9.99      | 119.98    | 199.92 | 203.77    | 299.95     | 1,999.99 | 132.27    | 0%     | 0%       | 0.3%         |
| `Order Item Total`              | 7.49      | 104.38    | 163.99 | 183.11    | 247.40     | 1,939.99 | 120.04    | 0%     | 0%       | 1.1%         |
| `Order Profit Per Order`        | -4,274.98 | 7         | 31.52  | 21.97     | 64.80      | 911.80   | 104.43    | 0.7%   | 18.7%    | 10.5%        |
| `Order Zipcode`                 | 1,040     | 23,464    | 59,405 | 55,426.13 | 90,008     | 99,301   | 31,919.28 | 0%     | 0%       | 0%           |
| `Product Card Id`               | 19        | 403       | 627    | 692.51    | 1,004      | 1,363    | 336.45    | 0%     | 0%       | 0%           |
| `Product Category Id`           | 2         | 18        | 29     | 31.85     | 45         | 76       | 15.64     | 0%     | 0%       | 0%           |
| `Product Price`                 | 9.99      | 50        | 59.99  | 141.23    | 199.99     | 1,999.99 | 139.73    | 0%     | 0%       | 1.1%         |
| `Product Status`                | 0         | 0         | 0      | 0         | 0          | 0        | 0         | 100.0% | 0%       | 0%           |

### Date/time columns

| Column                       | Format           | Earliest         | Latest           | Span (days) | Distinct days | Unparsed |
| ---------------------------- | ---------------- | ---------------- | ---------------- | ----------- | ------------- | -------- |
| `order date (DateOrders)`    | `%m/%d/%Y %H:%M` | 2015-01-01 00:00 | 2018-01-31 23:38 | 1,126       | 1,127         | 0        |
| `shipping date (DateOrders)` | `%m/%d/%Y %H:%M` | 2015-01-03 00:00 | 2018-02-06 22:14 | 1,130       | 1,131         | 0        |

### Value distributions (columns with ≤25 distinct values)

- **`Type`** (4): DEBIT 38.4% · TRANSFER 27.6% · PAYMENT 23.1% · CASH 10.9%
- **`Days for shipping (real)`** (7): 2 31.4% · 3 15.9% · 6 15.9% · 4 15.8% · 5 15.6% · 0 2.8% · … +1 more
- **`Days for shipment (scheduled)`** (4): 4 59.7% · 2 19.5% · 1 15.4% · 0 5.4%
- **`Delivery Status`** (4): Late delivery 54.8% · Advance shipping 23.0% · Shipping on time 17.8% · Shipping canceled 4.3%
- **`Late_delivery_risk`** (2): 1 54.8% · 0 45.2%
- **`Customer Country`** (2): EE. UU. 61.6% · Puerto Rico 38.4%
- **`Customer Segment`** (3): Consumer 51.8% · Corporate 30.4% · Home Office 17.9%
- **`Department Id`** (11): 7 37.0% · 4 27.1% · 5 18.4% · 3 8.0% · 6 5.4% · 2 1.4% · … +5 more
- **`Department Name`** (11): Fan Shop 37.0% · Apparel 27.1% · Golf 18.4% · Footwear 8.0% · Outdoors 5.4% · Fitness 1.4% · … +5 more
- **`Market`** (5): LATAM 28.6% · Europe 27.8% · Pacific Asia 22.9% · USCA 14.3% · Africa 6.4%
- **`Order Item Discount Rate`** (18): 0.04 5.6% · 0.05 5.6% · 0.06 5.6% · 0.07 5.6% · 0.09 5.6% · 0.1 5.6% · … +12 more
- **`Order Item Quantity`** (5): 1 54.9% · 5 11.3% · 3 11.3% · 4 11.3% · 2 11.3%
- **`Order Region`** (23): Central America 15.7% · Western Europe 15.0% · South America 8.3% · Oceania 5.6% · Northern Europe 5.4% · Southeast Asia 5.3% · … +17 more
- **`Order Status`** (9): COMPLETE 33.0% · PENDING_PAYMENT 22.1% · PROCESSING 12.1% · PENDING 11.2% · CLOSED 10.9% · ON_HOLD 5.4% · … +3 more
- **`Shipping Mode`** (4): Standard Class 59.7% · Second Class 19.5% · First Class 15.4% · Same Day 5.4%

### Data dictionary coverage

- Columns without a description: `Order Zipcode`
- Dictionary entries with no matching column: none

## tokenized_access_logs.csv

- **Rows × columns:** 469,977 × 8
- **Read with:** `utf-8`
- **Memory in pandas:** 255 MB
- **Fully duplicated rows:** 3,249 (0.7%)
- **Columns with missing values:** 0 of 8

### Flags

_Things to check before cleaning. Each one may be fine; that's for you to decide._

**Dates stored as text:**

- `Date`: dates stored as text (format `%m/%d/%Y %H:%M`)

**Leading/trailing whitespace:**

- `Department`: 469,977 values have leading/trailing whitespace

### Columns

| #   | Column       | Type              | Missing | Unique  | Most common values                                                           |
| --- | ------------ | ----------------- | ------- | ------- | ---------------------------------------------------------------------------- |
| 1   | `Product`    | text (str)        | –       | 76      | Perfect Fitness Perfect…, adidas Kids' RG III Mid…, Nike Men's Dri-FIT Vict… |
| 2   | `Category`   | text (str)        | –       | 33      | cleats, shop by sport, featured shops                                        |
| 3   | `Date`       | date (text) (str) | –       | 160,815 | 9/14/2017 20:34, 9/14/2017 20:37, 9/14/2017 21:05                            |
| 4   | `Month`      | text (str)        | –       | 5       | Sep, Oct, Dec                                                                |
| 5   | `Hour`       | numeric (int64)   | –       | 24      | 21, 20, 22                                                                   |
| 6   | `Department` | text (str)        | –       | 6       | outdoors , apparel , footwear                                                |
| 7   | `ip`         | text (str)        | –       | 3,340   | 157.21.93.193, 138.21.216.113, 77.137.114.147                                |
| 8   | `url`        | text (str)        | –       | 152     | /department/apparel/cat…, /department/apparel/cat…, /department/golf/catego… |

### Numeric columns

| Column | Min | 25% | Median | Mean  | 75% | Max | Std  | Zeros | Negative | IQR outliers |
| ------ | --- | --- | ------ | ----- | --- | --- | ---- | ----- | -------- | ------------ |
| `Hour` | 0   | 10  | 15     | 14.59 | 20  | 23  | 5.57 | 0.5%  | 0%       | 0%           |

### Date/time columns

| Column | Format           | Earliest         | Latest           | Span (days) | Distinct days | Unparsed |
| ------ | ---------------- | ---------------- | ---------------- | ----------- | ------------- | -------- |
| `Date` | `%m/%d/%Y %H:%M` | 2017-09-01 06:00 | 2018-01-31 23:58 | 152         | 153           | 0        |

### Value distributions (columns with ≤25 distinct values)

- **`Month`** (5): Sep 29.2% · Oct 17.9% · Dec 17.9% · Jan 17.8% · Nov 17.2%
- **`Hour`** (24): 21 6.5% · 20 6.5% · 22 6.3% · 19 6.0% · 23 5.9% · 18 5.4% · … +18 more
- **`Department`** (6): outdoors 17.0% · apparel 16.9% · footwear 16.8% · fan shop 16.8% · fitness 16.3% · golf 16.3%
