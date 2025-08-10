#!/usr/bin/env node
/**
 * AI Docu App - Document Splitter Tool (JavaScript)
 * 
 * This tool splits a source document folder into multiple work packages for collaborative analysis.
 * Each package contains:
 * - AI Docu App HTML file
 * - A subset of documents for analysis  
 * - Ready-to-share bundle for team collaboration
 * 
 * Author: AI Docu App Team
 */

const fs = require('fs').promises;
const path = require('path');
const { program } = require('commander');
const archiver = require('archiver');
const { createWriteStream } = require('fs');

class DocumentSplitter {
    constructor(sourceFolder, outputFolder, numSplits) {
        this.sourceFolder = path.resolve(sourceFolder);
        this.outputFolder = path.resolve(outputFolder);
        this.numSplits = numSplits;
        this.supportedExtensions = new Set(['.txt', '.pdf', '.docx', '.rtf', '.md']);
        this.htmlFiles = ['ai_docu.html'];
    }

    async findProjectRoot() {
        let current = path.dirname(__filename);
        while (current !== path.dirname(current)) {
            const hasAllHtml = await Promise.all(
                this.htmlFiles.map(file => 
                    fs.access(path.join(current, file))
                        .then(() => true)
                        .catch(() => false)
                )
            );
            
            if (hasAllHtml.every(exists => exists)) {
                return current;
            }
            current = path.dirname(current);
        }
        throw new Error('Could not find project root with HTML files');
    }

    async getDocumentFiles() {
        const documentFiles = [];
        
        try {
            const files = await fs.readdir(this.sourceFolder);
            
            for (const file of files) {
                const filePath = path.join(this.sourceFolder, file);
                const stats = await fs.stat(filePath);
                
                if (stats.isFile()) {
                    const ext = path.extname(file).toLowerCase();
                    if (this.supportedExtensions.has(ext)) {
                        documentFiles.push(filePath);
                    }
                }
            }
        } catch (error) {
            throw new Error(`Error reading source folder: ${error.message}`);
        }
        
        return documentFiles.sort();
    }

    splitDocuments(documentFiles) {
        if (documentFiles.length === 0) {
            throw new Error('No document files found in source folder');
        }
        
        const chunkSize = Math.ceil(documentFiles.length / this.numSplits);
        const chunks = [];
        
        for (let i = 0; i < this.numSplits; i++) {
            const startIdx = i * chunkSize;
            const endIdx = Math.min((i + 1) * chunkSize, documentFiles.length);
            const chunk = documentFiles.slice(startIdx, endIdx);
            
            if (chunk.length > 0) {
                chunks.push(chunk);
            }
        }
        
        return chunks;
    }

    async createWorkPackage(chunkId, documentChunk) {
        const packageName = `docu-package-${chunkId.toString().padStart(3, '0')}`;
        const packagePath = path.join(this.outputFolder, packageName);
        
        // Create package directory
        await fs.mkdir(packagePath, { recursive: true });
        
        const projectRoot = await this.findProjectRoot();
        
        // Copy HTML files
        for (const htmlFile of this.htmlFiles) {
            const srcPath = path.join(projectRoot, htmlFile);
            const dstPath = path.join(packagePath, htmlFile);
            await fs.copyFile(srcPath, dstPath);
            console.log(`  ✓ Copied ${htmlFile}`);
        }
        
        // Copy docs folder if it exists
        const docsSrc = path.join(projectRoot, 'docs');
        try {
            await fs.access(docsSrc);
            const docsDst = path.join(packagePath, 'docs');
            await this.copyDirectory(docsSrc, docsDst);
            console.log(`  ✓ Copied docs folder`);
        } catch (error) {
            // docs folder doesn't exist, skip
        }
        
        // Create documents subfolder and copy documents
        const documentsPath = path.join(packagePath, 'documents');
        await fs.mkdir(documentsPath, { recursive: true });
        
        for (const docFile of documentChunk) {
            const fileName = path.basename(docFile);
            const dstPath = path.join(documentsPath, fileName);
            await fs.copyFile(docFile, dstPath);
        }
        
        console.log(`  ✓ Copied ${documentChunk.length} documents`);
        
        // Create package manifest
        await this.createManifest(packagePath, chunkId, documentChunk);
        
        // Create README for team members
        await this.createPackageReadme(packagePath, chunkId, documentChunk);
        
        return packagePath;
    }

    async copyDirectory(src, dest) {
        await fs.mkdir(dest, { recursive: true });
        const files = await fs.readdir(src);
        
        for (const file of files) {
            const srcPath = path.join(src, file);
            const destPath = path.join(dest, file);
            const stats = await fs.stat(srcPath);
            
            if (stats.isDirectory()) {
                await this.copyDirectory(srcPath, destPath);
            } else {
                await fs.copyFile(srcPath, destPath);
            }
        }
    }

    async createManifest(packagePath, chunkId, documentChunk) {
        const manifest = {
            package_info: {
                id: chunkId,
                name: `docu-package-${chunkId.toString().padStart(3, '0')}`,
                created: new Date().toISOString(),
                total_packages: this.numSplits,
                document_count: documentChunk.length
            },
            html_files: this.htmlFiles,
            documents: documentChunk.map(doc => path.basename(doc)),
            instructions: {
                "1": "Open ai_docu.html in your browser",
                "2": "Load documents from the 'documents' folder", 
                "3": "Select your preferred AI model",
                "4": "Click 'AI Analyze' to process your assigned documents",
                "5": "Export metadata when analysis is complete",
                "6": "Share the exported JSON file back to the project lead"
            }
        };
        
        const manifestPath = path.join(packagePath, 'package-manifest.json');
        await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2), 'utf8');
        console.log(`  ✓ Created package manifest`);
    }

    async createPackageReadme(packagePath, chunkId, documentChunk) {
        const readmeContent = `# AI Docu Analysis Work Package

📦 **Package:** docu-package-${chunkId.toString().padStart(3, '0')}  
📄 **Documents to analyze:** ${documentChunk.length}  
📅 **Created:** ${new Date().toLocaleString()}

## 🚀 Quick Start

### 1. Open the AI Docu App
Open the HTML file in your web browser:
- \`ai_docu.html\` - AI-powered document analyzer with multiple AI models

### 2. Load Documents
- Click **"📁 Select Documents"** and choose files from the \`documents/\` folder
- Or click **"📂 Select Folder"** and select the entire \`documents/\` folder
- You should see ${documentChunk.length} documents loaded

### 3. Choose AI Model and Analyze
- Select your preferred AI model from the dropdown:
  - **Sentence-BERT**: Fast text embeddings and similarity
  - **DistilBERT**: Document classification and categorization  
  - **Universal Encoder**: Advanced semantic understanding
- Click the **AI Analyze** button 🧠
- Wait for analysis to complete (progress bar will show status)
- All documents will get AI-generated keywords, summaries, and classifications

### 4. Export Results
- Click **"💾 Export Metadata"** button
- This saves a \`.json\` file with all analysis results
- The filename will be based on your selected model: \`ai-docu-sentencebert-metadata.json\`, \`ai-docu-distilbert-metadata.json\`, or \`ai-docu-universal-metadata.json\`

### 5. Send Back to Team Lead
- **Compress this entire folder** (including the new metadata file):
  \`\`\`bash
  # Easy way:
  cd ..
  tar -czf docu-package-${chunkId.toString().padStart(3, '0')}-completed.tar.gz docu-package-${chunkId.toString().padStart(3, '0')}/
  \`\`\`
- **Send the compressed file** back to your team lead
- Team lead will merge all results using the join tool

## 📝 Tips

- **Edit summaries**: Click on any document summary to edit it manually
- **Search**: Use the AI search feature to find specific documents
- **Grid layout**: Adjust how many documents per row (1-4)
- **Model comparison**: Try different AI models to compare results
- **File info**: Toggle the "Show file info" checkbox to see document details

## 🔍 File Structure

\`\`\`
docu-package-${chunkId.toString().padStart(3, '0')}/
├── README.md                              # This file
├── ai_docu.html                           # AI Docu App
├── docs/                                  # Documentation assets  
├── documents/                             # Your ${documentChunk.length} documents to analyze
├── package-manifest.json                 # Package info
└── [exported-metadata].json              # Your analysis results (after export)
\`\`\`

## 📄 Document Types Supported

- **Text Files**: .txt, .rtf, .md
- **PDF Documents**: .pdf (with text extraction)
- **Word Documents**: .docx (with content conversion)

## ❓ Questions?

If you run into issues:
1. Make sure you're using a modern web browser (Chrome, Firefox, Safari, Edge)
2. Check the browser console for any error messages
3. Try a different AI model if one isn't working
4. Contact your team lead for help

**Happy document analyzing! 📄🚀**
`;
        
        const readmePath = path.join(packagePath, 'README.md');
        await fs.writeFile(readmePath, readmeContent, 'utf8');
        console.log(`  ✓ Created README.md for team members`);
    }

    async compressPackage(packagePath) {
        const archiveName = `${path.basename(packagePath)}.zip`;
        const archivePath = path.join(path.dirname(packagePath), archiveName);
        
        return new Promise((resolve, reject) => {
            const output = createWriteStream(archivePath);
            const archive = archiver('zip', { zlib: { level: 9 } });
            
            output.on('close', () => {
                console.log(`  ✓ Created ${archiveName} (${archive.pointer()} bytes)`);
                resolve(archivePath);
            });
            
            archive.on('error', (err) => {
                reject(err);
            });
            
            archive.pipe(output);
            archive.directory(packagePath, path.basename(packagePath));
            archive.finalize();
        });
    }

    async split() {
        console.log(`🔍 Analyzing source folder: ${this.sourceFolder}`);
        
        // Get all document files
        const documentFiles = await this.getDocumentFiles();
        if (documentFiles.length === 0) {
            throw new Error(`No document files found in ${this.sourceFolder}`);
        }
        
        console.log(`📄 Found ${documentFiles.length} document files`);
        
        // Split into chunks
        const chunks = this.splitDocuments(documentFiles);
        const actualSplits = chunks.length;
        
        if (actualSplits !== this.numSplits) {
            console.log(`⚠️  Created ${actualSplits} packages instead of ${this.numSplits} (insufficient documents)`);
        }
        
        console.log(`📦 Creating ${actualSplits} work packages in: ${this.outputFolder}`);
        
        // Create output directory
        await fs.mkdir(this.outputFolder, { recursive: true });
        
        // Create each work package
        const createdPackages = [];
        for (let i = 0; i < chunks.length; i++) {
            console.log(`\n📦 Creating package ${i+1}/${actualSplits}:`);
            const packagePath = await this.createWorkPackage(i+1, chunks[i]);
            createdPackages.push(packagePath);
            console.log(`   Package: ${path.basename(packagePath)} (${chunks[i].length} documents)`);
        }
        
        return createdPackages;
    }

    async compressPackages(packages) {
        const compressedFiles = [];
        
        console.log(`\n🗜️  Compressing ${packages.length} packages...`);
        
        for (const packagePath of packages) {
            try {
                const archivePath = await this.compressPackage(packagePath);
                compressedFiles.push(archivePath);
            } catch (error) {
                console.log(`   ❌ Error compressing ${path.basename(packagePath)}: ${error.message}`);
            }
        }
        
        return compressedFiles;
    }
}

// CLI setup
program
    .name('split-work')
    .description('📄 AI Docu App - Document Splitter Tool')
    .version('1.0.0')
    .requiredOption('-s, --source <folder>', 'Source folder containing documents to split')
    .requiredOption('-n, --num-splits <number>', 'Number of work packages to create', parseInt)
    .option('-o, --output <folder>', 'Output folder for work packages (default: ./split/)')
    .option('-c, --compress', 'Automatically compress each package as .zip', true)
    .action(async (options) => {
        try {
            if (options.numSplits < 1) {
                throw new Error('Number of splits must be at least 1');
            }
            
            if (options.numSplits > 100) {
                throw new Error('Number of splits cannot exceed 100 (too many packages)');
            }
            
            const outputFolder = options.output || path.join(__dirname, 'split');
            
            console.log('📄 AI Docu App - Document Splitter Tool');
            console.log('='.repeat(45));
            
            // Initialize splitter
            const splitter = new DocumentSplitter(options.source, outputFolder, options.numSplits);
            
            // Perform the split
            const packages = await splitter.split();
            
            // Compress packages if requested
            let compressedFiles = [];
            if (options.compress) {
                compressedFiles = await splitter.compressPackages(packages);
            }
            
            console.log(`\n✅ Successfully created ${packages.length} work packages!`);
            if (compressedFiles.length > 0) {
                console.log(`🗜️  Compressed ${compressedFiles.length} packages!`);
            }
            console.log(`📁 Output location: ${outputFolder}`);
            
            // Show summary
            console.log(`\n📋 Package Summary:`);
            for (let i = 0; i < packages.length; i++) {
                const manifestPath = path.join(packages[i], 'package-manifest.json');
                try {
                    const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
                    const documentCount = manifest.package_info.document_count;
                    console.log(`   ${path.basename(packages[i])}: ${documentCount} documents`);
                } catch (error) {
                    console.log(`   ${path.basename(packages[i])}: unknown document count`);
                }
            }
            
            console.log(`\n🚀 Next Steps:`);
            if (options.compress) {
                console.log(`1. Share .zip files with team members`);
                console.log(`2. Team members extract and analyze their assigned documents`);
                console.log(`3. Team members send back results`);
                console.log(`4. Team lead uses join-work.js to merge results`);
            } else {
                console.log(`1. Compress packages manually or run with -c flag`);
                console.log(`2. Share packages with team members`);
                console.log(`3. Team lead uses join-work.js to merge results`);
            }
            
        } catch (error) {
            console.error(`❌ Error: ${error.message}`);
            process.exit(1);
        }
    });

program.parse();