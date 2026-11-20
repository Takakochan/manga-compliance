# Rules

One YAML file per country. Each rule maps a flag to an outcome and says where its legal basis lives.

```yaml
- id: DE-SYMBOL-01            # unique, COUNTRY-TOPIC-NN
  country: DE                 # ISO code
  category: prohibited_symbol # one of the 8 flag categories
  min_severity: moderate      # mild | moderate | strong; the flag must be at least this
  sources: [image, text]      # optional; default both
  outcome: blocked            # ok < review < age_restricted < edit_required < blocked
  label: Symbol of an unconstitutional organisation
  doc: DE/stgb_86a.md         # file in corpus/ that holds the basis
  query: Kennzeichen verfassungswidriger Organisationen verwenden  # search text for step 3
```

How a page is judged:

- For each flag, the **strictest** matching rule of that country wins.
- The page outcome for a country is the strictest outcome among its findings.
- No matching rule means the flag is not a finding in that country.

Write `query` in the language of the source document. Mark a rule `DRAFT` in the file header until someone has read the source paragraph.

Next markets: UK and US (`uk.yaml`, `us.yaml`). The US has no state rating for books; use publishers' own age ratings.
