#!/bin/bash

# AI Image Viewer - Package Compression Script
# Compresses all work-package-<nnn> folders into .tar.gz files

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

printf "${BLUE}🗜️  AI Image Viewer - Package Compression Script${NC}\n"
printf "${BLUE}================================================${NC}\n"

# Check if any packages exist
if ! ls work-package-[0-9][0-9][0-9] >/dev/null 2>&1; then
    printf "${RED}❌ No work-package directories found in current directory${NC}\n"
    printf "${YELLOW}💡 Make sure you're in the directory containing work-package-001, work-package-002, etc.${NC}\n"
    exit 1
fi

# Count packages
package_count=$(ls -d work-package-[0-9][0-9][0-9] 2>/dev/null | wc -l)
printf "${BLUE}🔍 Found $package_count work packages to compress...${NC}\n"

compressed_count=0
skipped_count=0

for package_dir in work-package-[0-9][0-9][0-9]; do
    # Skip if it's not actually a directory (glob didn't match)
    if [ ! -d "$package_dir" ]; then
        continue
    fi
    
    package_name=$(basename "$package_dir")
    tar_file="${package_name}.tar.gz"
    
    # Check if tar.gz already exists
    if [ -f "$tar_file" ]; then
        printf "${YELLOW}⚠️  Skipping $package_name (${tar_file} already exists)${NC}\n"
        skipped_count=$((skipped_count + 1))
        continue
    fi
    
    printf "${BLUE}📦 Compressing $package_name...${NC}\n"
    
    # Create tar.gz file
    if tar -czf "$tar_file" "$package_dir"; then
        # Get file size for display
        size=$(du -h "$tar_file" | cut -f1)
        printf "${GREEN}✓ Created ${tar_file} (${size})${NC}\n"
        compressed_count=$((compressed_count + 1))
    else
        printf "${RED}❌ Failed to compress $package_name${NC}\n"
        exit 1
    fi
done

printf "\n${GREEN}🎉 Compression complete!${NC}\n"
printf "${GREEN}   Compressed: $compressed_count packages${NC}\n"

if [ $skipped_count -gt 0 ]; then
    printf "${YELLOW}   Skipped: $skipped_count packages (already existed)${NC}\n"
fi

printf "\n${BLUE}📋 Files created:${NC}\n"
for tar_file in work-package-*.tar.gz; do
    if [ -f "$tar_file" ]; then
        size=$(du -h "$tar_file" | cut -f1)
        printf "${GREEN}   - $tar_file (${size})${NC}\n"
    fi
done

printf "\n${BLUE}🚀 Next Steps:${NC}\n"
printf "1. Share .tar.gz files with team members\n"
printf "2. Team members extract: ${YELLOW}tar -xzf work-package-001.tar.gz${NC}\n"
printf "3. Team members analyze images and export metadata\n"
printf "4. Use join tools to merge completed work packages\n"

printf "\n${GREEN}✨ Ready for team collaboration! ✨${NC}\n"