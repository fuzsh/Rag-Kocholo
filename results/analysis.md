Let's break down the metrics for each category, dividing them into correct and incorrect metrics separately. We'll also separate them into their respective categories like `death` and `mix_*_death`, considering `mix_*` as wrong queries.

### Detailed Metrics

#### Death Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| death | 142 | 8 | 0 | 0.9467 |
| mix_random_death | 24 | 2 | 0 | 0.9231 |
| mix_domainrange_death | 26 | 0 | 0 | 1.0000 |
| mix_domain_death | 25 | 1 | 0 | 0.9615 |
| mix_range_death | 25 | 1 | 0 | 0.9615 |
| mix_property_death | 15 | 11 | 0 | 0.5769 |
| **Total** | 257 | 23 | 0 | 0.9179 |

#### Award Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| award | 150 | 0 | 0 | 1.0000 |
| mix_random_award | 25 | 1 | 0 | 0.9615 |
| mix_domainrange_award | 20 | 6 | 0 | 0.7692 |
| mix_domain_award | 22 | 4 | 0 | 0.8462 |
| mix_range_award | 19 | 7 | 0 | 0.7308 |
| mix_property_award | 10 | 16 | 0 | 0.3846 |
| **Total** | 246 | 34 | 0 | 0.8783 |

#### NBA Team Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| nbateam | 150 | 0 | 0 | 1.0000 |
| mix_random_nbateam | 24 | 2 | 0 | 0.9231 |
| mix_domainrange_nbateam | 15 | 11 | 0 | 0.5769 |
| mix_domain_nbateam | 9 | 17 | 0 | 0.3462 |
| mix_range_nbateam | 9 | 17 | 0 | 0.3462 |
| mix_property_nbateam | 15 | 11 | 0 | 0.5769 |
| **Total** | 222 | 58 | 0 | 0.7929 |

#### Spouse Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| spouse | 147 | 3 | 0 | 0.9800 |
| mix_random_spouse | 23 | 2 | 1 | 0.8846 |
| mix_domainrange_spouse | 21 | 5 | 0 | 0.8077 |
| mix_domain_spouse | 20 | 5 | 1 | 0.7692 |
| mix_range_spouse | 22 | 4 | 0 | 0.8462 |
| mix_property_spouse | 15 | 10 | 1 | 0.5769 |
| **Total** | 248 | 29 | 3 | 0.8955 |

#### Birth Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| birth | 148 | 2 | 0 | 0.9867 |
| mix_random_birth | 22 | 4 | 0 | 0.8462 |
| mix_domainrange_birth | 24 | 2 | 0 | 0.9231 |
| mix_domain_birth | 26 | 0 | 0 | 1.0000 |
| mix_range_birth | 26 | 0 | 0 | 1.0000 |
| mix_property_birth | 14 | 12 | 0 | 0.5385 |
| **Total** | 260 | 20 | 0 | 0.9286 |

#### FoundationPlace Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| foundationPlace | 97 | 53 | 0 | 0.6467 |
| mix_random_foundationPlace | 21 | 5 | 0 | 0.8077 |
| mix_domainrange_foundationPlace | 21 | 5 | 0 | 0.8077 |
| mix_domain_foundationPlace | 23 | 3 | 0 | 0.8846 |
| mix_range_foundationPlace | 17 | 9 | 0 | 0.6538 |
| mix_property_foundationPlace | 14 | 10 | 2 | 0.5385 |
| **Total** | 193 | 85 | 2 | 0.6961 |

#### Starring Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| starring | 148 | 2 | 0 | 0.9867 |
| mix_random_starring | 21 | 4 | 1 | 0.8077 |
| mix_domainrange_starring | 22 | 4 | 0 | 0.8462 |
| mix_domain_starring | 20 | 6 | 0 | 0.7692 |
| mix_range_starring | 17 | 9 | 0 | 0.6538 |
| mix_property_starring | 6 | 20 | 0 | 0.2308 |
| **Total** | 234 | 45 | 1 | 0.8378 |

#### Leader Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| leader | 150 | 0 | 0 | 1.0000 |
| mix_random_leader | 25 | 0 | 1 | 0.9615 |
| mix_domainrange_leader | 25 | 1 | 0 | 0.9615 |
| mix_domain_leader | 25 | 1 | 0 | 0.9615 |
| mix_range_leader | 22 | 4 | 0 | 0.8462 |
| mix_property_leader | 9 | 17 | 0 | 0.3462 |
| **Total** | 256 | 23 | 1 | 0.9182 |

#### PublicationDate Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| publicationDate | 146 | 4 | 0 | 0.9733 |
| mix_random_publicationDate | 22 | 4 | 0 | 0.8462 |
| mix_domainrange_publicationDate | 22 | 4 | 0 | 0.8462 |
| mix_domain_publicationDate | 17 | 9 | 0 | 0.6538 |
| mix_range_publicationDate | 15 | 11 | 0 | 0.5769 |
| mix_property_publicationDate | 13 | 12 | 1 | 0.5000 |
| **Total** | 235 | 44 | 1 | 0.8429 |

#### Subsidiary Category

| Subcategory | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| subsidiary | 139 | 9 | 2 | 0.9267 |
| mix_random_subsidiary | 23 | 3 | 0 | 0.8846 |
| mix_domainrange_subsidiary | 19 | 5 | 1 | 0.7600 |
| mix_domain_subsidiary | 19 | 6 | 1 | 0.7308 |
| mix_range_subsidiary | 20 | 6 | 0 | 0.7692 |
| mix_property_subsidiary | 13 | 12 | 1 | 0.5000 |
| **Total** | 233 | 41 | 5 | 0.8519 |

### Summary

Here is a consolidated view of the metrics divided for correct ones and wrong ones separately and also for each category:

| Category | Correct | Incorrect | Not understandable | Overall Accuracy |
| --- | --- | --- | --- | --- |
| death | 257 | 23 | 0 | 0.9179 |
| award | 246 | 34 | 0 | 0.8783 |
| nbateam | 222 | 58 | 0 | 0.7929 |
| spouse | 248 | 29 | 3 | 0.8955 |
| birth | 260 | 20 | 0 | 0.9286 |
| foundationPlace | 193 | 85 | 2 | 0.6961 |
| starring | 234 | 45 | 1 | 0.8378 |
| leader | 256 | 23 | 1 | 0.9182 |
| publicationDate | 235 | 44 | 1 | 0.8429 |
| subsidiary | 233 | 41 | 5 | 0.8519 |
| **Total** | **2384** | **402** | **13** | **0.8517**


In this detailed breakdown, the "Overall Accuracy" is calculated for each category by combining the main category metrics and the corresponding `mix_*` subcategory metrics. The table shows a clearer picture of the performance of each category, including the division between correct, incorrect, and not understandable results.