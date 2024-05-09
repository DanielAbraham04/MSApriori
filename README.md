# Market Basket Analysis using MSApriori Algorithm

This project implements the MSApriori algorithm in Python to perform market basket analysis on supermarket transaction data. The goal is to identify frequent itemsets, analyze patterns, and extract insights into consumer behavior. This analysis can help businesses understand purchasing trends and optimize product placement, marketing strategies, and inventory management.

Features:
1. Generates frequent itemsets from supermarket transaction data.
2. Implements the MSApriori algorithm with configurable parameters.
3. Identifies patterns in consumer behavior.
4. Supports minimum item support (MIS), support difference constraints (SDC), and lambda values for flexibility.

Parameters:
The script takes four parameters in the following order:

1. Path to Data File: The location of the file containing transaction data (e.g., data/transactions.csv).
2. Path to MIS File: The path to the MIS file, created by the script using a lambda value (e.g., output/mis.txt).
3. Lambda Value: A floating-point value used to set the minimum support values for items.
4. SDC Value: A floating-point value for the Support Difference Constraint, allowing variation in item support.
