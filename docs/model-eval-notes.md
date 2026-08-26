# Model eval notes

Running log of evaluation findings per fine-tuned checkpoint. Add an entry
each time you evaluate a new checkpoint via `backend/scripts/evaluate.py`.

## Template for each entry

### checkpoint-name (date)

- Base model / LoRA config used:
- Dataset size (train / eval), language breakdown:
- Coding eval: pass rate, notable failures
- Research eval: notable failures
- Juba Arabic eval: reviewer name, findings (REQUIRED — no automated metric
  substitutes for this)
- Decision: ship / iterate / discard
