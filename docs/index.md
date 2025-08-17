# ScraperV4 Documentation Hub

Welcome to the ScraperV4 documentation - your comprehensive guide to mastering enterprise-grade web scraping. This documentation follows the **Diátaxis framework**, organizing information by user intent and learning needs.

## What is Diátaxis?

Diátaxis is a systematic approach to technical documentation that recognizes four distinct user needs:

- **Learning** - when you want to acquire new skills
- **Goals** - when you want to solve a specific problem  
- **Understanding** - when you want to clarify concepts
- **Information** - when you need to look up facts

Our documentation is organized around these four quadrants to help you find exactly what you need, when you need it.

```
          LEARNING-ORIENTED        |        GOAL-ORIENTED
     ─────────────────────────────────────────────────────────
       📚 TUTORIALS                |        🎯 HOW-TO GUIDES
       • Step-by-step lessons      |        • Problem-solving
       • Learning by doing         |        • Real-world tasks
       • Guided practice           |        • Specific solutions
     ─────────────────────────────────────────────────────────
       📖 EXPLANATIONS             |        📋 REFERENCE
       • Background & context      |        • Technical specs
       • Design decisions          |        • API documentation
       • Conceptual clarity        |        • Complete coverage
     ─────────────────────────────────────────────────────────
          UNDERSTANDING-ORIENTED   |        INFORMATION-ORIENTED
```

## Quick Navigation

### 🚀 Getting Started
**New to ScraperV4?** Start here for your first scraping job.

- [Installation & Setup](tutorials/installation.md) - Get ScraperV4 running in 5 minutes
- [Your First Scrape](tutorials/first-scrape.md) - Build and run your first template
- [Web Interface Tour](tutorials/web-interface.md) - Navigate the user interface

### 🎯 Solve Specific Problems
**Need to accomplish a particular task?** Jump to the solution.

#### Core Operations
- [Create Advanced Templates](how-to/create-templates.md)
- [Configure Proxy Rotation](how-to/setup-proxies.md)
- [Handle Anti-Bot Protection](how-to/bypass-detection.md)
- [Export Data in Different Formats](how-to/export-data.md)

#### Advanced Techniques
- [Scrape JavaScript-Heavy Sites](how-to/javascript-sites.md)
- [Handle Large-Scale Jobs](how-to/scale-operations.md)
- [Implement Custom Stealth Profiles](how-to/custom-stealth.md)
- [Monitor Job Performance](how-to/monitor-jobs.md)

### 📖 Understand the System
**Want to understand how things work?** Explore the concepts.

- [Architecture Overview](explanations/architecture.md) - System design and components
- [Template Engine](explanations/template-engine.md) - How CSS selectors become data
- [Proxy Management](explanations/proxy-system.md) - Intelligent rotation strategies
- [Anti-Detection Techniques](explanations/stealth-features.md) - Staying under the radar
- [Data Processing Pipeline](explanations/data-pipeline.md) - From raw HTML to clean exports

### 📋 Look Up Technical Details
**Need precise technical information?** Find it in our reference.

- [Complete API Reference](reference/api/) - All endpoints and parameters
- [Configuration Options](reference/configuration.md) - Every setting explained
- [Template Schema](reference/template-schema.md) - Template structure specification
- [Error Codes & Troubleshooting](reference/error-codes.md) - Debugging guide
- [CLI Commands](reference/cli-commands.md) - Command-line interface

## Where Should I Start?

### 👋 I'm completely new to web scraping
Start with [Installation & Setup](tutorials/installation.md), then work through [Your First Scrape](tutorials/first-scrape.md). These tutorials will teach you fundamental concepts through hands-on practice.

### 🔧 I know scraping but I'm new to ScraperV4  
Jump to [Web Interface Tour](tutorials/web-interface.md) to understand our specific tools, then explore [How-To Guides](how-to/) for solutions to common tasks.

### 🚀 I need to solve a specific problem right now
Head straight to our [How-To Guides](how-to/) section. Each guide is designed to solve a specific real-world problem with step-by-step instructions.

### 🤔 I want to understand the underlying concepts
Browse our [Explanations](explanations/) section to understand why ScraperV4 works the way it does. Great for making informed architectural decisions.

### 📚 I need to look up specific technical details
Use our comprehensive [Reference](reference/) section. All APIs, configurations, and technical specifications are documented here.

### 🆘 Something's not working
Check [Error Codes & Troubleshooting](reference/error-codes.md) or search the [FAQ](reference/faq.md) for common issues and solutions.

## ScraperV4 at a Glance

ScraperV4 is an enterprise-grade web scraping framework featuring:

**🎯 Core Features**
- Template-based scraping with CSS selectors and XPath
- Asynchronous job execution with real-time progress monitoring  
- Multiple export formats (JSON, CSV, Excel) with advanced formatting
- Intelligent proxy rotation with performance tracking
- Advanced anti-bot detection and bypass capabilities

**🛡️ Stealth & Security**
- Dynamic user agent rotation and header randomization
- Real-time protection system detection (Cloudflare, Sucuri, reCAPTCHA)
- Sophisticated retry mechanisms with circuit breakers
- Browser fingerprint randomization

**💾 Data Management**
- Persistent job storage with comprehensive metadata
- Advanced data processing with validation rules
- Template testing and optimization tools
- Export customization and batch operations

**🌐 Modern Interface**
- Clean, responsive web UI built with HTML/CSS/JavaScript
- Real-time updates via Eel communication framework
- RESTful API for programmatic access
- Visual template creation and management

## Documentation Structure

```
docs/
├── index.md (you are here)           # This navigation hub
├── tutorials/                        # Learning-oriented
│   ├── installation.md              # Getting started
│   ├── first-scrape.md              # Your first template
│   ├── web-interface.md             # UI walkthrough
│   └── advanced-features.md         # Complex scenarios
├── how-to/                          # Goal-oriented
│   ├── create-templates.md          # Template creation
│   ├── setup-proxies.md             # Proxy configuration
│   ├── bypass-detection.md          # Anti-bot handling
│   ├── export-data.md               # Data export options
│   ├── javascript-sites.md          # JS-heavy sites
│   ├── scale-operations.md          # Large-scale jobs
│   ├── custom-stealth.md            # Stealth profiles
│   └── monitor-jobs.md              # Performance monitoring
├── explanations/                    # Understanding-oriented
│   ├── architecture.md              # System design
│   ├── template-engine.md           # Template concepts
│   ├── proxy-system.md              # Proxy management
│   ├── stealth-features.md          # Anti-detection
│   └── data-pipeline.md             # Processing pipeline
├── reference/                       # Information-oriented
│   ├── api/                         # API documentation
│   │   ├── scraping.md              # Scraping endpoints
│   │   ├── templates.md             # Template endpoints
│   │   ├── data.md                  # Data endpoints
│   │   └── monitoring.md            # Status endpoints
│   ├── configuration.md             # Config reference
│   ├── template-schema.md           # Template structure
│   ├── error-codes.md               # Error reference
│   ├── cli-commands.md              # CLI reference
│   └── faq.md                       # Common questions
└── README.md                        # Technical overview
```

## Contributing to Documentation

Found an error or want to improve our docs? We welcome contributions:

1. **Small fixes**: Edit files directly and submit a pull request
2. **New content**: Follow our [Documentation Guidelines](CONTRIBUTING.md#documentation)
3. **Structure changes**: Discuss in an issue first to align with Diátaxis principles

## Need Help?

- **Documentation Issues**: Open an issue in our GitHub repository
- **Feature Requests**: Use our issue templates for enhancement requests  
- **Community Support**: Join discussions in GitHub Discussions
- **Security Issues**: See our [Security Policy](SECURITY.md) for responsible disclosure

---

**Next Steps**: Choose your path from the navigation options above, or start with [Installation & Setup](tutorials/installation.md) if you're new to ScraperV4.

*This documentation is built with the Diátaxis framework - learn more at [diataxis.fr](https://diataxis.fr)*