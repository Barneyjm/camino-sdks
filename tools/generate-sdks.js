#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const OPENAPI_SPEC = path.join(__dirname, '..', 'openapi', 'camino-openapi.json');
const OUTPUT_DIR = path.join(__dirname, '..', 'generated');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function generatePythonSDK() {
  console.log('Generating Python SDK...');
  const outputPath = path.join(OUTPUT_DIR, 'python');
  ensureDir(outputPath);
  
  try {
    execSync(`npx @openapitools/openapi-generator-cli generate \
      -i "${OPENAPI_SPEC}" \
      -g python \
      -o "${outputPath}" \
      --additional-properties=packageName=camino_ai,packageVersion=0.1.0,projectName=camino-ai-sdk`, 
      { stdio: 'inherit' }
    );
    console.log('✅ Python SDK generated successfully');
  } catch (error) {
    console.error('❌ Failed to generate Python SDK:', error.message);
  }
}

function generateJavaScriptSDK() {
  console.log('Generating JavaScript SDK...');
  const outputPath = path.join(OUTPUT_DIR, 'javascript');
  ensureDir(outputPath);
  
  try {
    execSync(`npx @openapitools/openapi-generator-cli generate \
      -i "${OPENAPI_SPEC}" \
      -g typescript-node \
      -o "${outputPath}" \
      --additional-properties=npmName=@camino-ai/sdk,npmVersion=0.1.0,supportsES6=true`, 
      { stdio: 'inherit' }
    );
    console.log('✅ JavaScript SDK generated successfully');
  } catch (error) {
    console.error('❌ Failed to generate JavaScript SDK:', error.message);
  }
}

function main() {
  console.log('🚀 Generating Camino AI SDKs...');
  
  if (!fs.existsSync(OPENAPI_SPEC)) {
    console.error(`❌ OpenAPI spec not found at: ${OPENAPI_SPEC}`);
    process.exit(1);
  }
  
  ensureDir(OUTPUT_DIR);
  
  generatePythonSDK();
  generateJavaScriptSDK();
  
  console.log('✨ SDK generation complete!');
}

if (require.main === module) {
  main();
}

module.exports = { generatePythonSDK, generateJavaScriptSDK };