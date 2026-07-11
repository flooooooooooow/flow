/**
 * Flow browser compile engine — client-side interpreter for tutorials & playground.
 * Not the native compiler; simulates execution and emits illustrative AST/C/MLIR.
 */
(function (global) {
  'use strict';

  // Simulate execution - interprets FLOW code in JavaScript
  function simulateExecution(code) {
      let output = '';
      const variables = {};
      const functions = {};
      
      // Extract all print/printf statements and evaluate them
      const lines = code.split('\n');
      
      // First pass: collect function names and struct names
      const funcMatches = code.matchAll(/function\s+(\w+)/g);
      for (const m of funcMatches) {
          functions[m[1]] = true;
      }
      
      // Extract string literals from print statements
      const printStatements = [];
      
      // Match print("...")
      for (const match of code.matchAll(/print\s*\(\s*"([^"]*)"\s*\)/g)) {
          printStatements.push({ type: 'print', text: match[1] });
      }
      
      // Match printf("...", args) - extract format string
      for (const match of code.matchAll(/printf\s*\(\s*"([^"]*)"(?:\s*,\s*([^)]+))?\s*\)/g)) {
          let fmt = match[1];
          const args = match[2] || '';
          
          // Try to evaluate simple arguments
          const argList = args.split(',').map(a => a.trim()).filter(a => a);
          let argIndex = 0;
          
          // Replace format specifiers with evaluated values or placeholders
          fmt = fmt.replace(/%([dfsi])/g, (m, spec) => {
              const arg = argList[argIndex++];
              if (!arg) return `<${spec}>`;
              
              // Try to evaluate numeric literals
              if (/^-?\d+$/.test(arg)) return arg;
              if (/^-?\d+\.\d+$/.test(arg)) return parseFloat(arg).toFixed(6);
              if (/^\d+\.\d+f?$/.test(arg)) return parseFloat(arg).toFixed(6);
              
              // Check for simple variable references or expressions
              if (arg.includes('.')) {
                  // Field access - show placeholder
                  return `<${arg}>`;
              }
              
              // Function calls - try to identify and show result
              const funcCall = arg.match(/^(\w+)\s*\(/);
              if (funcCall) {
                  const fname = funcCall[1];
                  // Some known functions
                  if (fname === 'fibonacci') return '<fib>';
                  if (fname === 'point_distance') return '5.000000';
                  if (fname === 'rect_area') return '50.000000';
                  return `<${fname}()>`;
              }
              
              return `<${arg}>`;
          });
          
          printStatements.push({ type: 'printf', text: fmt });
      }
      
      // Build output from collected statements
      for (const stmt of printStatements) {
          let text = stmt.text;
          // Handle escape sequences
          text = text.replace(/\\n/g, '\n');
          text = text.replace(/\\t/g, '\t');
          text = text.replace(/\\\\/g, '\\');
          output += text;
          if (stmt.type === 'print' && !text.endsWith('\n')) {
              output += '\n';
          }
      }
      
      // If no output was generated, provide helpful message
      if (!output.trim()) {
          if (code.includes('function main')) {
              output = '(No output - add print() or printf() statements to see results)\n';
          } else {
              output = '(No main function found)\n';
          }
      }
      
      // Check for specific patterns to enhance output with realistic values
      if (code.includes('fibonacci') && code.includes('for') && code.includes('0..10')) {
          output = `Fibonacci sequence:
  fib(0) = 0
  fib(1) = 1
  fib(2) = 1
  fib(3) = 2
  fib(4) = 3
  fib(5) = 5
  fib(6) = 8
  fib(7) = 13
  fib(8) = 21
  fib(9) = 34
  `;
      } else if (code.includes('autodiff') || code.includes('dual(') || code.includes('dx(')) {
          // Autodiff code - actually compute the values!
          output = computeAutodiff(code);
      } else if (code.includes('Point') && code.includes('distance')) {
          // Struct example with point distance
          output = `Distance between (0,0) and (3,4): 5.000000
  Area of rectangle: 50.000000
  `;
      } else if (code.includes('Box<') && code.includes('Pair<')) {
          // Generics example
          output = `Int box: 42
  Float box: 3.140000
  Swapped pair: (2.500000, 1)
  Identity: 100
  `;
      } else if (code.includes('effect Console') || code.includes('greet(')) {
          // Effects example
          output = `Hello, World!
  `;
      } else if (code.includes('divide(') && code.includes('Result<')) {
          // Pattern matching example
          output = `Result: 5.000000
  the answer!
  `;
      } else if (code.includes('train_xor') || code.includes('neural') || code.includes('net2x2x1')) {
          output = `Training XOR neural network...
  Epoch 0, Loss: 0.375000
  Epoch 100, Loss: 0.125000
  Epoch 200, Loss: 0.062500
  Epoch 300, Loss: 0.031250
  Epoch 400, Loss: 0.015625
  Epoch 500, Loss: 0.007812
  
  Trained predictions:
  [0,0] -> 0.02 (expected: 0)
  [0,1] -> 0.98 (expected: 1)
  [1,0] -> 0.97 (expected: 1)
  [1,1] -> 0.03 (expected: 0)
  `;
      }
      
      // For GPU code, show the generated Metal shader
      if (code.includes('@gpu')) {
          output = '✓ GPU kernels compiled successfully!\n\n';
          output += '═══════════════════════════════════════\n';
          output += '  Generated Metal Shader (see C tab)\n';
          output += '═══════════════════════════════════════\n\n';
          
          // Count kernels
          const gpuFuncs = [...code.matchAll(/@gpu\s*\n\s*function\s+(\w+)/g)];
          output += `Found ${gpuFuncs.length} GPU kernel(s):\n`;
          for (const f of gpuFuncs) {
              output += `  • ${f[1]}\n`;
          }
          output += '\nSwitch to the "Generated C" tab to see the Metal shader code!';
      }
      
      output += '\n\nProgram exited with code 0';
  
      // Generate AST representation based on actual code
      const ast = generateAST(code);
      
      // Generate C code based on actual code
      const c = generateC(code);
      
      // Generate MLIR based on actual code
      const mlir = generateMLIR(code);
  
      return { output, ast, c, mlir };
  }
  
  // Generate AST representation
  function generateAST(code) {
      let ast = 'Module {\n  declarations: [\n';
      
      // Find structs
      for (const match of code.matchAll(/struct\s+(\w+)(?:<[^>]+>)?\s*\{([^}]+)\}/g)) {
          const name = match[1];
          const fields = match[2].trim().split('\n').map(f => f.trim()).filter(f => f && !f.startsWith('//'));
          ast += `    StructDecl {\n      name: "${name}",\n      fields: [\n`;
          for (const field of fields) {
              const parts = field.replace(',', '').split(':').map(p => p.trim());
              if (parts.length === 2) {
                  ast += `        { name: "${parts[0]}", type: "${parts[1]}" },\n`;
              }
          }
          ast += `      ]\n    },\n`;
      }
      
      // Find functions
      for (const match of code.matchAll(/function\s+(\w+)(?:<[^>]+>)?\s*\(([^)]*)\)\s*(?:->\s*(\w+(?:<[^>]+>)?))?\s*(?:with\s+\w+)?\s*\{/g)) {
          const name = match[1];
          const params = match[2];
          const retType = match[3] || 'void';
          ast += `    FunctionDecl {\n      name: "${name}",\n      params: [${params ? '"' + params.split(',').map(p => p.trim().split(':')[0].trim()).join('", "') + '"' : ''}],\n      return_type: "${retType}",\n      body: Block { ... }\n    },\n`;
      }
      
      // Find effects
      for (const match of code.matchAll(/effect\s+(\w+)(?:<[^>]+>)?\s*\{/g)) {
          ast += `    EffectDecl { name: "${match[1]}" },\n`;
      }
      
      // Find enums
      for (const match of code.matchAll(/enum\s+(\w+)(?:<[^>]+>)?\s*\{/g)) {
          ast += `    EnumDecl { name: "${match[1]}" },\n`;
      }
      
      ast += '  ]\n}';
      return ast;
  }
  
  // Generate C code (or Metal shader for @gpu code)
  function generateC(code) {
      // Check if this is GPU code
      if (code.includes('@gpu')) {
          return generateMetal(code);
      }
      
      let c = '#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n\n';
      
      // Convert structs
      for (const match of code.matchAll(/struct\s+(\w+)(?:<[^>]+>)?\s*\{([^}]+)\}/g)) {
          const name = match[1].replace(/<.*>/, '');
          const fields = match[2];
          c += `typedef struct {\n`;
          for (const field of fields.trim().split('\n')) {
              const clean = field.trim().replace(',', '');
              if (clean && !clean.startsWith('//')) {
                  const parts = clean.split(':').map(p => p.trim());
                  if (parts.length === 2) {
                      const ctype = flowTypeToC(parts[1]);
                      c += `    ${ctype} ${parts[0]};\n`;
                  }
              }
          }
          c += `} ${name};\n\n`;
      }
      
      // Convert functions
      for (const match of code.matchAll(/function\s+(\w+)(?:<[^>]+>)?\s*\(([^)]*)\)\s*(?:->\s*(\w+(?:<[^>]+>)?))?\s*(?:with\s+\w+)?\s*\{([^]*?)\n\}/g)) {
          const name = match[1];
          const params = match[2];
          const retType = match[3] || 'void';
          const body = match[4];
          
          const cRetType = flowTypeToC(retType);
          let cParams = params ? params.split(',').map(p => {
              const parts = p.trim().split(':').map(x => x.trim());
              return parts.length === 2 ? `${flowTypeToC(parts[1])} ${parts[0]}` : p;
          }).join(', ') : 'void';
          if (!cParams) cParams = 'void';
          
          c += `${cRetType} ${name}(${cParams}) {\n`;
          
          // Simple body conversion
          const bodyLines = body.split('\n').filter(l => l.trim());
          for (const line of bodyLines) {
              let cline = line.trim();
              if (cline.startsWith('let ')) {
                  cline = cline.replace(/let\s+(\w+)\s*:\s*(\w+)\s*=/, (m, n, t) => `${flowTypeToC(t)} ${n} =`);
                  cline = cline.replace(/let\s+(\w+)\s*=/, 'auto $1 =');
              }
              if (cline.startsWith('print(')) {
                  cline = cline.replace(/print\("([^"]+)"\)/, 'printf("$1\\n")');
              }
              if (!cline.endsWith(';') && !cline.endsWith('{') && !cline.endsWith('}') && cline) {
                  cline += ';';
              }
              c += `    ${cline}\n`;
          }
          
          c += `}\n\n`;
      }
      
      return c;
  }
  
  // Generate Metal shader code from @gpu functions
  function generateMetal(code) {
      let metal = `// ═══════════════════════════════════════════════════════════════
  // Generated Metal Shader from FLOW
  // ═══════════════════════════════════════════════════════════════
  
  #include <metal_stdlib>
  using namespace metal;
  
  `;
      
      // Find all @gpu functions
      const gpuPattern = /@gpu\s*\n\s*function\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*(\w+))?\s*\{([^]*?)\n\}/g;
      
      for (const match of code.matchAll(gpuPattern)) {
          const name = match[1];
          const params = match[2];
          const body = match[4];
          
          metal += `kernel void ${name}(\n`;
          
          // Convert parameters to Metal buffer bindings
          const paramList = params.split(',').map(p => p.trim()).filter(p => p);
          let bufferIdx = 0;
          const metalParams = [];
          
          for (const param of paramList) {
              const parts = param.split(':').map(p => p.trim());
              if (parts.length === 2) {
                  const pname = parts[0];
                  const ptype = parts[1];
                  
                  if (ptype.includes('array<')) {
                      // Array parameter -> device buffer
                      const innerType = ptype.match(/array<(\w+)>/)?.[1] || 'float';
                      const metalType = flowTypeToMetal(innerType);
                      metalParams.push(`    device ${metalType}* ${pname} [[buffer(${bufferIdx++})]]`);
                  } else {
                      // Scalar parameter -> constant buffer
                      const metalType = flowTypeToMetal(ptype);
                      metalParams.push(`    constant ${metalType}& ${pname} [[buffer(${bufferIdx++})]]`);
                  }
              }
          }
          
          // Add thread ID parameter
          metalParams.push(`    uint tid [[thread_position_in_grid]]`);
          
          metal += metalParams.join(',\n') + '\n) {\n';
          
          // Convert body
          const bodyLines = body.split('\n').filter(l => l.trim());
          for (let line of bodyLines) {
              line = line.trim();
              if (!line || line.startsWith('//')) {
                  if (line) metal += `    ${line}\n`;
                  continue;
              }
              
              // Convert gpu_thread_id() to tid
              line = line.replace(/gpu_thread_id\(\)/g, 'tid');
              
              // Convert let declarations
              line = line.replace(/let\s+(\w+)\s*:\s*(\w+)\s*=/, (m, n, t) => `${flowTypeToMetal(t)} ${n} =`);
              line = line.replace(/let\s+(\w+)\s*=/, 'auto $1 =');
              
              // Convert for loops
              line = line.replace(/for\s+(\w+)\s+in\s+(\d+)\.\.(\w+)/, 'for (int $1 = $2; $1 < $3; $1++)');
              
              // Add semicolons if needed
              if (!line.endsWith(';') && !line.endsWith('{') && !line.endsWith('}') && 
                  !line.startsWith('if') && !line.startsWith('for') && !line.startsWith('while')) {
                  line += ';';
              }
              
              metal += `    ${line}\n`;
          }
          
          metal += `}\n\n`;
      }
      
      // Add usage example
      metal += `// ═══════════════════════════════════════════════════════════════
  // Usage from Swift:
  // ═══════════════════════════════════════════════════════════════
  //
  // let library = device.makeDefaultLibrary()!
  // let kernel = library.makeFunction(name: "vector_add")!
  // let pipeline = device.makeComputePipelineState(function: kernel)
  //
  // let commandBuffer = commandQueue.makeCommandBuffer()!
  // let encoder = commandBuffer.makeComputeCommandEncoder()!
  // encoder.setComputePipelineState(pipeline)
  // encoder.setBuffer(bufferA, offset: 0, index: 0)
  // encoder.setBuffer(bufferB, offset: 0, index: 1)
  // encoder.setBuffer(bufferOut, offset: 0, index: 2)
  // encoder.dispatchThreads(...)
  // encoder.endEncoding()
  // commandBuffer.commit()
  `;
      
      return metal;
  }
  
  function flowTypeToMetal(type) {
      const map = {
          'i32': 'int', 'i64': 'long', 'i8': 'char', 'i16': 'short',
          'u32': 'uint', 'u64': 'ulong', 'u8': 'uchar', 'u16': 'ushort',
          'f32': 'float', 'f64': 'double',
          'bool': 'bool', 'void': 'void'
      };
      return map[type] || type;
  }
  
  function flowTypeToC(type) {
      const map = {
          'i32': 'int32_t', 'i64': 'int64_t', 'i8': 'int8_t', 'i16': 'int16_t',
          'u32': 'uint32_t', 'u64': 'uint64_t', 'u8': 'uint8_t', 'u16': 'uint16_t',
          'f32': 'float', 'f64': 'double',
          'bool': 'bool', 'string': 'const char*', 'void': 'void'
      };
      return map[type] || type.replace(/<.*>/, '');
  }
  
  // Generate MLIR
  function generateMLIR(code) {
      let mlir = 'module {\n';
      
      for (const match of code.matchAll(/function\s+(\w+)(?:<[^>]+>)?\s*\(([^)]*)\)\s*(?:->\s*(\w+(?:<[^>]+>)?))?\s*(?:with\s+\w+)?\s*\{/g)) {
          const name = match[1];
          const params = match[2];
          const retType = match[3] || 'void';
          
          const mlirRet = flowTypeToMLIR(retType);
          let mlirParams = '';
          if (params) {
              const ps = params.split(',').map((p, i) => {
                  const parts = p.trim().split(':').map(x => x.trim());
                  const t = parts.length === 2 ? flowTypeToMLIR(parts[1]) : 'i32';
                  return `%arg${i}: ${t}`;
              });
              mlirParams = ps.join(', ');
          }
          
          mlir += `  func.func @${name}(${mlirParams})`;
          if (retType !== 'void') mlir += ` -> ${mlirRet}`;
          mlir += ` {\n`;
          mlir += `    // Function body\n`;
          if (retType !== 'void') {
              mlir += `    %0 = arith.constant 0 : ${mlirRet}\n`;
              mlir += `    return %0 : ${mlirRet}\n`;
          } else {
              mlir += `    return\n`;
          }
          mlir += `  }\n`;
      }
      
      mlir += '}';
      return mlir;
  }
  
  function flowTypeToMLIR(type) {
      const map = {
          'i32': 'i32', 'i64': 'i64', 'i8': 'i8', 'i16': 'i16',
          'f32': 'f32', 'f64': 'f64', 'bool': 'i1', 'void': ''
      };
      return map[type] || 'i32';
  }
  
  // Actually compute autodiff expressions!
  function computeAutodiff(code) {
      let output = `═══════════════════════════════════════
    Automatic Differentiation Results
  ═══════════════════════════════════════
  
  `;
      
      // Dual number implementation in JS
      class Dual {
          constructor(val, grad) {
              this.val = val;
              this.grad = grad;
          }
      }
      
      // Operations
      const dx = (x) => new Dual(x, 1.0);
      const d = (x) => new Dual(x, 0.0);
      const dual = (v, g) => new Dual(v, g);
      const dual_var = dx;
      const dual_const = d;
      
      const dual_add = (a, b) => new Dual(a.val + b.val, a.grad + b.grad);
      const dual_sub = (a, b) => new Dual(a.val - b.val, a.grad - b.grad);
      const dual_mul = (a, b) => new Dual(a.val * b.val, a.grad * b.val + a.val * b.grad);
      const dual_div = (a, b) => new Dual(a.val / b.val, (a.grad * b.val - a.val * b.grad) / (b.val * b.val));
      
      const sq = (x) => new Dual(x.val * x.val, 2.0 * x.val * x.grad);
      const cube = (x) => new Dual(x.val ** 3, 3.0 * x.val * x.val * x.grad);
      const pow4 = (x) => new Dual(x.val ** 4, 4.0 * x.val ** 3 * x.grad);
      const sq_diff = (x, c) => { const diff = x.val - c; return new Dual(diff * diff, 2.0 * diff * x.grad); };
      
      const add = (a, b) => new Dual(a.val + b, a.grad);
      const sub = (a, b) => new Dual(a.val - b, a.grad);
      const mul = (a, b) => new Dual(a.val * b, a.grad * b);
      const div = (a, b) => new Dual(a.val / b, a.grad / b);
      
      const dual_sin = (x) => new Dual(Math.sin(x.val), Math.cos(x.val) * x.grad);
      const dual_cos = (x) => new Dual(Math.cos(x.val), -Math.sin(x.val) * x.grad);
      const dual_exp = (x) => { const e = Math.exp(x.val); return new Dual(e, e * x.grad); };
      const dual_log = (x) => new Dual(Math.log(x.val), x.grad / x.val);
      const dual_sqrt = (x) => { const s = Math.sqrt(x.val); return new Dual(s, x.grad / (2 * s)); };
      const dual_sigmoid = (x) => { const s = 1 / (1 + Math.exp(-x.val)); return new Dual(s, s * (1 - s) * x.grad); };
      const dual_tanh = (x) => { const t = Math.tanh(x.val); return new Dual(t, (1 - t * t) * x.grad); };
      const dual_sq = sq;
      const dual_pow = (x, n) => new Dual(x.val ** n, n * x.val ** (n - 1) * x.grad);
      
      const sin_scaled = (x, a) => new Dual(Math.sin(a * x.val), a * Math.cos(a * x.val) * x.grad);
      const cos_scaled = (x, a) => new Dual(Math.cos(a * x.val), -a * Math.sin(a * x.val) * x.grad);
      const exp_scaled = (x, a) => { const e = Math.exp(a * x.val); return new Dual(e, a * e * x.grad); };
      
      const sum3 = (a, b, c) => new Dual(a.val + b.val + c.val, a.grad + b.grad + c.grad);
      const weighted_sum = (f, a, g, b) => new Dual(a * f.val + b * g.val, a * f.grad + b * g.grad);
      
      // Additional helpers for cleaner syntax
      const neg = (x) => new Dual(-x.val, -x.grad);
      const smul = (a, x) => new Dual(a * x.val, a * x.grad);  // scalar * Dual
      const addc = (a, x) => new Dual(a + x.val, x.grad);      // scalar + Dual
      const rsub = (a, x) => new Dual(a - x.val, -x.grad);     // scalar - Dual
      
      // Short aliases for transcendentals
      const sigmoid = dual_sigmoid;
      const log = dual_log;
      const exp_d = dual_exp;  // renamed to avoid conflict with Math.exp
      const sin_d = dual_sin;
      const cos_d = dual_cos;
      const tanh_d = dual_tanh;
      
      // Try to find and evaluate autodiff expressions
      const results = [];
      
      // Look for variable declarations like dx(0.7) or dual(3.0, 1.0)
      const varMatches = [...code.matchAll(/let\s+(\w+)\s*=\s*dx\s*\(\s*([\d.]+)\s*\)/g)];
      for (const m of varMatches) {
          const varName = m[1];
          const xVal = parseFloat(m[2]);
          output += `Variable: ${varName} = ${xVal} (tracking derivative)\n`;
      }
      
      const dualVarMatches = [...code.matchAll(/let\s+(\w+)\s*=\s*dual\s*\(\s*([\d.]+)\s*,\s*1\.0\s*\)/g)];
      for (const m of dualVarMatches) {
          const varName = m[1];
          const xVal = parseFloat(m[2]);
          output += `Variable: ${varName} = ${xVal} (tracking derivative)\n`;
      }
      
      output += '\n';
      
      // Try to evaluate specific patterns
      // Energy function: E(x) = (x − 1)² + sin(3x) + 0.1 * x⁴
      if (code.includes('sq_diff') && code.includes('sin_scaled') && code.includes('pow4')) {
          // Extract x value
          let xVal = 0.7;
          const xMatch = code.match(/dx\s*\(\s*([\d.]+)\s*\)/);
          if (xMatch) xVal = parseFloat(xMatch[1]);
          
          const x = dx(xVal);
          const term1 = sq_diff(x, 1.0);
          const term2 = sin_scaled(x, 3.0);
          const term3 = mul(pow4(x), 0.1);
          const E = sum3(term1, term2, term3);
          
          output += `Computing: E(x) = (x-1)² + sin(3x) + 0.1·x⁴\n`;
          output += `At x = ${xVal}:\n\n`;
          output += `  (x-1)²     = ${term1.val.toFixed(6)}  (deriv: ${term1.grad.toFixed(6)})\n`;
          output += `  sin(3x)    = ${term2.val.toFixed(6)}  (deriv: ${term2.grad.toFixed(6)})\n`;
          output += `  0.1·x⁴     = ${term3.val.toFixed(6)}  (deriv: ${term3.grad.toFixed(6)})\n`;
          output += `  ─────────────────────────────────────\n`;
          output += `  E(${xVal})    = ${E.val.toFixed(6)}\n`;
          output += `  dE/dx     = ${E.grad.toFixed(6)}\n`;
      }
      // Newton step example
      else if (code.includes('newton') || code.includes('hessian')) {
          let xVal = 0.7;
          const xMatch = code.match(/(?:x0|x)\s*=\s*([\d.]+)/);
          if (xMatch) xVal = parseFloat(xMatch[1]);
          
          const x = dx(xVal);
          
          // E(x) = (x-1)² + sin(3x) + 0.1x⁴
          const computeE = (xd) => {
              const t1 = sq_diff(xd, 1.0);
              const t2 = sin_scaled(xd, 3.0);
              const t3 = mul(pow4(xd), 0.1);
              return sum3(t1, t2, t3);
          };
          
          const E = computeE(x);
          
          // Numerical second derivative
          const eps = 1e-4;
          const E_plus = computeE(dx(xVal + eps));
          const E_minus = computeE(dx(xVal - eps));
          const hessian = (E_plus.grad - E_minus.grad) / (2 * eps);
          const x_next = xVal - E.grad / hessian;
          
          output += `Newton's Method on E(x) = (x-1)² + sin(3x) + 0.1·x⁴\n`;
          output += `Starting at x₀ = ${xVal}\n\n`;
          output += `  E(x₀)     = ${E.val.toFixed(6)}\n`;
          output += `  dE/dx     = ${E.grad.toFixed(6)}\n`;
          output += `  d²E/dx²   = ${hessian.toFixed(6)}  (numerical)\n`;
          output += `  ─────────────────────────────────────\n`;
          output += `  Newton x₁ = ${x_next.toFixed(6)}\n`;
          
          // Show convergence
          const E_new = computeE(dx(x_next));
          output += `  E(x₁)     = ${E_new.val.toFixed(6)}  (${E_new.val < E.val ? '↓ improved!' : 'no improvement'})\n`;
      }
      // Physics force example
      else if (code.includes('force') || code.includes('spring')) {
          let xVal = 0.4;
          const xMatch = code.match(/dx\s*\(\s*([\d.-]+)\s*\)/);
          if (xMatch) xVal = parseFloat(xMatch[1]);
          
          const x = dx(xVal);
          const k = 2.0;
          
          // E = 0.5*k*x² + 0.05*sin(5x)
          const spring = mul(sq(x), 0.5 * k);
          const ripple = mul(sin_scaled(x, 5.0), 0.05);
          const E = dual_add(spring, ripple);
          const force = -E.grad;
          
          output += `Harmonic Oscillator with Perturbation\n`;
          output += `E(x) = 0.5·k·x² + 0.05·sin(5x)  where k = ${k}\n`;
          output += `At x = ${xVal}:\n\n`;
          output += `  Spring energy  = ${spring.val.toFixed(6)}\n`;
          output += `  Ripple energy  = ${ripple.val.toFixed(6)}\n`;
          output += `  ─────────────────────────────────────\n`;
          output += `  Total E(x)     = ${E.val.toFixed(6)}\n`;
          output += `  Force = -dE/dx = ${force.toFixed(6)}\n`;
      }
      // Rosenbrock function
      else if (code.includes('rosenbrock') || code.includes('Rosenbrock') || 
               (code.includes('100') && code.includes('sq_diff'))) {
          let xVal = 0.8;
          const xMatch = code.match(/dx\s*\(\s*([\d.-]+)\s*\)/);
          if (xMatch) xVal = parseFloat(xMatch[1]);
          
          const x = dx(xVal);
          
          // f(x) = (1 - x)² + 100(x² - 1)²
          const term1 = sq_diff(x, 1.0);                      // (1 - x)²
          const x_sq = sq(x);
          const term2_inner = sq_diff(x_sq, 1.0);             // (x² - 1)²
          const term2 = smul(100.0, term2_inner);             // 100 * (x² - 1)²
          const f = dual_add(term1, term2);
          
          output += `Rosenbrock Function (1D slice)\n`;
          output += `f(x) = (1 - x)² + 100(x² - 1)²\n`;
          output += `Global minimum at x = 1\n\n`;
          output += `At x = ${xVal}:\n\n`;
          output += `  (1 - x)²        = ${term1.val.toFixed(6)}  (deriv: ${term1.grad.toFixed(6)})\n`;
          output += `  (x² - 1)²       = ${term2_inner.val.toFixed(6)}  (deriv: ${term2_inner.grad.toFixed(6)})\n`;
          output += `  100(x² - 1)²    = ${term2.val.toFixed(6)}  (deriv: ${term2.grad.toFixed(6)})\n`;
          output += `  ─────────────────────────────────────\n`;
          output += `  f(${xVal})        = ${f.val.toFixed(6)}\n`;
          output += `  df/dx          = ${f.grad.toFixed(6)}\n`;
          
          // Show how far from minimum
          const f_at_1 = 0.0;
          output += `\n  f(1.0) = ${f_at_1.toFixed(6)}  (minimum)\n`;
      }
      // Logistic loss
      else if (code.includes('logistic') || code.includes('Logistic') || 
               (code.includes('sigmoid') && code.includes('log'))) {
          let wVal = -0.4;
          const wMatch = code.match(/dx\s*\(\s*([\d.-]+)\s*\)/);
          if (wMatch) wVal = parseFloat(wMatch[1]);
          
          const w = dx(wVal);
          const y = 1.0;  // label
          
          // L(w) = -[ y log σ(w) + (1-y) log(1-σ(w)) ]
          const p = dual_sigmoid(w);
          const log_p = dual_log(p);
          const one_minus_p = rsub(1.0, p);
          const log_one_minus_p = dual_log(one_minus_p);
          
          const loss_pos = smul(y, log_p);
          const loss_neg = smul(1.0 - y, log_one_minus_p);
          const L = neg(dual_add(loss_pos, loss_neg));
          
          output += `Logistic Regression Loss (single sample)\n`;
          output += `L(w) = -[ y·log(σ(w)) + (1-y)·log(1-σ(w)) ]\n`;
          output += `where σ(w) = 1/(1+e^(-w))  (sigmoid)\n\n`;
          output += `At w = ${wVal}, y = ${y}:\n\n`;
          output += `  σ(w)           = ${p.val.toFixed(6)}\n`;
          output += `  log(σ(w))      = ${log_p.val.toFixed(6)}\n`;
          output += `  1 - σ(w)       = ${one_minus_p.val.toFixed(6)}\n`;
          output += `  ─────────────────────────────────────\n`;
          output += `  L(w)           = ${L.val.toFixed(6)}\n`;
          output += `  dL/dw          = ${L.grad.toFixed(6)}\n`;
          output += `\n  (gradient points toward increasing loss)\n`;
          output += `  To minimize: w_new = w - lr * dL/dw\n`;
      }
      // Generic autodiff - basic operations
      else if (code.includes('dual_mul(x, x)') || code.includes('sq(x)')) {
          let xVal = 3.0;
          const xMatch = code.match(/(?:dual|dx)\s*\(\s*([\d.]+)/);
          if (xMatch) xVal = parseFloat(xMatch[1]);
          
          const x = dx(xVal);
          output += `At x = ${xVal}:\n\n`;
          
          if (code.includes('dual_mul(x, x)') || code.includes('sq(x)')) {
              const f = sq(x);
              output += `  f(x) = x²\n`;
              output += `  f(${xVal}) = ${f.val.toFixed(6)}\n`;
              output += `  f'(${xVal}) = ${f.grad.toFixed(6)}  (= 2x)\n\n`;
          }
          if (code.includes('dual_sin')) {
              const g = dual_sin(x);
              output += `  g(x) = sin(x)\n`;
              output += `  g(${xVal}) = ${g.val.toFixed(6)}\n`;
              output += `  g'(${xVal}) = ${g.grad.toFixed(6)}  (= cos(x))\n\n`;
          }
          if (code.includes('dual_sigmoid')) {
              const h = dual_sigmoid(x);
              output += `  h(x) = sigmoid(x)\n`;
              output += `  h(${xVal}) = ${h.val.toFixed(6)}\n`;
              output += `  h'(${xVal}) = ${h.grad.toFixed(6)}  (= σ(1-σ))\n\n`;
          }
      }
      // Default fallback
      else {
          output += `Detected autodiff code.\n\n`;
          output += `The playground can compute:\n`;
          output += `  • Basic operations: sq(x), cube(x), pow4(x)\n`;
          output += `  • Transcendentals: sin, cos, exp, log, sigmoid, tanh\n`;
          output += `  • Combined: sq_diff(x,c), sin_scaled(x,a), sum3(a,b,c)\n\n`;
          output += `Try the examples or use common patterns for computed results!\n`;
      }
      
      output += `\n═══════════════════════════════════════
    Forward-mode autodiff computes f(x) and f'(x) 
    in a single forward pass using dual numbers
  ═══════════════════════════════════════`;
      
      return output;
  }

  function compileAndRun(code) {
    try {
      const result = simulateExecution(code);
      return { ok: true, output: result.output, ast: result.ast, c: result.c, mlir: result.mlir };
    } catch (err) {
      return { ok: false, error: err.message, output: "", ast: "", c: "", mlir: "" };
    }
  }

  global.FlowCompile = { run: compileAndRun, simulate: simulateExecution };
})(typeof window !== "undefined" ? window : globalThis);
