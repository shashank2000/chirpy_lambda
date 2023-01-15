## Integration tests

You can run these tests using 

```
pytest
```

in the `tests/` directory. You'll need to have a Bluejay server up; see `bluejay/` for details on that.

## Writing your own tests

Principles of good test design:
- Don't have tests be dependent on long strings of dialogue to get to the node you want---this exposes your tests to arbitrary dependencies.
- In particular, split a test into two sections:
  - **Accessing the node**: Write a test that verifies that some dialogue activates a node.
  - **Testing the node dialogue**: Set flags, state, and prioritized_supernode judiciously to get to the node you want to trigger.
  
*(Why? Historically, tests were hard to use because they often depended on long activation dialogues \[see `tests/` for old these\]. These were hard to use; tests would often break due to unforeseen dependencies on other parts of the bot. We're hoping to avoid that this year.*

Implementation notes:
- Note that you need to always assert an equals for nice log messages to come out. In particular, instead of writing:
```python
assert x
```
- try writing:
```python
assert x == True
```

This is necessary to trigger the rewrite hook.

## TODOS

In terms of code, we would like to add:
- Setting flags and state using kwargs
- Spreadsheet integration for full runs of tests
