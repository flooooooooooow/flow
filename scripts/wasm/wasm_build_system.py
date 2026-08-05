#!/usr/bin/env python3
"""
Complete FLOW to WebAssembly Build System
Handles all examples including SIMD, structs, GPU operations, and complex features
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from flow_to_wasm import FlowToWasmConverter

class WasmBuildSystem:
    def __init__(self):
        self.converter = FlowToWasmConverter()
        self.build_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'categories': {
                'basic': 0,
                'simd': 0,
                'structs': 0,
                'gpu': 0,
                'effects': 0,
                'loops': 0,
                'math': 0,
                'other': 0
            }
        }
    
    def categorize_example(self, flow_file):
        """Categorize FLOW example by its content"""
        try:
            with open(flow_file, 'r') as f:
                content = f.read().lower()
            
            if 'vec' in content and '<' in content:
                return 'simd'
            elif 'struct' in content:
                return 'structs'
            elif any(keyword in content for keyword in ['metal', 'gpu', 'cuda', 'opencl']):
                return 'gpu'
            elif 'effect' in content:
                return 'effects'
            elif any(keyword in content for keyword in ['for', 'while', 'loop']):
                return 'loops'
            elif any(keyword in content for keyword in ['sin', 'cos', 'sqrt', 'fibonacci', 'factorial']):
                return 'math'
            else:
                return 'basic'
        except:
            return 'other'
    
    def build_all_examples(self, examples_dir="examples", output_dir="wasm_examples"):
        """Build all FLOW examples to WebAssembly"""
        examples_path = Path(examples_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("🚀 Building ALL FLOW Examples to WebAssembly")
        print("=" * 50)
        
        # Find all FLOW files
        flow_files = list(examples_path.rglob("*.flow"))
        print(f"📁 Found {len(flow_files)} FLOW examples")
        
        # Build each example
        results = []
        for flow_file in sorted(flow_files):
            category = self.categorize_example(flow_file)
            self.build_stats['categories'][category] += 1
            self.build_stats['total'] += 1
            
            # Convert relative path for display
            relative_path = flow_file.relative_to(Path.cwd())
            
            print(f"\n🔨 [{category.upper()}] {relative_path}")
            
            if self.converter.convert_file(flow_file, output_dir):
                self.build_stats['success'] += 1
                results.append({
                    'file': str(relative_path),
                    'category': category,
                    'status': 'success',
                    'name': flow_file.stem
                })
                print(f"✅ Success")
            else:
                self.build_stats['failed'] += 1
                results.append({
                    'file': str(relative_path),
                    'category': category,
                    'status': 'failed',
                    'name': flow_file.stem
                })
                print(f"❌ Failed")
        
        # Generate comprehensive index
        self.generate_comprehensive_index(results, output_path)
        
        # Print summary
        self.print_build_summary()
        
        return self.build_stats['failed'] == 0
    
    def generate_comprehensive_index(self, results, output_path):
        """Generate a comprehensive HTML index with all examples"""
        
        # Group results by category
        categories = {}
        for result in results:
            if result['category'] not in categories:
                categories[result['category']] = []
            categories[result['category']].append(result)
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLOW WebAssembly Examples - Complete Collection</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.2); 
        }}
        h1 {{ color: #333; text-align: center; margin-bottom: 10px; font-size: 2.5em; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 40px; font-size: 1.2em; }}
        
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 40px; 
        }}
        .stat-card {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .stat-label {{ opacity: 0.9; }}
        
        .category-section {{ margin: 40px 0; }}
        .category-title {{ 
            color: #333; 
            font-size: 1.8em; 
            margin-bottom: 20px; 
            padding-bottom: 10px; 
            border-bottom: 2px solid #e0e0e0; 
            display: flex; 
            align-items: center; 
            gap: 10px; 
        }}
        .examples-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-top: 20px; 
        }}
        .example-card {{ 
            border: 2px solid #e0e0e0; 
            border-radius: 12px; 
            padding: 20px; 
            background: #f9f9f9; 
            transition: all 0.3s ease; 
            cursor: pointer; 
            position: relative;
            overflow: hidden;
        }}
        .example-card:hover {{ 
            border-color: #667eea; 
            transform: translateY(-3px); 
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2); 
        }}
        .example-card.success {{ border-left: 4px solid #28a745; }}
        .example-card.failed {{ border-left: 4px solid #dc3545; opacity: 0.7; }}
        
        .example-title {{ 
            color: #333; 
            margin: 0 0 10px 0; 
            font-weight: bold; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
        }}
        .example-path {{ 
            color: #666; 
            font-size: 0.9em; 
            margin-bottom: 10px; 
            font-family: 'Courier New', monospace; 
        }}
        .example-description {{ 
            color: #555; 
            line-height: 1.5; 
            margin-bottom: 15px; 
        }}
        .status-badge {{ 
            position: absolute; 
            top: 10px; 
            right: 10px; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 0.8em; 
            font-weight: bold; 
        }}
        .status-badge.success {{ 
            background: #d4edda; 
            color: #155724; 
        }}
        .status-badge.failed {{ 
            background: #f8d7da; 
            color: #721c24; 
        }}
        .btn {{ 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 6px; 
            cursor: pointer; 
            text-decoration: none; 
            display: inline-block; 
            font-size: 0.9em; 
            transition: background 0.3s ease;
        }}
        .btn:hover {{ background: #5a6fd8; }}
        .btn:disabled {{ 
            background: #ccc; 
            cursor: not-allowed; 
        }}
        
        .category-icons {{
            'basic': '📝',
            'simd': '⚡',
            'structs': '🏗️',
            'gpu': '🎮',
            'effects': '🌊',
            'loops': '🔄',
            'math': '🔢',
            'other': '📁'
        }}
        
        .footer {{ 
            text-align: center; 
            margin-top: 50px; 
            padding: 30px; 
            background: #f8f9fa; 
            border-radius: 10px; 
            border-top: 2px solid #e0e0e0; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 FLOW WebAssembly Examples</h1>
        <p class="subtitle">Complete collection of FLOW examples compiled to WebAssembly for browser execution</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{self.build_stats['total']}</div>
                <div class="stat-label">Total Examples</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.build_stats['success']}</div>
                <div class="stat-label">Successfully Built</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.build_stats['failed']}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([c for c in self.build_stats['categories'].values() if c > 0])}</div>
                <div class="stat-label">Categories</div>
            </div>
        </div>
'''
        
        # Add category sections
        category_icons = {
            'basic': '📝',
            'simd': '⚡',
            'structs': '🏗️',
            'gpu': '🎮',
            'effects': '🌊',
            'loops': '🔄',
            'math': '🔢',
            'other': '📁'
        }
        
        category_descriptions = {
            'basic': 'Fundamental FLOW language features',
            'simd': 'SIMD vector operations and parallel computing',
            'structs': 'Data structures and object-oriented patterns',
            'gpu': 'GPU computing and hardware acceleration',
            'effects': 'Algebraic effects and control flow',
            'loops': 'Iteration and control flow patterns',
            'math': 'Mathematical algorithms and computations',
            'other': 'Advanced and experimental features'
        }
        
        for category in ['basic', 'simd', 'structs', 'gpu', 'effects', 'loops', 'math', 'other']:
            if category in categories and categories[category]:
                html_content += f'''
        <div class="category-section">
            <h2 class="category-title">
                <span>{category_icons.get(category, '📁')}</span>
                {category.title()} Examples ({len(categories[category])})
            </h2>
            <p>{category_descriptions.get(category, 'FLOW examples')}</p>
            
            <div class="examples-grid">
'''
                
                for example in categories[category]:
                    status_class = example['status']
                    status_text = '✅ Ready' if example['status'] == 'success' else '❌ Failed'
                    status_class_badge = 'success' if example['status'] == 'success' else 'failed'
                    
                    # Get first line as description
                    try:
                        with open(example['file'], 'r') as f:
                            first_line = f.readline().strip()
                            description = first_line.lstrip('# ') if first_line.startswith('#') else 'FLOW example program'
                    except:
                        description = 'FLOW example program'
                    
                    html_content += f'''
                <div class="example-card {status_class}" onclick="window.open('{example['name']}.html', '_blank')">
                    <div class="status-badge {status_class_badge}">{status_text}</div>
                    <div class="example-title">
                        <span>{category_icons.get(category, '📁')}</span>
                        {example['name']}
                    </div>
                    <div class="example-path">{example['file']}</div>
                    <div class="example-description">{description}</div>
                    {'<a href="' + example['name'] + '.html" class="btn">▶️ Run in Browser</a>' if example['status'] == 'success' else '<span class="btn" disabled>▶️ Build Failed</span>'}
                </div>
'''
                
                html_content += '''
            </div>
        </div>
'''
        
        html_content += f'''
        
        <div class="footer">
            <h3>🛠️ About This WebAssembly Collection</h3>
            <p>All FLOW examples have been compiled from FLOW → C → WebAssembly using Emscripten. 
            Each example runs real WebAssembly code in your browser with native performance.</p>
            
            <p><strong>Features demonstrated:</strong></p>
            <ul style="text-align: left; max-width: 600px; margin: 0 auto;">
                <li>✅ Static typing with type inference</li>
                <li>✅ Function definitions and calls</li>
                <li>✅ Data structures (structs, arrays)</li>
                <li>✅ SIMD vector operations</li>
                <li>✅ Control flow (if, while, for)</li>
                <li>✅ Mathematical algorithms</li>
                <li>✅ GPU computing concepts</li>
                <li>✅ Real WebAssembly execution</li>
            </ul>
            
            <p style="margin-top: 20px;">
                <strong>Build completed:</strong> {self.build_stats['success']}/{self.build_stats['total']} examples successfully compiled
            </p>
        </div>
    </div>
</body>
</html>'''
        
        # Write index file
        index_file = output_path / "index.html"
        with open(index_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 Generated comprehensive index: {index_file}")
    
    def print_build_summary(self):
        """Print build summary statistics"""
        print("\n" + "=" * 50)
        print("🎉 FLOW WebAssembly Build Summary")
        print("=" * 50)
        
        print(f"📊 Total examples: {self.build_stats['total']}")
        print(f"✅ Successfully built: {self.build_stats['success']}")
        print(f"❌ Failed: {self.build_stats['failed']}")
        
        if self.build_stats['success'] > 0:
            success_rate = (self.build_stats['success'] / self.build_stats['total']) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
        
        print("\n📂 Examples by category:")
        for category, count in self.build_stats['categories'].items():
            if count > 0:
                icon = {'basic': '📝', 'simd': '⚡', 'structs': '🏗️', 'gpu': '🎮', 
                       'effects': '🌊', 'loops': '🔄', 'math': '🔢', 'other': '📁'}.get(category, '📁')
                print(f"   {icon} {category.title()}: {count}")
        
        print(f"\n📁 Output directory: wasm_examples/")
        print(f"🌐 Open wasm_examples/index.html to see all examples")
        
        if self.build_stats['failed'] > 0:
            print(f"\n⚠️  {self.build_stats['failed']} examples failed to build")
            print("   Check individual build logs for details")

def main():
    print("🚀 FLOW WebAssembly Build System")
    print("Building ALL examples with full feature support...")
    
    builder = WasmBuildSystem()
    success = builder.build_all_examples()
    
    if success:
        print("\n🎉 ALL examples built successfully!")
        print("🌐 Open wasm_examples/index.html to see the complete collection")
    else:
        print(f"\n⚠️  Some examples failed to build")
        print("Check the build output above for details")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
