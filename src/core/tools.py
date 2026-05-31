from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
import matplotlib.pyplot as plt
import io
import base64

repl = PythonREPL()

@tool
def code_interpreter(user_query: str) -> str:
    """Run Python code. Returns plots as images in chat."""
    try:
        from langchain_groq import ChatGroq
        from src.config import get_settings
        settings = get_settings()
        
        llm = ChatGroq(model=settings.llm_model, temperature=0.0, groq_api_key=settings.groq_api_key)

        code_prompt = f"""Write clean Python code for this request. Only return the code.

Request: {user_query}

- Use matplotlib for plots
- Always use plt.show() at the end
- Make plots look good"""

        generated_code = llm.invoke(code_prompt).content.strip()

        # Clean code
        if "```" in generated_code:
            generated_code = generated_code.split("```")[1].strip()
            if generated_code.startswith("python"):
                generated_code = generated_code[6:].strip()

        print("Generated Code:\n", generated_code)

        # Execute
        if "plt." in generated_code.lower():
            buf = io.BytesIO()
            exec(generated_code, {"plt": plt})
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            # Return as pure markdown image
            return f"![Plot](data:image/png;base64,{img_base64})"
        else:
            result = repl.run(generated_code)
            return str(result)

    except Exception as e:
        return f"Error: {str(e)}"