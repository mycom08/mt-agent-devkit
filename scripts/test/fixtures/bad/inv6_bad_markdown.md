# Fixture: invariant #6 -- Markdown well-formedness

## 1. Normal H2 section

Some content.

### Normal H3 sub-section

Content here.

##### Skipped H5 (jumps from H3 to H5 -- should be flagged)

The heading above jumps from level 3 to level 5, skipping level 4.

Also, the code fence below is intentionally unclosed:

```python
def example():
    print("This fence is never closed")
