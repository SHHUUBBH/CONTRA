#!/usr/bin/env python
"""
Script to update existing image metadata files to include topic_id.
This helps ensure that existing images will work with the new topic-based filtering.
"""

import os
import json
import time
import logging
from pathlib import Path
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_metadata_files():
    """Update existing metadata files to include topic_id."""
    # Path to the image cache directory
    cache_dir = Path("cache/images")
    
    if not cache_dir.exists():
        logger.error(f"Cache directory {cache_dir} does not exist.")
        return
    
    # Find all JSON metadata files
    metadata_files = list(cache_dir.glob("*.json"))
    logger.info(f"Found {len(metadata_files)} metadata files to process.")
    
    updated_count = 0
    for meta_file in metadata_files:
        try:
            # Read the metadata
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            
            # Skip if topic_id already exists
            if "topic_id" in metadata and metadata["topic_id"]:
                continue
            
            # Create a topic_id from the filename
            filename = meta_file.stem
            
            # Extract topic from prompt if available
            topic = ""
            if "prompt" in metadata:
                # Use the first part of the prompt as the topic
                prompt_parts = metadata["prompt"].split(",")
                if prompt_parts:
                    topic = prompt_parts[0].strip()
            
            # If no topic could be extracted, use a placeholder
            if not topic:
                topic = "unknown_topic"
            
            # Create a unique topic_id
            topic_id = re.sub(r'[^a-zA-Z0-9]', '_', topic.lower())
            topic_id = f"topic_{topic_id}_{int(time.time())}"
            
            # Update the metadata
            metadata["topic_id"] = topic_id
            
            # Write the updated metadata
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update the PNG file if it exists
            png_file = meta_file.with_suffix(".png")
            if png_file.exists():
                logger.info(f"Updated metadata for {png_file.name} with topic_id: {topic_id}")
            
            updated_count += 1
            
        except Exception as e:
            logger.error(f"Error updating metadata for {meta_file}: {e}")
    
    logger.info(f"Updated {updated_count} metadata files with topic_id.")

def main():
    """Main function to update the metadata files."""
    print("\n===== UPDATING IMAGE METADATA =====\n")
    
    print("Adding topic_id to existing image metadata...")
    update_metadata_files()
    
    print("\n===== UPDATE COMPLETED =====")
    print("\nImage metadata has been updated to include topic_id.")
    print("This enables filtering images by topic for better user experience.")
    print("\nPlease restart your application with:")
    print("python run.py")

if __name__ == "__main__":
    main() 