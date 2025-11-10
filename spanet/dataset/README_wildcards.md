# Wildcard Pattern Support in SPANet

SPANet now supports wildcard patterns and lists of patterns for `training_file`, `validation_file`, and `testing_file` in the options JSON file.

## Usage Examples

### Single Wildcard Pattern

```json
{
    "training_file": "/path/to/files/*_train.h5",
    "validation_file": "/path/to/files/*_val.h5"
}
```

### Multiple Patterns as a List

You can specify a list of patterns to combine files from different sources:

```json
{
    "training_file": [
        "/path/to/files/mc20_13TeV.*signal_H260_A80*train.h5",
        "/path/to/files/mc20_13TeV.*tty*train.h5"
    ],
    "validation_file": [
        "/path/to/files/mc20_13TeV.*signal_H260_A80*val.h5",
        "/path/to/files/mc20_13TeV.*tty*val.h5"
    ]
}
```

### Mixed Patterns

You can also mix wildcard patterns with specific file paths:

```json
{
    "training_file": [
        "/specific/file.h5",
        "/path/to/other/*_train.h5"
    ]
}
```

## How It Works

1. **Pattern Expansion**: The code uses Python's `glob` module to expand wildcard patterns (`*`, `?`, `[]`) to find all matching files.

2. **File Combination**: If multiple files match (either from a single pattern or multiple patterns), they are automatically combined into a temporary HDF5 file.

3. **Duplicate Handling**: If the same file matches multiple patterns, duplicates are automatically removed.

4. **Backward Compatibility**: If you don't use wildcards and specify a single file path, it works exactly as before.

## Notes

- Patterns are processed in order
- Duplicate files are removed automatically
- Combined files are stored in temporary files (typically in `/tmp/`)
- Verbose output can be enabled via `"verbose_output": true` to see which files are being combined

