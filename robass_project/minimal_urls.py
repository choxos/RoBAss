from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home_view(request):
    html = """
    <html>
    <head>
        <title>RoBAss - Risk of Bias Assessment Tool</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .hero { background: #007bff; color: white; padding: 60px 20px; text-align: center; margin-bottom: 40px; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>🩺 RoBAss</h1>
            <h2>Risk of Bias Assessment Tool</h2>
            <p>Comprehensive tool for health research assessments</p>
        </div>
        
        <div class="card">
            <h3>✅ Deployment Successful!</h3>
            <p>Your Django application is running on Railway.</p>
            <p><strong>Database:</strong> Connected to PostgreSQL</p>
            <p><strong>Status:</strong> Ready for development</p>
        </div>
        
        <div class="card">
            <h3>🔧 Next Steps:</h3>
            <ul>
                <li>Access the <a href="/admin/" class="btn">Admin Panel</a> to set up assessment tools</li>
                <li>The full RoBAss interface will be available after setup</li>
                <li>This is a minimal working version to ensure deployment works</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>🚀 Features Coming:</h3>
            <ul>
                <li>RoB 2.0 for randomized trials</li>
                <li>ROBINS-I/E for observational studies</li>
                <li>AMSTAR-2 and ROBIS for systematic reviews</li>
                <li>Beautiful visualizations and CSV exports</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
]
