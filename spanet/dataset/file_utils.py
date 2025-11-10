"""
Utility functions for handling file paths with wildcard patterns in SPANet.
Allows combining multiple HDF5 files that match a pattern or a list of patterns.
"""
import glob
import os
import tempfile
from typing import List, Union

import h5py

# Import shared utilities for concatenation
import sys
# Get the SPANet root directory (3 levels up from this file)
spanet_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
utils_path = os.path.join(spanet_root, 'utils', 'shared.py')
if os.path.exists(utils_path):
    # Add SPANet root to path so we can import utils.shared
    if spanet_root not in sys.path:
        sys.path.insert(0, spanet_root)
    from utils.shared import concatenate, extract, write as write_hdf5
else:
    # Fallback: try importing with SPANet prefix
    try:
        from SPANet.utils.shared import concatenate, extract, write as write_hdf5
    except ImportError:
        # Last resort: assume utils is in path
        from utils.shared import concatenate, extract, write as write_hdf5


def _expand_single_pattern(pattern: str, verbose: bool = True) -> List[str]:
    """
    Expand a single wildcard pattern to find matching HDF5 files.
    
    Parameters
    ----------
    pattern : str
        File path pattern that may contain wildcards (*, ?, [])
    verbose : bool
        Whether to print progress information
        
    Returns
    -------
    List[str]
        List of matching file paths (sorted)
    """
    # Check if pattern contains wildcards
    has_wildcard = '*' in pattern or '?' in pattern or '[' in pattern
    
    if has_wildcard:
        # Expand pattern to find matching files
        matching_files = sorted(glob.glob(pattern))
        if not matching_files:
            raise FileNotFoundError(
                f"No files found matching pattern: {pattern}"
            )
        
        if verbose:
            print(f"Found {len(matching_files)} files matching pattern: {pattern}")
            for i, f in enumerate(matching_files, 1):
                print(f"  {i}. {f}")
        
        return matching_files
    else:
        # No wildcards - just check if file exists
        if not os.path.exists(pattern):
            raise FileNotFoundError(f"File not found: {pattern}")
        return [pattern]


def _combine_hdf5_files(file_list: List[str], verbose: bool = True) -> str:
    """
    Combine multiple HDF5 files into a single temporary file.
    
    Parameters
    ----------
    file_list : List[str]
        List of HDF5 file paths to combine
    verbose : bool
        Whether to print progress information
        
    Returns
    -------
    str
        Path to the combined HDF5 file
    """
    if not file_list:
        raise ValueError("file_list cannot be empty")
    
    if len(file_list) == 1:
        # Only one file, return it directly
        return file_list[0]
    
    # Multiple files - combine them
    if verbose:
        print(f"Combining {len(file_list)} HDF5 files...")
    
    # Extract data from all files
    all_data = []
    for filename in file_list:
        if verbose:
            print(f"Reading: {filename}")
        with h5py.File(filename, 'r') as file:
            all_data.append(extract(file))
    
    # Concatenate all data
    if verbose:
        print("Concatenating datasets...")
    combined_data = concatenate(*all_data)
    
    # Create temporary file
    temp_fd, output_file = tempfile.mkstemp(suffix='.h5', prefix='spanet_combined_')
    os.close(temp_fd)  # Close file descriptor, but keep the file
    
    if verbose:
        print(f"Writing combined file to: {output_file}")
    
    with h5py.File(output_file, 'w') as output:
        write_hdf5(combined_data, output, verbose=verbose)
    
    return output_file


def expand_and_combine_hdf5(pattern: Union[str, List[str]], verbose: bool = True) -> str:
    """
    Expand one or more wildcard patterns to find matching HDF5 files and combine them.
    
    If the input is a list of patterns, all matching files from all patterns are combined.
    If a pattern doesn't contain wildcards and points to a single file, that file is included.
    Otherwise, combines all matching files into a temporary file and returns the path.
    
    Parameters
    ----------
    pattern : str or List[str]
        File path pattern(s) that may contain wildcards (*, ?, [])
        Can be a single string or a list of strings
    verbose : bool
        Whether to print progress information
        
    Returns
    -------
    str
        Path to a single HDF5 file (original or combined)
    """
    # Handle list of patterns
    if isinstance(pattern, list):
        if verbose:
            print(f"Processing {len(pattern)} pattern(s)...")
        
        # Expand all patterns and collect all matching files
        all_matching_files = []
        for p in pattern:
            matching_files = _expand_single_pattern(p, verbose=verbose)
            all_matching_files.extend(matching_files)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in all_matching_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        
        if verbose and len(all_matching_files) != len(unique_files):
            print(f"Removed {len(all_matching_files) - len(unique_files)} duplicate files")
        
        # Combine all files
        return _combine_hdf5_files(unique_files, verbose=verbose)
    
    # Handle single pattern (existing behavior)
    else:
        matching_files = _expand_single_pattern(pattern, verbose=verbose)
        return _combine_hdf5_files(matching_files, verbose=verbose)
