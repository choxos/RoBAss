# RoBAss - Risk of Bias Assessment Tool

A comprehensive web application for conducting risk of bias assessments in health research. Built with Django and designed for systematic reviewers and health researchers.

## Features

- **Multiple Assessment Tools**: Support for RoB 2.0, ROBINS-I, ROBINS-E, AMSTAR-2, and ROBIS
- **Beautiful Visualizations**: Generate publication-ready plots (traffic light plots, summary charts, weighted visualizations)
- **Data Export**: Export assessments as CSV files for analysis
- **User Management**: Register accounts or use guest access
- **Project Organization**: Create projects, organize studies, track progress
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Supported Risk of Bias Tools

### Interventional Studies
- **RoB 2.0** - Parallel randomized trials
- **RoB 2.0** - Cluster randomized trials  
- **RoB 2.0** - Crossover randomized trials

### Observational Studies
- **ROBINS-I** - Risk of bias in non-randomized studies of interventions
- **ROBINS-E** - Risk of bias in non-randomized studies of exposures

### Systematic Reviews
- **AMSTAR-2** - A MeaSurement Tool to Assess systematic Reviews
- **ROBIS** - Risk of Bias in Systematic reviews

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RoBAss.git
   cd RoBAss
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

### Railway Deployment

This application is ready for deployment on Railway:

1. **Fork this repository** to your GitHub account

2. **Connect to Railway**:
   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository

3. **Add a PostgreSQL database**:
   - In your Railway project dashboard
   - Click "New" → "Database" → "Add PostgreSQL"

4. **Set environment variables**:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-domain.railway.app,localhost,127.0.0.1
   ```

5. **Deploy**: Railway will automatically deploy your application

6. **Run initial setup** (in Railway console):
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Visualization**: matplotlib, seaborn, pandas
- **Deployment**: Railway, Gunicorn, WhiteNoise
- **Authentication**: Django Auth + Custom User Profiles

## Project Structure

```
RoBAss/
├── accounts/              # User authentication and profiles
├── assessments/           # Core assessment functionality
│   ├── models.py         # Database models
│   ├── views.py          # Application logic
│   ├── forms.py          # Form definitions
│   ├── utils.py          # Visualization and export utilities
│   └── admin.py          # Admin interface
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── RoBTools/            # Risk of bias assessment guidance documents
├── requirements.txt     # Python dependencies
├── railway.json         # Railway deployment configuration
└── manage.py           # Django management script
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use RoBAss in your research, please cite:

```
RoBAss: A Comprehensive Risk of Bias Assessment Tool for Health Research
[Add proper citation when published]
```

## Support

For questions or support:
- Create an issue on GitHub
- Contact: [your-email@example.com]

## Acknowledgments

- Built following Cochrane Risk of Bias guidance
- Inspired by the excellent [robvis](https://github.com/mcguinlu/robvis) R package
- Thanks to the systematic review and evidence synthesis community

---

**Note**: This tool is designed to assist with risk of bias assessment but does not replace the need for trained reviewers and careful consideration of each study's context.
