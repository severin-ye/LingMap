#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch translate Chinese comments to English in Python files
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_translation_mapping() -> Dict[str, str]:
    """Get Chinese to English translation mapping for common terms"""
    return {
        # Class/module descriptions
        "Event extractor base class": "Event extractor base class",
        "Causal linker base class": "Causal linker base class", 
        "Hallucination refiner base class": "Hallucination refiner base class",
        "Graph renderer base class": "Graph renderer base class",
        "Text segmentation tool for splitting chapter text into multiple paragraphs": "Text segmentation tool for splitting chapter text into multiple paragraphs",
        "Load novel chapters from text files and process into standard format": "Load novel chapters from text files and process into standard format",
        "Unified causal linker implementation": "Unified causal linker implementation",
        "Unified causal linker combining original and optimized features": "Unified causal linker combining original and optimized features",
        
        # Method descriptions
        "Initialize extractor": "Initialize extractor",
        "Initialize linker": "Initialize linker", 
        "Initialize refiner": "Initialize refiner",
        "Initialize renderer": "Initialize renderer",
        "Initialize chapter loader": "Initialize chapter loader",
        "Format prompt template": "Format prompt template",
        "Parse LLM response to extract events": "Parse LLM response to extract events",
        "Parse LLM response to extract causal relationships": "Parse LLM response to extract causal relationships",
        "Parse LLM response to update event": "Parse LLM response to update event",
        "Split text by paragraphs (separated by empty lines)": "Split text by paragraphs (separated by empty lines)",
        "Split text by sentences (separated by periods, exclamation marks, question marks)": "Split text by sentences (separated by periods, exclamation marks, question marks)",
        "Split chapter content into segments suitable for LLM processing": "Split chapter content into segments suitable for LLM processing",
        "Extract chapter information (chapter number and title) from text": "Extract chapter information (chapter number and title) from text",
        "Load chapter content from TXT file": "Load chapter content from TXT file",
        "Batch load TXT files": "Batch load TXT files",
        
        # Parameters
        "Prompt template path": "Prompt template path",
        "Text to process": "Text to process",
        "First event": "First event",
        "Second event": "Second event", 
        "Event to be refined": "Event to be refined",
        "Context information supporting refinement": "Context information supporting refinement",
        "Default rendering options": "Default rendering options",
        "Segment size, target character count per segment": "Segment size, target character count per segment",
        "Chapter text": "Chapter text",
        "Target segment length": "Target segment length",
        "Input text": "Input text",
        "TXT file path": "TXT file path",
        "Directory path": "Directory path",
        "File matching pattern": "File matching pattern",
        
        # Return values
        "Formatted prompt dictionary": "Formatted prompt dictionary",
        "List of extracted events": "List of extracted events",
        "Causal edge object, returns None if no causal relationship exists": "Causal edge object, returns None if no causal relationship exists",
        "Refined event": "Refined event",
        "List of paragraphs": "List of paragraphs",
        "List of sentences": "List of sentences",
        "List of segmented chapter fragments, each segment is a dictionary": "List of segmented chapter fragments, each segment is a dictionary",
        "Dictionary containing chapter ID and title, returns None if unable to extract": "Dictionary containing chapter ID and title, returns None if unable to extract",
        "Chapter object, returns None if loading fails": "Chapter object, returns None if loading fails",
        "List of chapter objects": "List of chapter objects",
        
        # Error messages
        "Subclasses must implement this method": "Subclasses must implement this method",
        "File does not exist": "File does not exist",
        "Failed to load chapter": "Failed to load chapter",
        
        # Comments
        "Filter empty paragraphs": "Filter empty paragraphs",
        "Chinese sentence splitting regex": "Chinese sentence splitting regex",
        "Process sentences that may not end with punctuation": "Process sentences that may not end with punctuation",
        "If current paragraph plus existing content would exceed target length and current segment is not empty, save current segment and start new segment": "If current paragraph plus existing content would exceed target length and current segment is not empty, save current segment and start new segment",
        "Process remaining content": "Process remaining content",
        "Optimization parameters, optimization enabled by default": "Optimization parameters, optimization enabled by default",
        
        # App descriptions  
        "Main entry point for GRAPH_BUILDER module": "Main entry point for GRAPH_BUILDER module",
        "Generate causal graph": "Generate causal graph",
        "Input causal relationship JSON file": "Input causal relationship JSON file",
        "Output Mermaid file path": "Output Mermaid file path",
        "Show legend": "Show legend",
        "Show labels on edges": "Show labels on edges",
        "Rendering options": "Rendering options",
        
        # Directory/path related
        "Add project root directory to path": "Add project root directory to path",
        "Add project root directory to Python path": "Add project root directory to Python path",
    }


def find_chinese_text(content: str) -> List[Tuple[str, int, int]]:
    """Find Chinese text in content and return positions"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+[^"\']*')
    matches = []
    
    for match in chinese_pattern.finditer(content):
        start, end = match.span()
        text = match.group()
        # Skip if it's part of a string literal (very basic check)
        before_start = max(0, start - 10)
        context_before = content[before_start:start]
        if '"' in context_before or "'" in context_before:
            # More sophisticated check needed
            pass
        matches.append((text, start, end))
    
    return matches


def translate_content(content: str, translation_map: Dict[str, str]) -> str:
    """Translate Chinese content to English using mapping"""
    result = content
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_translations = sorted(translation_map.items(), key=lambda x: len(x[0]), reverse=True)
    
    for chinese, english in sorted_translations:
        # Use word boundaries and context-aware replacement
        pattern = re.escape(chinese)
        result = re.sub(pattern, english, result)
    
    return result


def process_file(file_path: Path, translation_map: Dict[str, str]) -> bool:
    """Process a single Python file to translate comments"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file contains Chinese
        if not re.search(r'[\u4e00-\u9fff]', content):
            return False
            
        print(f"Processing: {file_path}")
        
        # Translate content
        translated_content = translate_content(content, translation_map)
        
        # Write back if changed
        if translated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            print(f"  ✅ Translated: {file_path}")
            return True
        else:
            print(f"  ⏭️  No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to translate all Python files in the project"""
    print("🌐 Starting batch translation of Chinese comments to English...")
    
    translation_map = get_translation_mapping()
    
    # Find all Python files
    python_files = []
    for pattern in ["**/*.py"]:
        python_files.extend(PROJECT_ROOT.glob(pattern))
    
    print(f"📂 Found {len(python_files)} Python files")
    
    processed_count = 0
    translated_count = 0
    
    for file_path in python_files:
        # Skip certain directories
        skip_dirs = ['.git', '__pycache__', '.pytest_cache', 'venv', 'env']
        if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
            continue
            
        processed_count += 1
        if process_file(file_path, translation_map):
            translated_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  📁 Total files processed: {processed_count}")
    print(f"  🌐 Files translated: {translated_count}")
    print(f"  ✅ Translation completed!")


if __name__ == "__main__":
    main()
