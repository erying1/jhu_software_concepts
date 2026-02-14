# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 3: Database Queries Assignment Experiment 
#
# module_4/src/app/__init__.py
#
from flask import Flask, app

# Now import routes
#from .routes import bp as routes_bp


def create_app(test_config=None): 
    app = Flask(__name__) 

    app.jinja_env.globals['pct'] = lambda v: f"{float(v):.2f}" if v is not None else "N/A"
    app.jinja_env.globals['na'] = lambda v: "N/A" if v is None else v

    # Load default configuration FIRST 
    app.config.from_mapping( 
        SECRET_KEY="dev", 
        TESTING=False, 
        DATABASE_URL=None, 
        ) 
    
    # Apply test_config SECOND 
    if test_config is not None: 
        app.config.update(test_config) 
        
    # Pytest override LAST 
    import os 
    if os.getenv("PYTEST_CURRENT_TEST"): 
        app.config["TESTING"] = True 
        
    # Register filters 
    @app.template_filter('pct')
    def pct_filter(value): 
        try: 
            return f"{float(value):.2f}" 
        except Exception: 
            return "0.00" 
        
    @app.template_filter("na")
    def na_filter(value): 
        if value is None: 
            return "N/A" 
        if isinstance(value, str) and value.strip() == "": 
            return "N/A" 
        return value 
    
    # Import blueprint *inside* function so pytest sees it 
    from .routes import bp 
    app.register_blueprint(bp) 
    
    app.BUSY = False 
    return app

