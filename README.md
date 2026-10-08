# Ofgem Cap Watch

A small Streamlit dashboard that tracks the UK default tariff cap from
April 2019 to the present, models what a Fuse-style variable tariff
sitting below the cap would have meant for a typical household, and runs
a back-of-envelope on the value of off-peak load shifting (the prize
Fuse Energy's *Project Zero* is going after).

**Live demo:** _add Streamlit Cloud URL after deploying_

## What it does

1. **Cap history chart.** Quarterly default tariff cap from Apr 2019, annotated
   with the events that moved it — Covid demand collapse, the Russian gas
   shock, the EPG, and the April 2026 7% cut.
2. **Variable-tariff simulator.** Pick a discount-vs-cap (Fuse's reported gap
   has sat in the 3–7% band) and a comparison window. See cumulative savings
   for a typical household.
3. **Off-peak shifting simulator.** Slide flexible kWh, peak-vs-off-peak gap,
   and shift-success share. Get an indicative annual saving — the value Energy
   Dollar accrual is competing with on the consumer side.

## Why I built it

I'm applying to Fuse Energy's Operations Internship and wanted a working
view of the economics customer-ops will be explaining every day. The
interesting friction isn't the headline cap — it's the gap between the
cap and what a variable tariff *can* deliver, and the gap between *what
shifting is worth* and *what customers will actually shift*. Both are
operational problems before they're technical ones.

## Running locally

```bash
git clone https://github.com/[your-github-username]/ofgem-cap-watch.git
cd ofgem-cap-watch
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

## Deploying to Streamlit Community Cloud (free)

1. Push this repo to GitHub (public).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click *New app*, pick this repo, branch `main`, file `app.py`.
4. Deploy. You'll get a public URL like `https://[your-app].streamlit.app`.
5. Add that URL to your CV and to the repo description.

## Updating data

Cap data lives in `data/price_cap_history.csv`. Ofgem announces each
quarter ~6 weeks before it starts; replace the latest row with the new
period when the announcement lands.

Source: https://www.ofgem.gov.uk/energy-policy-and-regulation/policy-and-regulatory-programmes/default-tariff-cap

## Caveats

- Cap figures are headline annual values for typical dual-fuel direct-debit
  households. Actual bills vary by region, usage, and standing charge.
- The variable-tariff sim applies a flat discount to the cap. Real variable
  tariffs price off wholesale and other costs, not the cap directly.
- The off-peak sim ignores standing charges and network levies.

## Stack

Python · Streamlit · pandas · Altair

## License

MIT
