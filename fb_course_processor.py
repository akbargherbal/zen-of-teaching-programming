"""
Course Materials Processing Pipeline
Processes course materials through multiple stages: copy, unzip, convert, and consolidate.
"""

import shutil
import zipfile
from pathlib import Path
from typing import List
import pandas as pd
import pymupdf
import srt
import re

# ============================================================================
# STAGE 00: Directory Copy Functions
# ============================================================================


def copy_directory_filtered(
    source_path: str,
    target_name: str = "STAGE_00_course_materials",
    exclude_extensions: List[str] = None,
) -> Path:
    """
    Copy a directory to the current working directory, excluding files with specified extensions.
    """
    if exclude_extensions is None:
        exclude_extensions = [".mp4"]

    exclude_extensions = [
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in exclude_extensions
    ]

    source = Path(source_path).resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_path}")

    target = Path.cwd() / target_name
    target = target.resolve()

    # SAFETY CHECK: Prevent copying directory into itself
    if target == source:
        raise ValueError("Target directory cannot be the same as source directory")
    if source in target.parents:
        raise ValueError("Cannot copy a directory into itself")
    if target.exists() and source in target.resolve().parents:
        raise ValueError(
            "Target already exists inside source - would create infinite loop"
        )

    # Remove target if it already exists
    if target.exists():
        print(f"Warning: Removing existing directory: {target}")
        shutil.rmtree(target)

    target.mkdir(parents=True, exist_ok=True)

    # Walk through source directory and copy files
    for item in source.rglob("*"):
        try:
            if target in item.resolve().parents or item.resolve() == target:
                continue
        except (OSError, ValueError):
            continue

        if item.is_file():
            if item.suffix.lower() in exclude_extensions:
                continue

            relative_path = item.relative_to(source)
            target_file = target / relative_path
            target_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(item, target_file)
            except Exception as e:
                print(f"Failed to copy {item}: {e}")

    return target


def unzip_with_prefix(directory: str = ".") -> None:
    """
    Unzip all .zip files in directory and prefix extracted files with the zip filename.

    Example:
        '011 Decorators-1.zip' containing 'Decorators 1.ipynb'
        becomes '011 Decorators-Decorators 1.ipynb'
    """
    dir_path = Path(directory)
    zip_files = list(dir_path.glob("*.zip"))

    if not zip_files:
        print("No zip files found.")
        return

    for zip_path in zip_files:
        zip_stem = zip_path.stem
        print(f"\nProcessing: {zip_path.name}")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            file_list = zip_ref.namelist()

            for file_name in file_list:
                if file_name.endswith("/"):
                    continue

                file_data = zip_ref.read(file_name)
                original_name = Path(file_name).name
                new_name = f"{zip_stem}-{original_name}"
                new_path = dir_path / new_name

                new_path.write_bytes(file_data)
                print(f"  Extracted: {original_name} -> {new_name}")

        print(f"  ✓ Completed: {zip_path.name}")


# ============================================================================
# STAGE 01: Format Conversion Functions
# ============================================================================


def batch_convert_pdfs(directory: str) -> None:
    """Convert all PDF files in directory to .txt files in the same directory."""
    dir_path = Path(directory)
    pdf_files = list(dir_path.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return

    for pdf_file in pdf_files:
        output_file = dir_path / f"{pdf_file.stem}.txt"

        doc = pymupdf.open(pdf_file)
        with open(output_file, "w", encoding="utf-8") as f:
            for page_num, page in enumerate(doc, 1):
                f.write(f"\n--- Slide {page_num} ---\n\n")
                pdf_text = page.get_text("text")
                pdf_text = re.sub("©.*$", "", pdf_text)
                f.write(pdf_text)
        doc.close()

        print(f"✓ {pdf_file.name} → {output_file.name}")


def extract_text_from_srt(srt_path: Path) -> str:
    """Extract only text from SRT file using the srt library."""
    with open(srt_path, "r", encoding="utf-8") as f:
        subtitles = srt.parse(f.read())
    return "\n".join(sub.content for sub in subtitles)


def convert_notebooks_to_markdown(directory: str) -> None:
    """Convert all Jupyter notebooks to markdown and remove original .ipynb files."""
    import subprocess

    dir_path = Path(directory)
    ipynb_files = list(dir_path.glob("*.ipynb"))

    if not ipynb_files:
        print("No notebook files found.")
        return

    print(f"Converting {len(ipynb_files)} notebooks to markdown...")

    # Convert all notebooks
    result = subprocess.run(
        ["jupyter", "nbconvert", "--to", "markdown", "*.ipynb"],
        cwd=dir_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✓ Conversion complete")

        # Remove original .ipynb files
        for ipynb_file in ipynb_files:
            ipynb_file.unlink()
        print(f"✓ Removed {len(ipynb_files)} .ipynb files")
    else:
        print(f"Error during conversion: {result.stderr}")


# ============================================================================
# STAGE 02: Consolidation Functions
# ============================================================================


def consolidate_course_materials(
    directory: str, output_file: str = "consolidated_materials.txt"
) -> None:
    """
    Walk through directory, read all files, and consolidate into a single text file.
    Handles .srt files specially with text extraction.
    """
    dir_path = Path(directory)

    # Collect all files
    all_files = []
    for item in dir_path.rglob("*"):
        if item.is_file():
            all_files.append(item)

    all_files = sorted(all_files)

    if not all_files:
        print("No files found to consolidate.")
        return

    # Read content from each file
    list_content = []
    for filepath in all_files:
        file_name = filepath.name
        try:
            if filepath.suffix == ".srt":
                content = extract_text_from_srt(filepath)
            else:
                content = filepath.read_text(encoding="utf-8")
            list_content.append((file_name, content))
        except Exception as e:
            print(f"Warning: Could not read {file_name}: {e}")

    # Write consolidated file
    output_path = Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        for filename, content in list_content:
            f.write(f"\n{filename}\n---\n{content}\n\n")

    print(f"✓ Consolidated {len(list_content)} files into {output_path}")

    # Also create a DataFrame for reference
    df = pd.DataFrame(list_content, columns=["FILE_NAME", "CONTENT"])
    df.to_pickle(output_path.with_suffix(".pkl"))
    print(f"✓ Saved DataFrame to {output_path.with_suffix('.pkl')}")


# ============================================================================
# Main Pipeline
# ============================================================================


def process_course_materials(
    source_path: str, exclude_extensions: List[str] = None
) -> None:
    """
    Complete pipeline to process course materials through all stages.

    Args:
        source_path: Path to original course materials
        exclude_extensions: List of file extensions to exclude (default: ['.mp4'])
    """
    if exclude_extensions is None:
        exclude_extensions = [".mp4"]

    print("=" * 70)
    print("STAGE 00: Copying course materials")
    print("=" * 70)
    stage_00 = copy_directory_filtered(
        source_path, "STAGE_00_course_materials", exclude_extensions
    )
    print(f"\n✓ Stage 00 complete: {stage_00}\n")

    print("=" * 70)
    print("STAGE 00.5: Unzipping files with prefix")
    print("=" * 70)
    unzip_with_prefix(stage_00)
    print("\n✓ Stage 00.5 complete\n")

    print("=" * 70)
    print("STAGE 01: Creating working copy and converting PDFs")
    print("=" * 70)
    stage_01 = Path("STAGE_01_course_materials")
    if stage_01.exists():
        shutil.rmtree(stage_01)
    shutil.copytree(stage_00, stage_01)

    # Remove zip files from stage 01
    for zip_file in stage_01.glob("*.zip"):
        zip_file.unlink()

    batch_convert_pdfs(stage_01)
    print(f"\n✓ Stage 01 complete: {stage_01}\n")

    print("=" * 70)
    print("STAGE 02: Converting notebooks to markdown")
    print("=" * 70)
    stage_02 = Path("STAGE_02_course_materials")
    if stage_02.exists():
        shutil.rmtree(stage_02)
    shutil.copytree(stage_01, stage_02)

    convert_notebooks_to_markdown(stage_02)
    print(f"\n✓ Stage 02 complete: {stage_02}\n")

    print("=" * 70)
    print("FINAL: Consolidating all materials")
    print("=" * 70)
    consolidate_course_materials(stage_02, "consolidated_course_materials.txt")
    print("\n✓ Pipeline complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        source = sys.argv[1]
        exclude = sys.argv[2:] if len(sys.argv) > 2 else [".mp4"]
        process_course_materials(source, exclude)
    else:
        print(
            "Usage: python course_materials_processor.py <source_path> [exclude_extensions...]"
        )
        print(
            "Example: python course_materials_processor.py ./course_materials .mp4 .mov"
        )

        # Interactive mode
        source = input("Enter source path of course materials: ").strip()
        if source:
            process_course_materials(source)
