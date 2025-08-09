#!/usr/bin/env node

/**
 * AI Image Viewer - Work Splitter Tool (JavaScript)
 * 
 * This tool splits a source image folder into multiple work packages for collaborative analysis.
 * Each package contains:
 * - All 3 AI Image Viewer HTML files (MobileNet, EfficientNet, MediaPipe)
 * - A subset of images for analysis
 * - Ready-to-share bundle for team collaboration
 * 
 * Author: AI Image Viewer Team
 */

import { Command } from 'commander';
import fs from 'fs-extra';
import path from 'path';
import { glob } from 'glob';
import chalk from 'chalk';

class WorkSplitter {
    constructor(sourceFolder, outputFolder, numSplits) {
        this.sourceFolder = path.resolve(sourceFolder);
        this.outputFolder = path.resolve(outputFolder);
        this.numSplits = numSplits;
        this.supportedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'];
        this.htmlFiles = [
            'ai_image_viewer.html',
            'ai_image_viewer_efficientnet.html',
            'ai_image_viewer_mediapipe.html'
        ];
        this.projectRoot = this.findProjectRoot();
    }

    findProjectRoot() {
        let current = path.dirname(new URL(import.meta.url).pathname);
        while (current !== path.dirname(current)) {
            const hasAllHtml = this.htmlFiles.every(htmlFile => 
                fs.existsSync(path.join(current, htmlFile))
            );
            if (hasAllHtml) {
                return current;
            }
            current = path.dirname(current);
        }
        throw new Error('Could not find project root with HTML files');
    }

    async getImageFiles() {
        const patterns = this.supportedExtensions.flatMap(ext => [
            path.join(this.sourceFolder, `*${ext}`),
            path.join(this.sourceFolder, `*${ext.toUpperCase()}`)
        ]);
        
        const imageFiles = [];
        for (const pattern of patterns) {
            const matches = await glob(pattern);
            imageFiles.push(...matches);
        }
        
        return [...new Set(imageFiles)].sort(); // Remove duplicates and sort
    }

    splitImages(imageFiles) {
        if (imageFiles.length === 0) {
            throw new Error('No image files found in source folder');
        }

        const chunkSize = Math.ceil(imageFiles.length / this.numSplits);
        const chunks = [];

        for (let i = 0; i < this.numSplits; i++) {
            const startIdx = i * chunkSize;
            const endIdx = Math.min((i + 1) * chunkSize, imageFiles.length);
            const chunk = imageFiles.slice(startIdx, endIdx);
            if (chunk.length > 0) {
                chunks.push(chunk);
            }
        }

        return chunks;
    }

    async createWorkPackage(chunkId, imageChunk) {
        const packageName = `work-package-${chunkId.toString().padStart(3, '0')}`;
        const packagePath = path.join(this.outputFolder, packageName);

        // Create package directory
        await fs.ensureDir(packagePath);

        // Copy HTML files
        for (const htmlFile of this.htmlFiles) {
            const srcPath = path.join(this.projectRoot, htmlFile);
            const dstPath = path.join(packagePath, htmlFile);
            if (await fs.pathExists(srcPath)) {
                await fs.copy(srcPath, dstPath);
                console.log(chalk.green(`  ✓ Copied ${htmlFile}`));
            }
        }

        // Copy docs folder if it exists
        const docsSrc = path.join(this.projectRoot, 'docs');
        if (await fs.pathExists(docsSrc)) {
            const docsDst = path.join(packagePath, 'docs');
            await fs.copy(docsSrc, docsDst);
            console.log(chalk.green('  ✓ Copied docs folder'));
        }

        // Create images subfolder and copy images
        const imagesPath = path.join(packagePath, 'images');
        await fs.ensureDir(imagesPath);

        for (const imgFile of imageChunk) {
            const fileName = path.basename(imgFile);
            const dstPath = path.join(imagesPath, fileName);
            await fs.copy(imgFile, dstPath);
        }

        console.log(chalk.green(`  ✓ Copied ${imageChunk.length} images`));

        // Create package manifest
        await this.createManifest(packagePath, chunkId, imageChunk);

        return packagePath;
    }

    async createManifest(packagePath, chunkId, imageChunk) {
        const manifest = {
            package_info: {
                id: chunkId,
                name: `work-package-${chunkId.toString().padStart(3, '0')}`,
                created: new Date().toISOString(),
                total_packages: this.numSplits,
                image_count: imageChunk.length
            },
            html_files: this.htmlFiles,
            images: imageChunk.map(img => path.basename(img)),
            instructions: {
                "1": "Open any of the HTML files in your browser",
                "2": "Load images from the 'images' folder",
                "3": "Click 'AI Analyze' to process your assigned images",
                "4": "Export metadata when analysis is complete",
                "5": "Share the exported JSON file back to the project lead"
            }
        };

        const manifestPath = path.join(packagePath, 'package-manifest.json');
        await fs.writeJSON(manifestPath, manifest, { spaces: 2 });
        console.log(chalk.green('  ✓ Created package manifest'));
    }

    async split() {
        console.log(chalk.cyan(`🔍 Analyzing source folder: ${this.sourceFolder}`));

        // Get all image files
        const imageFiles = await this.getImageFiles();
        if (imageFiles.length === 0) {
            throw new Error(`No image files found in ${this.sourceFolder}`);
        }

        console.log(chalk.blue(`📸 Found ${imageFiles.length} image files`));

        // Split into chunks
        const chunks = this.splitImages(imageFiles);
        const actualSplits = chunks.length;

        if (actualSplits !== this.numSplits) {
            console.log(chalk.yellow(`⚠️  Created ${actualSplits} packages instead of ${this.numSplits} (insufficient images)`));
        }

        console.log(chalk.blue(`📦 Creating ${actualSplits} work packages in: ${this.outputFolder}`));

        // Create output directory
        await fs.ensureDir(this.outputFolder);

        // Create each work package
        const createdPackages = [];
        for (let i = 0; i < chunks.length; i++) {
            const chunk = chunks[i];
            console.log(chalk.blue(`\n📦 Creating package ${i + 1}/${actualSplits}:`));
            const packagePath = await this.createWorkPackage(i + 1, chunk);
            createdPackages.push(packagePath);
            console.log(chalk.green(`   Package: ${path.basename(packagePath)} (${chunk.length} images)`));
        }

        return createdPackages;
    }
}

// CLI Setup
const program = new Command();

program
    .name('split-work')
    .description('🧠 AI Image Viewer - Work Splitter Tool\n\nSplit a source image folder into multiple work packages for team collaboration.')
    .version('1.0.0')
    .requiredOption('-s, --source <directory>', 'Source folder containing images to split')
    .requiredOption('-n, --num-splits <number>', 'Number of work packages to create', parseInt)
    .option('-o, --output <directory>', 'Output folder for work packages (default: ./split/)')
    .addHelpText('after', `
Examples:
  $ node split-work.js -s ./big-dataset -n 5
  $ node split-work.js -s /path/to/images -n 3 -o /path/to/packages
  $ npx split-work -s ./dataset -n 4
`);

program.parse();

const options = program.opts();

// Validation
if (options.numSplits < 1) {
    console.error(chalk.red('❌ Number of splits must be at least 1'));
    process.exit(1);
}

if (options.numSplits > 100) {
    console.error(chalk.red('❌ Number of splits cannot exceed 100 (too many packages)'));
    process.exit(1);
}

if (!await fs.pathExists(options.source)) {
    console.error(chalk.red(`❌ Source folder does not exist: ${options.source}`));
    process.exit(1);
}

// Set default output location
const outputFolder = options.output || path.join(process.cwd(), 'split');

// Main execution
async function main() {
    try {
        console.log(chalk.bold.blue('🧠 AI Image Viewer - Work Splitter Tool'));
        console.log(chalk.blue('=' * 45));

        // Initialize splitter
        const splitter = new WorkSplitter(options.source, outputFolder, options.numSplits);

        // Perform the split
        const packages = await splitter.split();

        console.log(chalk.green(`\n✅ Successfully created ${packages.length} work packages!`));
        console.log(chalk.blue(`📁 Output location: ${outputFolder}`));

        // Show summary
        console.log(chalk.blue('\n📋 Package Summary:'));
        for (const packagePath of packages) {
            const manifestPath = path.join(packagePath, 'package-manifest.json');
            if (await fs.pathExists(manifestPath)) {
                const manifest = await fs.readJSON(manifestPath);
                const imageCount = manifest.package_info.image_count;
                const packageName = path.basename(packagePath);
                console.log(chalk.white(`   ${packageName}: ${imageCount} images`));
            }
        }

        console.log(chalk.green('\n🚀 Next Steps:'));
        console.log(chalk.white('1. Compress each package: tar -czf package.tar.gz work-package-001/'));
        console.log(chalk.white('2. Share packages with team members'));
        console.log(chalk.white('3. Team members analyze their assigned images'));
        console.log(chalk.white('4. Use join-work to merge results when complete'));

    } catch (error) {
        console.error(chalk.red(`❌ Error: ${error.message}`));
        process.exit(1);
    }
}

main();