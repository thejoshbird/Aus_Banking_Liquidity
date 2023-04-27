# Aus_Banking_Liquidity
A Python script to scrape marketwatch.com.au for aussie banks deposit coverage. 
This came about following Silicon Valley Banks collapse over the last few days. 
I tried to see if there was any exposure here in Australia, however, found that my source of information was drastically 
inconsistent between the different banks :)

For example, if you take a look at Westpac's deposits for 2022, it claims they hold $46,295m 
in customer deposits. However, looking at their financial statement: https://www.westpac.com.au/about-westpac/investor-centre/financial-information/annual-reports/
We can see that on Page 210, that this figure is for 'Total Certificates of deposit in excess
of insured amounts' 

CBA, on the other hand, has a different formulation for their Deposits on IntelligentInvestor.com.au

As such, the value of such analysis is limited until a more consistent source of truth is found.
Additionally, there was only complete information for 8 ADI institutions, so more info is required.

Formula used: (Short Term Money + Investment Securities)/Deposits
ie. For every $1 of deposits, BankA has $2 of liquid assets

This ratio could be improved with more sophisticated metrics, but given this was sort of a mini-project, I simply used the most available data.

