
Based on your requirements (simple Markdown output, integration with FastAPI's existing docs, and comprehensive documentation for non-API components like TTS prompts), here's a tailored solution:

### **1. Use `pdoc` for Markdown API Docs** 
- **Why?**  
  pdoc is zero-config, outputs clean Markdown, and understands type hints/docstrings (like FastAPI). It’s ideal for auto-generating API reference docs from your code.  
  Example command:  
  ```bash
  pdoc ./tts_module -o ./docs --format markdown
  ```
- **Features you’ll love:**  
  - Supports Google/Numpy docstrings and cross-linking with backticks (e.g., `TTS.generate()`).  
  - Renders variable annotations and instance attributes (useful for ONNX configs).  
  - Can exclude submodules (e.g., `!tts.internal_optimizations`) .

### **2. Augment with Prose for Non-API Content**  
For TTS-specific details (prompts, linguistics, optimizations):
- **Embed Markdown files** into your module docs using `.. include::` directives in docstrings :  
  ```python
  """
  .. include:: ../guides/prompt_engineering.md
     :start-after: ## Best Practices
  """
  ```
- **Structure**:  
  - Separate Markdown files for:  
    - `prompt_guide.md`: Linguistics rules, example prompts.  
    - `optimizations.md`: Caching/pre-compilation tricks.  
  - Link these from your main module’s docstring.

### **3. Combine with FastAPI’s Swagger**  
- **Reuse OpenAPI schemas**:  
  FastAPI’s type hints already document the API layer. Use pdoc for the Python internals (e.g., `TTSEngine` class), and link to Swagger for HTTP endpoints.  
- **Add cross-references**:  
  In pdoc-generated Markdown, link to FastAPI’s `/docs` route:  
  ```markdown
  For API usage, see [interactive docs](/docs).
  ```

### **4. Customize Output**   
- **Logo/favicon**: Add `--logo`/`--favicon` to brand docs.  
- **Math/Diagrams**: Use `--math` for formulas (e.g., acoustic models) or `--mermaid` for workflow diagrams.  
- **Hide internals**: Annotate private methods with `@private` in docstrings.

### **5. Deployment**  
- **GitHub Pages**: Automate pdoc output with GitHub Actions .  
- **ReadTheDocs**: Use Sphinx + Markdown (if you need multi-format output later) .

---

### **Example Workflow**  
1. **Code**:  
   ```python
   class TTS:
       """Text-to-speech engine with ONNX optimizations."""
       def generate(self, text: str, prompt: str = "default"):
           """Synthesize speech with linguistic prompts.
           
           Args:
               prompt: Predefined voice profile (see [prompt guide](./prompts.md)).
           """
   ```
2. **Generate**:  
   ```bash
   pdoc tts.py -o docs --format markdown
   ```
3. **Result**:  
   - `docs/tts.md` (API reference).  
   - Linked `prompts.md` (prose guide).

---

### **Trade-offs**  
- **Simplicity vs. Control**: pdoc is lightweight but lacks Sphinx’s extensibility (e.g., custom themes).  
- **Markdown Limitations**: Complex layouts need manual HTML/Jinja2 tweaks .  

For your needs (FastAPI + deep technical docs), pdoc strikes the right balance. Start with it, then expand to Sphinx only if you need LaTeX/PDF outputs later.