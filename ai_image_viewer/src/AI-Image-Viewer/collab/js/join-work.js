#!/usr/bin/env node

/**
 * AI Image Viewer - Work Joiner Tool (JavaScript)
 * 
 * This tool merges multiple work packages back into a single consolidated package.
 * It combines:
 * - Images from all work packages
 * - AI analysis metadata from all JSON exports
 * - Creates a unified dataset with complete analysis results
 * 
 * Author: AI Image Viewer Team
 */

import { Command } from 'commander';
import fs from 'fs-extra';
import path from 'path';
import { glob } from 'glob';
import chalk from 'chalk';
import tar from 'tar';
import { tmpdir } from 'os';
import { mkdtemp } from 'fs/promises';

class WorkJoiner {
    constructor(packagePaths, outputPath) {
        this.packagePaths = packagePaths.map(p => path.resolve(p));
        this.outputPath = path.resolve(outputPath);
        this.supportedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'];
        this.htmlFiles = [
            'ai_image.html'
        ];
        // Removed metadataPatterns - now using flexible filename detection
        this.projectRoot = this.findProjectRoot();
        this.tempDir = null; // For extracted .tar.gz files
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

    async detectAndExtractArchives() {
        const extractedPaths = [];
        const archiveFiles = [];
        
        for (const inputPath of this.packagePaths) {
            const stats = await fs.stat(inputPath).catch(() => null);
            
            if (stats && stats.isFile() && inputPath.endsWith('.tar.gz')) {
                // This is a .tar.gz file
                archiveFiles.push(inputPath);
            } else if (stats && stats.isDirectory()) {
                // Check if directory contains .tar.gz files
                const gzFiles = await glob(path.join(inputPath, '*.tar.gz'));
                archiveFiles.push(...gzFiles);
                
                // Also check for existing work-package directories
                const workDirs = await glob(path.join(inputPath, 'work-package-*'));
                for (const workDir of workDirs) {
                    if ((await fs.stat(workDir)).isDirectory()) {
                        extractedPaths.push(workDir);
                    }
                }
            } else if (stats && stats.isDirectory()) {
                // Regular directory
                extractedPaths.push(inputPath);
            }
        }
        
        // Extract .tar.gz files if any found
        if (archiveFiles.length > 0) {
            console.log(chalk.cyan(`🗜️  Found ${archiveFiles.length} compressed packages to extract...`));
            
            // Create temporary directory for extraction
            this.tempDir = await mkdtemp(path.join(tmpdir(), 'ai-image-join-'));
            
            for (const archiveFile of archiveFiles) {
                console.log(chalk.blue(`📦 Extracting ${path.basename(archiveFile)}...`));
                
                try {
                    await tar.x({
                        file: archiveFile,
                        cwd: this.tempDir
                    });
                    console.log(chalk.green(`  ✓ Extracted ${path.basename(archiveFile)}`));
                    
                    // Find extracted work-package directories
                    const extractedDirs = await glob(path.join(this.tempDir, 'work-package-*'));
                    for (const extractedDir of extractedDirs) {
                        if ((await fs.stat(extractedDir)).isDirectory()) {
                            extractedPaths.push(extractedDir);
                        }
                    }
                    
                } catch (error) {
                    console.log(chalk.red(`  ❌ Failed to extract ${path.basename(archiveFile)}: ${error.message}`));
                    continue;
                }
            }
        }
        
        return extractedPaths;
    }

    async cleanupTempFiles() {
        if (this.tempDir && await fs.pathExists(this.tempDir)) {
            await fs.remove(this.tempDir);
            console.log(chalk.green('🧹 Cleaned up temporary files'));
        }
    }

    async validatePackages() {
        const validPackages = [];

        for (const packagePath of this.packagePaths) {
            if (!await fs.pathExists(packagePath)) {
                console.log(chalk.yellow(`⚠️  Warning: Package not found: ${packagePath}`));
                continue;
            }

            const stats = await fs.stat(packagePath);
            if (!stats.isDirectory()) {
                if (path.extname(packagePath) === '.gz' || path.extname(packagePath) === '.zip') {
                    console.log(chalk.blue(`📦 Found compressed package: ${path.basename(packagePath)}`));
                    // TODO: Add extraction logic if needed
                    continue;
                } else {
                    console.log(chalk.yellow(`⚠️  Warning: Expected folder, got file: ${packagePath}`));
                    continue;
                }
            }

            // Check if it's a valid package directory
            const imagesPath = path.join(packagePath, 'images');
            if (!await fs.pathExists(imagesPath)) {
                console.log(chalk.yellow(`⚠️  Warning: No images folder in: ${path.basename(packagePath)}`));
                continue;
            }

            validPackages.push(packagePath);
            console.log(chalk.green(`✓ Valid package: ${path.basename(packagePath)}`));
        }

        return validPackages;
    }

    async collectImages(packages) {
        const allImages = [];
        const seenNames = new Set();

        for (const packagePath of packages) {
            const imagesPath = path.join(packagePath, 'images');
            if (!await fs.pathExists(imagesPath)) {
                continue;
            }

            const patterns = this.supportedExtensions.flatMap(ext => [
                path.join(imagesPath, `*${ext}`),
                path.join(imagesPath, `*${ext.toUpperCase()}`)
            ]);

            const packageImages = [];
            for (const pattern of patterns) {
                const matches = await glob(pattern);
                packageImages.push(...matches);
            }

            console.log(chalk.blue(`📸 Package ${path.basename(packagePath)}: ${packageImages.length} images`));

            for (const imgPath of packageImages) {
                const originalName = path.basename(imgPath);
                if (seenNames.has(originalName)) {
                    // Skip duplicates - first survives
                    console.log(chalk.yellow(`  ⚠️  Skipping duplicate image: ${originalName} (first survives)`));
                    continue;
                } else {
                    allImages.push(imgPath);
                    seenNames.add(originalName);
                }
            }
        }

        return allImages;
    }

    async findMetadataFiles(packages) {
        const metadataFiles = [];

        for (const packagePath of packages) {
            const foundInPackage = [];

            // Find all .json files in the package
            const jsonFiles = await glob(path.join(packagePath, '*.json'));

            // Filter for files containing "metadata" (case-insensitive)
            for (const jsonFile of jsonFiles) {
                const filename = path.basename(jsonFile).toLowerCase();
                if (filename.includes('metadata')) {
                    // Exclude package-manifest.json (not analysis data)
                    if (path.basename(jsonFile) !== 'package-manifest.json') {
                        foundInPackage.push(jsonFile);
                    }
                }
            }

            if (foundInPackage.length > 0) {
                console.log(chalk.blue(`📊 Package ${path.basename(packagePath)}: ${foundInPackage.length} metadata files`));
                for (const metaFile of foundInPackage) {
                    console.log(chalk.white(`  - ${path.basename(metaFile)}`));
                }
                metadataFiles.push(...foundInPackage);
            } else {
                console.log(chalk.yellow(`⚠️  Package ${path.basename(packagePath)}: No metadata files found`));
            }
        }

        return metadataFiles;
    }

    async mergeMetadata(metadataFiles) {
        const merged = {
            version: '2.0-Consolidated',
            timestamp: new Date().toISOString(),
            appName: 'AI Image Viewer - Consolidated Results',
            consolidation_info: {
                source_files: metadataFiles.map(f => path.basename(f)),
                packages_merged: new Set(metadataFiles.map(f => path.basename(path.dirname(f)))).size,
                merge_date: new Date().toISOString(),
                models_used: [],
                total_analyzed_images: 0
            },
            totalImages: 0,
            aiEnabled: true,
            captions: {},
            aiData: {}
        };

        let imageCount = 0;
        const modelsUsed = new Set();

        for (const metaFile of metadataFiles) {
            try {
                const data = await fs.readJSON(metaFile);
                const packageName = path.basename(path.dirname(metaFile));
                
                console.log(chalk.blue(`📋 Processing: ${path.basename(metaFile)}`));

                // Merge captions - first survives for duplicates
                if (data.captions) {
                    for (const [imgName, caption] of Object.entries(data.captions)) {
                        if (!merged.captions[imgName]) {
                            merged.captions[imgName] = caption;
                        }
                        // Skip if duplicate - first survives
                    }
                }

                // Merge AI data - first survives for duplicates
                if (data.aiData) {
                    for (const [imgName, aiData] of Object.entries(data.aiData)) {
                        if (!merged.aiData[imgName]) {
                            merged.aiData[imgName] = aiData;
                        }
                        // Skip if duplicate - first survives

                        // Track models used
                        if (aiData.modelUsed) {
                            modelsUsed.add(aiData.modelUsed);
                        }
                    }
                }

                // Count images
                if (data.totalImages) {
                    imageCount += data.totalImages;
                }

            } catch (error) {
                if (error.name === 'SyntaxError') {
                    console.log(chalk.red(`❌ Error parsing ${path.basename(metaFile)}: ${error.message}`));
                } else {
                    console.log(chalk.yellow(`⚠️  Warning processing ${path.basename(metaFile)}: ${error.message}`));
                }
                continue;
            }
        }

        merged.totalImages = imageCount;
        merged.consolidation_info.models_used = [...modelsUsed];
        merged.consolidation_info.total_analyzed_images = Object.keys(merged.aiData).length;

        return merged;
    }

    async createConsolidatedPackage(images, metadata) {
        console.log(chalk.blue(`📦 Creating consolidated package: ${this.outputPath}`));

        // Create output directory
        await fs.ensureDir(this.outputPath);

        // Copy HTML files from project root
        for (const htmlFile of this.htmlFiles) {
            const srcPath = path.join(this.projectRoot, htmlFile);
            const dstPath = path.join(this.outputPath, htmlFile);
            if (await fs.pathExists(srcPath)) {
                await fs.copy(srcPath, dstPath);
                console.log(chalk.green(`✓ Copied ${htmlFile}`));
            }
        }

        // Copy docs folder if it exists
        const docsSrc = path.join(this.projectRoot, 'docs');
        if (await fs.pathExists(docsSrc)) {
            const docsDst = path.join(this.outputPath, 'docs');
            await fs.copy(docsSrc, docsDst);
            console.log(chalk.green('✓ Copied docs folder'));
        }

        // Create images folder and copy all images
        const imagesDst = path.join(this.outputPath, 'images');
        await fs.ensureDir(imagesDst);

        let copiedCount = 0;
        for (const imgPath of images) {
            const dstPath = path.join(imagesDst, path.basename(imgPath));
            await fs.copy(imgPath, dstPath);
            copiedCount++;
        }

        console.log(chalk.green(`✓ Copied ${copiedCount} images`));

        // Save consolidated metadata
        const metadataPath = path.join(this.outputPath, 'consolidated-metadata.json');
        await fs.writeJSON(metadataPath, metadata, { spaces: 2 });
        console.log(chalk.green('✓ Created consolidated metadata'));

        // Create summary report
        await this.createSummaryReport(metadata);

        return this.outputPath;
    }

    async createSummaryReport(metadata) {
        const reportPath = path.join(this.outputPath, 'consolidation-report.txt');
        
        const reportLines = [
            '🧠 AI Image Viewer - Consolidation Report',
            '='.repeat(50),
            '',
            `Consolidation Date: ${metadata.consolidation_info.merge_date}`,
            `Packages Merged: ${metadata.consolidation_info.packages_merged}`,
            `Source Files: ${metadata.consolidation_info.source_files.length}`,
            `Total Images: ${metadata.totalImages}`,
            `Analyzed Images: ${metadata.consolidation_info.total_analyzed_images}`,
            `Analysis Coverage: ${(metadata.consolidation_info.total_analyzed_images / metadata.totalImages * 100).toFixed(1)}%`,
            ''
        ];

        if (metadata.consolidation_info.models_used.length > 0) {
            reportLines.push('AI Models Used:');
            for (const model of metadata.consolidation_info.models_used) {
                reportLines.push(`  - ${model}`);
            }
            reportLines.push('');
        }

        reportLines.push('Source Metadata Files:');
        for (const sourceFile of metadata.consolidation_info.source_files) {
            reportLines.push(`  - ${sourceFile}`);
        }

        await fs.writeFile(reportPath, reportLines.join('\n'));
        console.log(chalk.green('✓ Created consolidation report'));
    }

    async join() {
        try {
            console.log(chalk.cyan(`🔍 Processing ${this.packagePaths.length} input paths...`));

            // Detect and extract .tar.gz files
            const extractedPaths = await this.detectAndExtractArchives();
            
            // Update package paths with extracted directories
            this.packagePaths = extractedPaths;

            console.log(chalk.cyan(`🔍 Validating ${this.packagePaths.length} packages...`));

            // Validate packages
            const validPackages = await this.validatePackages();
            if (validPackages.length === 0) {
                throw new Error('No valid packages found to merge');
            }

            console.log(chalk.green(`✓ Found ${validPackages.length} valid packages`));

            // Collect all images
            console.log(chalk.cyan('\n📸 Collecting images from packages...'));
            const allImages = await this.collectImages(validPackages);
            console.log(chalk.green(`✓ Collected ${allImages.length} total images`));

            // Find and merge metadata
            console.log(chalk.cyan('\n📊 Processing metadata files...'));
            const metadataFiles = await this.findMetadataFiles(validPackages);

            let mergedMetadata;
            if (metadataFiles.length === 0) {
                console.log(chalk.yellow('⚠️  No metadata files found. Creating package with images only.'));
                mergedMetadata = {
                    version: '2.0-Consolidated',
                    timestamp: new Date().toISOString(),
                    appName: 'AI Image Viewer - Consolidated Results',
                    consolidation_info: {
                        source_files: [],
                        packages_merged: validPackages.length,
                        merge_date: new Date().toISOString(),
                        models_used: [],
                        total_analyzed_images: 0
                    },
                    totalImages: allImages.length,
                    aiEnabled: false,
                    captions: {},
                    aiData: {}
                };
            } else {
                mergedMetadata = await this.mergeMetadata(metadataFiles);
            }

            // Create consolidated package
            console.log(chalk.cyan('\n📦 Creating consolidated package...'));
            const outputPath = await this.createConsolidatedPackage(allImages, mergedMetadata);

            return outputPath;
        } finally {
            // Clean up temporary files
            await this.cleanupTempFiles();
        }
    }
}

// CLI Setup
const program = new Command();

program
    .name('join-work')
    .description('🧠 AI Image Viewer - Work Joiner Tool\n\nMerge multiple work packages into a single consolidated package.')
    .version('1.0.0')
    .argument('<packages...>', 'Work package directories to merge')
    .option('-o, --output <directory>', 'Output folder for consolidated package (default: ./join/consolidated)')
    .option('-f, --force', 'Force overwrite existing output directory')
    .addHelpText('after', `
Examples:
  $ node join-work.js ../split/work-package-*
  $ node join-work.js package1/ package2/ package3/ -o final-results/
  $ npx join-work ../split/* -f
`);

program.parse();

const packages = program.args;
const options = program.opts();

// Validation
if (packages.length < 1) {
    console.error(chalk.red('❌ At least one package must be specified'));
    process.exit(1);
}

// Set default output location
const outputPath = options.output || path.join(process.cwd(), 'join', 'consolidated');

// Main execution
async function main() {
    try {
        // Check if output exists
        if (await fs.pathExists(outputPath) && !options.force) {
            console.log(chalk.yellow(`Output directory ${outputPath} exists.`));
            // In a real CLI, you'd want to prompt for user input
            // For now, we'll just remove it
            await fs.remove(outputPath);
        } else if (await fs.pathExists(outputPath) && options.force) {
            await fs.remove(outputPath);
        }

        console.log(chalk.bold.blue('🧠 AI Image Viewer - Work Joiner Tool'));
        console.log(chalk.blue('='.repeat(43)));

        // Initialize joiner
        const joiner = new WorkJoiner(packages, outputPath);

        // Perform the join
        const resultPath = await joiner.join();

        console.log(chalk.green('\n✅ Successfully created consolidated package!'));
        console.log(chalk.blue(`📁 Output location: ${resultPath}`));

        // Show final summary
        const metadataPath = path.join(resultPath, 'consolidated-metadata.json');
        if (await fs.pathExists(metadataPath)) {
            const metadata = await fs.readJSON(metadataPath);

            console.log(chalk.blue('\n📋 Final Summary:'));
            console.log(chalk.white(`   Total Images: ${metadata.totalImages}`));
            console.log(chalk.white(`   Analyzed Images: ${metadata.consolidation_info?.total_analyzed_images || 0}`));
            console.log(chalk.white(`   Packages Merged: ${packages.length}`));

            const models = metadata.consolidation_info?.models_used || [];
            console.log(chalk.white(`   AI Models Used: ${models.length > 0 ? models.join(', ') : 'None'}`));
        }

        console.log(chalk.green('\n🚀 Next Steps:'));
        console.log(chalk.white('1. Open any HTML file in the consolidated package'));
        console.log(chalk.white('2. Import \'consolidated-metadata.json\' to see all analysis results'));
        console.log(chalk.white('3. Review \'consolidation-report.txt\' for detailed statistics'));

    } catch (error) {
        console.error(chalk.red(`❌ Error: ${error.message}`));
        process.exit(1);
    }
}

main();