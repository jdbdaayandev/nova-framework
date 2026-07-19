import html
import traceback
from engine.Routing.router import HttpError
from engine.Http.response import Response
from engine.Support.config import config  # Upgraded from engine.Support.env

class ErrorHandler:
    
    @classmethod
    def handle_exception(cls, exception: Exception) -> Response:
        """Handles Python exceptions and HttpErrors based on the application configuration."""
        # Check if the master app debug toggle is active
        app_debug = config('app.debug', False)
        
        if isinstance(exception, HttpError):
            return cls.render_error_page(
                status_code=exception.status_code, 
                message=getattr(exception, 'message', 'Not Found')
            )
        
        # Log stack trace to console for the terminal runner
        traceback.print_exc()
        
        # Extract exception details
        exception_name = type(exception).__name__
        exception_message = str(exception)
        
        # Dev context classification engine
        detailed_msg = f"{exception_name}: {exception_message}"
        if "has no attribute" in exception_message:
            detailed_msg = f"Missing Function Error — {detailed_msg}"
        elif "not found" in exception_message.lower() or "module" in exception_message.lower():
            detailed_msg = f"Missing Controller Error — {detailed_msg}"
            
        exception_trace = traceback.format_exc()
        
        # Secure the application if debug mode is explicitly turned off
        if not app_debug:
            return cls.render_error_page(500, "Internal Server Error")
        
        # Fully verbose tracking UI for development mode
        return cls.render_error_page(500, detailed_msg, exception_trace)

    @classmethod
    def handle_error_response(cls, response: Response) -> Response:
        """Intercepts manual 404/403/500 Responses from the router and styles them."""
        status_code = getattr(response, 'status_code', getattr(response, 'status', 200))
        
        if status_code >= 400:
            messages = {403: "Forbidden", 404: "Page Not Found", 405: "Method Not Allowed", 500: "Server Error"}
            return cls.render_error_page(status_code, messages.get(status_code, "Error"))
            
        return response

    @staticmethod
    def render_error_page(status_code: int, message: str, exception_trace: str = "") -> Response:
        """Generates a contextual error page matching the clean look of the welcome index."""
        
        # Read parameters safely from the centralized application configuration repository
        is_debug = config('app.debug', False)
        app_env = config('app.env', 'production').upper()
        
        # Dynamic theme shifting elements
        badge_text = "Development Mode" if is_debug else "System Error"
        badge_style = "background-color: #fee2e2; color: #b91c1c;" if is_debug else "background-color: #e0e7ff; color: #3776AB;"
        
        if is_debug:
            description = "Nova Framework caught a runtime exception during the request lifecycle. Fix the structural implementation below."
        else:
            description = "We encountered an unexpected issue handling your request. The engineering team has been notified."

        # Render traceback ONLY if we are in debug mode
        traceback_html = ""
        if is_debug and exception_trace:
            traceback_html = f"""
            <div class="traceback-wrapper">
                <div class="traceback-header">
                    <div class="window-buttons">
                        <span style="background-color: #ef4444;"></span>
                        <span style="background-color: #eab308;"></span>
                        <span style="background-color: #22c55e;"></span>
                    </div>
                    <div class="window-title">Exception Stack Trace</div>
                </div>
                <div class="traceback-body">
                    <pre><code>{html.escape(exception_trace)}</code></pre>
                </div>
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{status_code} — {message if is_debug else 'Error'}</title>
            <style>
                :root {{
                    --bg-color: #f8fafc;
                    --text-main: #0f172a;
                    --text-muted: #64748b;
                    --accent: #3776AB;
                    --card-bg: #ffffff;
                    --border: #e2e8f0;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: var(--bg-color);
                    color: var(--text-main);
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    -webkit-font-smoothing: antialiased;
                    padding: 3rem 1.5rem;
                    box-sizing: border-box;
                }}

                .container {{
                    text-align: center;
                    max-width: 800px;
                    width: 100%;
                }}

                .badge {{
                    {badge_style}
                    padding: 0.4rem 0.9rem;
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    display: inline-block;
                    margin-bottom: 2rem;
                    line-height: 1;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                }}

                .error-heading {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 1.5rem;
                    margin-bottom: 1.5rem;
                    flex-wrap: wrap;
                }}

                .status-code {{
                    font-size: 4.5rem;
                    font-weight: 800;
                    letter-spacing: -0.04em;
                    line-height: 1;
                    color: var(--text-main);
                }}

                .divider {{
                    width: 1px;
                    height: 3.5rem;
                    background-color: var(--border);
                }}

                @media (max-width: 600px) {{
                    .divider {{ display: none; }}
                    .error-heading {{ flex-direction: column; gap: 0.5rem; }}
                }}

                .message {{
                    font-size: 1.35rem;
                    font-weight: 500;
                    color: #b91c1c;
                    letter-spacing: -0.02em;
                    text-align: left;
                    max-width: 550px;
                }}
                
                .message.prod {{
                    color: var(--text-muted);
                    text-align: center;
                }}

                .description {{
                    font-size: 1rem;
                    color: var(--text-muted);
                    max-width: 580px;
                    margin: 0 auto 2.5rem auto;
                    line-height: 1.6;
                }}

                .links {{
                    display: flex;
                    gap: 1.5rem;
                    justify-content: center;
                    margin-bottom: 3rem;
                }}

                .links a {{
                    text-decoration: none;
                    color: var(--text-muted);
                    font-weight: 500;
                    font-size: 0.9rem;
                    padding: 0.5rem 1rem;
                    border: 1px solid var(--border);
                    border-radius: 6px;
                    background-color: var(--card-bg);
                    transition: all 0.2s ease;
                }}

                .links a:hover {{
                    color: var(--accent);
                    border-color: var(--accent);
                }}

                .traceback-wrapper {{
                    background: var(--card-bg);
                    border: 1px solid var(--border);
                    border-radius: 10px;
                    text-align: left;
                    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04);
                    overflow: hidden;
                    margin-top: 2rem;
                }}

                .traceback-header {{
                    background-color: #fafafa;
                    border-bottom: 1px solid var(--border);
                    padding: 0.75rem 1.25rem;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }}

                .window-buttons {{
                    display: flex;
                    gap: 0.4rem;
                }}

                .window-buttons span {{
                    width: 9px;
                    height: 9px;
                    border-radius: 50%;
                    display: inline-block;
                }}

                .window-title {{
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    color: var(--text-muted);
                }}

                .traceback-body {{
                    padding: 1.5rem;
                    background-color: #ffffff;
                    max-height: 450px;
                    overflow-y: auto;
                }}

                pre {{
                    margin: 0;
                }}

                code {{
                    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                    color: #334155;
                    font-size: 0.875rem;
                    line-height: 1.6;
                    white-space: pre-wrap;
                }}

                footer {{
                    margin-top: 4rem;
                    font-size: 0.8rem;
                    color: var(--text-muted);
                    letter-spacing: 0.05em;
                }}
                
                footer code {{
                    background: var(--border);
                    padding: 0.15rem 0.35rem;
                    border-radius: 4px;
                    color: var(--text-main);
                    display: inline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="badge">{badge_text}</div>
                
                <div class="error-heading">
                    <div class="status-code">{status_code}</div>
                    <div class="divider"></div>
                    <div class="message {'prod' if not is_debug else ''}">{message}</div>
                </div>

                <p class="description">
                    {description}
                </p>
                
                <div class="links">
                    <a href="/">Return Home</a>
                    <a href="https://github.com" target="_blank">Documentation</a>
                </div>

                {traceback_html}

                <footer>
                    Nova Framework &nbsp;|&nbsp; Environment: <code>{app_env}</code>
                </footer>
            </div>
        </body>
        </html>
        """

        return Response(html_content, status=status_code, headers={'Content-Type': 'text/html; charset=utf-8'})