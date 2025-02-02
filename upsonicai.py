from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from upsonic import Agent, Task, ObjectResponse
from upsonic.client.tools import Search

app = FastAPI()

# Upsonic AI Agent
class Company(ObjectResponse):
    any_customer: bool

class CompanyInput(BaseModel):
    company_url: str

product_manager = Agent("Product Manager", model="azure/gpt-4o")

@app.post("/analyze-company/")
async def analyze_company(input_data: CompanyInput):
    task = Task("Check the website and analyze", response_format=Company, context=[input_data.company_url], tools=[Search])
    result = product_manager.do(task)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to analyze company website.")
    return result

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Company Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin: 50px; }
            input, button { padding: 10px; margin: 10px; width: 300px; }
            button { background: blue; color: white; border: none; cursor: pointer; }
            #results { margin-top: 20px; text-align: left; }
        </style>
    </head>
    <body>
        <h1>Company Analysis</h1>
        <input type="text" id="company_url" placeholder="Enter company website">
        <button onclick="analyzeCompany()">Analyze</button>
        <div id="results"></div>
        <script>
            async function analyzeCompany() {
                const company_url = document.getElementById('company_url').value;
                const response = await fetch('/analyze-company/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ company_url })
                });
                const data = await response.json();
                document.getElementById('results').innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            }
        </script>
    </body>
    </html>
    """
