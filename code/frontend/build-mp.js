const { build } = require('vite')
const path = require('path')

async function buildMiniProgram() {
  try {
    console.log('[build] Starting UniApp mini-program build...')
    
    const result = await build({
      root: __dirname,
      mode: 'production',
      build: {
        outDir: 'dist/build/mp-weixin',
        emptyOutDir: true,
      },
    })
    
    console.log('[build] ✅ Build complete!')
    console.log('[build] Output: dist/build/mp-weixin/')
  } catch (err) {
    console.error('[build] ❌ Build failed:', err.message)
    process.exit(1)
  }
}

buildMiniProgram()
