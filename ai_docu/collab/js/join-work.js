#!/usr/bin/env node
/**
 * AI Docu App - Document Joiner Tool (JavaScript)
 * 
 * This tool merges analysis results from multiple work packages back into a unified dataset.
 * It combines:
 * - Multiple metadata JSON files from different team members
 * - Document analysis results from various AI models
 * - Consolidated output for project leads
 * 
 * Author: AI Docu App Team
 */

const fs = require('fs').promises;
const path = require('path');
const { program } = require('commander');
const AdmZip = require('adm-zip');

class DocumentJoiner {
    constructor(inputFolder, outputFolder) {
        this.inputFolder = path.resolve(inputFolder);
        this.outputFolder = path.resolve(outputFolder);
        this.supportedMetadataPatterns = [
            'ai-docu-sentencebert-metadata.json',
            'ai-docu-distilbert-metadata.json',
            'ai-docu-universal-metadata.json',
            'ai-docu-metadata.json'
        ];
        this.processedFiles = new Set();
        this.mergedData = {};
    }

    async extractCompressedPackages() {
        const extractedPaths = [];
        
        try {
            const files = await fs.readdir(this.inputFolder);
            const archiveFiles = files.filter(file => 
                file.endsWith('.zip') || file.endsWith('.tar.gz')
            );
            
            if (archiveFiles.length > 0) {
                console.log(`🗜️  Found ${archiveFiles.length} compressed packages to extract`);
                
                for (const archiveFile of archiveFiles) {
                    console.log(`   Extracting ${archiveFile}...`);
                    
                    try {
                        const archivePath = path.join(this.inputFolder, archiveFile);
                        
                        if (archiveFile.endsWith('.zip')) {
                            const zip = new AdmZip(archivePath);
                            zip.extractAllTo(this.inputFolder, true);
                            
                            // Find the extracted folder
                            const packageName = path.basename(archiveFile, '.zip');
                            const extractedPath = path.join(this.inputFolder, packageName);
                            
                            if (await this.pathExists(extractedPath)) {
                                extractedPaths.push(extractedPath);
                                console.log(`   ✓ Extracted to ${packageName}/`);
                            }
                        } else {
                            // For .tar.gz files, suggest using system tools
                            console.log(`   ⚠️  .tar.gz extraction requires system tools`);
                            console.log(`   Run: tar -xzf ${archiveFile} -C ${this.inputFolder}`);
                        }
                        
                    } catch (error) {
                        console.log(`   ❌ Error extracting ${archiveFile}: ${error.message}`);
                    }
                }
            }
        } catch (error) {
            console.log(`Warning: Could not read input folder: ${error.message}`);
        }
        
        return extractedPaths;
    }

    async pathExists(filePath) {
        try {
            await fs.access(filePath);
            return true;
        } catch {
            return false;
        }
    }

    async findPackageDirectories() {
        const packageDirs = [];
        
        try {
            const items = await fs.readdir(this.inputFolder);
            
            for (const item of items) {
                const itemPath = path.join(this.inputFolder, item);
                const stats = await fs.stat(itemPath);
                
                if (stats.isDirectory()) {
                    const isPackage = item.startsWith('docu-package-') ||
                                    item.toLowerCase().includes('package') ||
                                    await this.hasMetadataFiles(itemPath);
                    
                    if (isPackage) {
                        packageDirs.push(itemPath);
                    }
                }
            }
        } catch (error) {
            throw new Error(`Error reading input folder: ${error.message}`);
        }
        
        return packageDirs.sort();
    }

    async hasMetadataFiles(directory) {
        for (const pattern of this.supportedMetadataPatterns) {
            if (await this.pathExists(path.join(directory, pattern))) {
                return true;
            }
        }
        return false;
    }

    async findMetadataFiles(packageDir) {
        const metadataFiles = [];
        
        for (const pattern of this.supportedMetadataPatterns) {
            const metadataFile = path.join(packageDir, pattern);
            if (await this.pathExists(metadataFile)) {
                metadataFiles.push(metadataFile);
            }
        }
        
        return metadataFiles;
    }

    async loadMetadataFile(metadataFile) {
        try {
            const content = await fs.readFile(metadataFile, 'utf8');
            const data = JSON.parse(content);
            
            // Validate structure
            if (typeof data !== 'object' || data === null) {
                throw new Error('Metadata must be a JSON object');
            }
            
            if (!data.metadata) {
                throw new Error('Missing "metadata" key in JSON');
            }
            
            return data;
            
        } catch (error) {
            if (error.name === 'SyntaxError') {
                throw new Error(`Invalid JSON format: ${error.message}`);
            }
            throw new Error(`Error reading file: ${error.message}`);
        }
    }

    mergeMetadata(allMetadata) {
        if (allMetadata.length === 0) {
            return {};
        }
        
        // Start with the base structure
        const merged = {
            metadata: {},
            export_info: {
                timestamp: new Date().toISOString(),
                source: 'AI Docu App - Document Joiner',
                merged_packages: allMetadata.length,
                total_documents: 0,
                ai_models_used: new Set()
            }
        };
        
        // Merge all document metadata
        for (const metadataDict of allMetadata) {
            if (metadataDict.metadata) {
                Object.assign(merged.metadata, metadataDict.metadata);
            }
            
            // Collect export info
            if (metadataDict.export_info && metadataDict.export_info.ai_model) {
                merged.export_info.ai_models_used.add(metadataDict.export_info.ai_model);
            }
        }
        
        // Convert set to array for JSON serialization
        merged.export_info.ai_models_used = Array.from(merged.export_info.ai_models_used);
        merged.export_info.total_documents = Object.keys(merged.metadata).length;
        
        return merged;
    }

    createSummaryReport(mergedData, packageDirs) {
        const now = new Date();
        const report = `# AI Docu App - Document Analysis Summary Report

## 📊 Merge Summary

**Generated:** ${now.toLocaleString()}  
**Source Packages:** ${packageDirs.length}  
**Total Documents:** ${Object.keys(mergedData.metadata || {}).length}  
**AI Models Used:** ${mergedData.export_info.ai_models_used.join(', ')}

## 📦 Source Packages

`;
        
        let packageInfo = '';
        packageDirs.forEach((packageDir, i) => {
            const packageName = path.basename(packageDir);
            packageInfo += `${i + 1}. **${packageName}**\n`;
            packageInfo += `   - Status: Processed\n`;
            packageInfo += `   - Location: ${packageDir}\n\n`;
        });
        
        const analysisOverview = this.createAnalysisOverview(mergedData);
        
        const nextSteps = `
## 🚀 Next Steps

1. **Review Results**: Open the merged metadata JSON file to review all analysis
2. **Import to AI Docu App**: Load the consolidated results back into the main application
3. **Quality Check**: Verify that all expected documents are included
4. **Archive Packages**: Clean up individual work packages if no longer needed

## 📁 Output Files

- \`merged-ai-docu-metadata.json\` - Consolidated analysis results
- \`join-summary-report.md\` - This summary report
- \`package-manifest.json\` - Details about the merge process

---

*Report generated by AI Docu App Document Joiner v1.0.0*
`;
        
        return report + packageInfo + analysisOverview + nextSteps;
    }

    createAnalysisOverview(mergedData) {
        if (!mergedData.metadata || Object.keys(mergedData.metadata).length === 0) {
            return '\n## 📄 Document Analysis Overview\n\nNo document metadata found.\n';
        }
        
        let overview = '\n## 📄 Document Analysis Overview\n\n';
        
        // Count by file type
        const fileTypes = {};
        let hasSummaries = 0;
        let hasKeywords = 0;
        
        Object.entries(mergedData.metadata).forEach(([filename, docData]) => {
            // Extract file extension
            const ext = path.extname(filename).toLowerCase() || 'no extension';
            fileTypes[ext] = (fileTypes[ext] || 0) + 1;
            
            if (docData.summary) {
                hasSummaries++;
            }
            if (docData.keywords) {
                hasKeywords++;
            }
        });
        
        overview += '### File Types\n';
        Object.entries(fileTypes)
            .sort(([a], [b]) => a.localeCompare(b))
            .forEach(([ext, count]) => {
                overview += `- **${ext}**: ${count} files\n`;
            });
        
        const totalDocs = Object.keys(mergedData.metadata).length;
        overview += `\n### Analysis Coverage\n`;
        overview += `- Documents with summaries: ${hasSummaries}/${totalDocs} (${(hasSummaries/totalDocs*100).toFixed(1)}%)\n`;
        overview += `- Documents with keywords: ${hasKeywords}/${totalDocs} (${(hasKeywords/totalDocs*100).toFixed(1)}%)\n`;
        
        return overview;
    }

    async join() {
        console.log(`🔍 Analyzing input folder: ${this.inputFolder}`);
        
        // Extract any compressed packages first
        const extractedPaths = await this.extractCompressedPackages();
        if (extractedPaths.length > 0) {
            console.log(`✓ Extracted ${extractedPaths.length} compressed packages`);
        }
        
        // Find all package directories
        const packageDirs = await this.findPackageDirectories();
        if (packageDirs.length === 0) {
            throw new Error(`No package directories found in ${this.inputFolder}`);
        }
        
        console.log(`📦 Found ${packageDirs.length} package directories`);
        
        // Collect all metadata files
        const allMetadata = [];
        let totalDocuments = 0;
        
        for (const packageDir of packageDirs) {
            console.log(`\n📄 Processing package: ${path.basename(packageDir)}`);
            
            const metadataFiles = await this.findMetadataFiles(packageDir);
            if (metadataFiles.length === 0) {
                console.log(`   ⚠️  No metadata files found, skipping`);
                continue;
            }
            
            console.log(`   Found ${metadataFiles.length} metadata files`);
            
            // Process each metadata file
            for (const metadataFile of metadataFiles) {
                try {
                    console.log(`   Loading ${path.basename(metadataFile)}...`);
                    const metadataDict = await this.loadMetadataFile(metadataFile);
                    
                    const docCount = Object.keys(metadataDict.metadata || {}).length;
                    allMetadata.push(metadataDict);
                    totalDocuments += docCount;
                    
                    console.log(`   ✓ Loaded ${docCount} documents`);
                    
                } catch (error) {
                    console.log(`   ❌ Error loading ${path.basename(metadataFile)}: ${error.message}`);
                }
            }
        }
        
        if (allMetadata.length === 0) {
            throw new Error('No valid metadata files found to merge');
        }
        
        console.log(`\n🔄 Merging ${allMetadata.length} metadata files...`);
        console.log(`📊 Total documents to merge: ${totalDocuments}`);
        
        // Merge all metadata
        const mergedData = this.mergeMetadata(allMetadata);
        
        // Create output directory
        await fs.mkdir(this.outputFolder, { recursive: true });
        
        // Save merged metadata
        const outputFile = path.join(this.outputFolder, 'merged-ai-docu-metadata.json');
        await fs.writeFile(outputFile, JSON.stringify(mergedData, null, 2), 'utf8');
        console.log(`✓ Saved merged metadata: ${outputFile}`);
        
        // Create summary report
        const summaryReport = this.createSummaryReport(mergedData, packageDirs);
        const reportFile = path.join(this.outputFolder, 'join-summary-report.md');
        await fs.writeFile(reportFile, summaryReport, 'utf8');
        console.log(`✓ Created summary report: ${reportFile}`);
        
        // Create package manifest
        const manifest = {
            join_info: {
                timestamp: new Date().toISOString(),
                source_packages: packageDirs,
                total_metadata_files: allMetadata.length,
                total_documents: Object.keys(mergedData.metadata).length,
                ai_models_used: mergedData.export_info.ai_models_used
            },
            output_files: [
                'merged-ai-docu-metadata.json',
                'join-summary-report.md',
                'package-manifest.json'
            ]
        };
        
        const manifestFile = path.join(this.outputFolder, 'package-manifest.json');
        await fs.writeFile(manifestFile, JSON.stringify(manifest, null, 2), 'utf8');
        console.log(`✓ Created package manifest: ${manifestFile}`);
        
        return mergedData;
    }
}

// CLI setup
program
    .name('join-work')
    .description('📄 AI Docu App - Document Joiner Tool')
    .version('1.0.0')
    .requiredOption('-i, --input <folder>', 'Input folder containing completed work packages')
    .option('-o, --output <folder>', 'Output folder for merged results (default: ./joined/)')
    .option('-c, --clean-extracted', 'Clean up extracted package folders after processing')
    .action(async (options) => {
        try {
            const outputFolder = options.output || path.join(__dirname, 'joined');
            
            console.log('📄 AI Docu App - Document Joiner Tool');
            console.log('='.repeat(42));
            
            // Initialize joiner
            const joiner = new DocumentJoiner(options.input, outputFolder);
            
            // Perform the join
            const mergedData = await joiner.join();
            
            console.log(`\n✅ Successfully merged document analysis results!`);
            console.log(`📁 Output location: ${outputFolder}`);
            console.log(`📊 Total documents: ${Object.keys(mergedData.metadata || {}).length}`);
            console.log(`🤖 AI models used: ${mergedData.export_info.ai_models_used.join(', ')}`);
            
            console.log(`\n🚀 Next Steps:`);
            console.log(`1. Review: Open join-summary-report.md for detailed analysis`);
            console.log(`2. Import: Load merged-ai-docu-metadata.json into AI Docu App`);
            console.log(`3. Verify: Check that all expected documents are included`);
            
            if (options.cleanExtracted) {
                console.log(`4. Cleanup: Removing extracted package directories...`);
                // Clean up extracted directories
                const items = await fs.readdir(options.input);
                for (const item of items) {
                    const itemPath = path.join(options.input, item);
                    const stats = await fs.stat(itemPath);
                    if (stats.isDirectory() && item.startsWith('docu-package-')) {
                        await fs.rmdir(itemPath, { recursive: true });
                        console.log(`   ✓ Removed ${item}`);
                    }
                }
            }
            
        } catch (error) {
            console.error(`❌ Error: ${error.message}`);
            process.exit(1);
        }
    });

program.parse();